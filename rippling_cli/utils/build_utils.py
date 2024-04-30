import configparser
import os
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import asdict
from http import client
from typing import Optional

import click

from rippling_cli.config.config import get_app_config
from rippling_cli.constants import (
    APP_BUILD_MODULE,
    APP_FOLDER,
    PYPROJECT_TOML,
    RIPPLING_API,
)
from rippling_cli.core.api_client import APIClient
from rippling_cli.core.s3 import S3UploadFileCredentials
from rippling_cli.utils.loading_bar import start_circular_loading_bar, start_loading_bar, stop_loading_bar
from rippling_cli.utils.login_utils import get_api_client_with_role_company
from rippling_cli.utils.s3_utils import get_s3_upload_url_credentials
from rippling_cli.utils.validation_summary import Validation, ValidationSummary


def starter_package_already_extracted_on_current_directory():
    """
    Check if the starter package has already been extracted in the current working directory.
    :return:
    """
    cwd = os.getcwd()

    # Check if the 'manifest' file exists in the target directory
    app_dir_path = os.path.join(cwd, "app")
    if os.path.isdir(app_dir_path):
        # Check if the 'app' directory exists in the target directory
        manifest_dir_path = os.path.join(app_dir_path, "manifest.json")
        if os.path.isfile(manifest_dir_path):
            return True

    return False


def remove_existing_starter_package():
    """
    Remove the existing starter package from the current working directory along with the pyproject.toml, poetry.lock,
    .venv, and .idea files/directories.
    :return:
    """
    # Construct the path for the directory we want to remove
    cwd = os.getcwd()
    target_dir_path = os.path.join(cwd, "app")

    # Remove the directory with hyphens replaced by underscores and its contents
    if os.path.exists(target_dir_path):
        try:
            shutil.rmtree(target_dir_path)
        except Exception:
            pass

    # Remove the pyproject.toml, poetry.lock, .venv, and .idea files/directories
    files_to_remove = ["pyproject.toml", "poetry.lock", ".venv", ".idea"]
    for file_or_dir in files_to_remove:
        file_or_dir_path = os.path.join(os.getcwd(), file_or_dir)
        if os.path.exists(file_or_dir_path):
            try:
                if os.path.isfile(file_or_dir_path):
                    os.remove(file_or_dir_path)
                else:
                    shutil.rmtree(file_or_dir_path)
            except Exception:
                pass


def get_run_config_xml_content(project_name):
    """
    Generate the content for the .idea/runConfigurations/Flask.xml file.
    :param project_name:
    :return:
    """
    return f"""
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="Flask (flux_dev_tools.server.flask)" type="Python.FlaskServer"\
 nameIsGenerated="true">
    <module name="{project_name}" />
    <option name="target" value="flux_dev_tools.server.flask" />
    <option name="targetType" value="PYTHON" />
    <option name="INTERPRETER_OPTIONS" value="" />
    <option name="PARENT_ENVS" value="true" />
    <option name="SDK_HOME" value="$PROJECT_DIR$/.venv/bin/python" />
    <option name="WORKING_DIRECTORY" value="" />
    <option name="IS_MODULE_SDK" value="false" />
    <option name="ADD_CONTENT_ROOTS" value="true" />
    <option name="ADD_SOURCE_ROOTS" value="true" />
    <EXTENSION ID="PythonCoverageRunConfigurationExtension" runner="coverage.py" />
    <option name="launchJavascriptDebuger" value="false" />
    <method v="2" />
  </configuration>
</component>
"""


def get_pyproject_toml_content(project_name="my-project", authors="developer <developer@example.com>"):
    """
    Get the content for a pyproject.toml file with the given project name and authors.
    :param project_name:
    :param authors:
    :return:
    """
    return f"""
[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = ""
authors = ["{authors}"]

[tool.poetry.dependencies]
python = "^3.10"

[tool.poetry.dev-dependencies]
rippling-flux-sdk = "^0.20"
rippling-flux-dev-tools = "^0.1.16"
flask = "^3"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""


def create_pyproject_toml(project_name="my-project", authors="developer <developer@example.com>"):
    """
    Create a pyproject.toml file with the given project name and authors.
    :param project_name:
    :param authors:
    :return:
    """
    click.echo("Creating pyproject.toml file...")
    with open("pyproject.toml", "w") as toml_file:
        toml_file.write(get_pyproject_toml_content(project_name, authors))
    click.echo("pyproject.toml file created.")


def display_builds(builds):
    """
    Display the builds in the console.
    :param builds:
    :return:
    """

    for build in builds:
        click.echo(
            f"- {build.get('name')} {build.get('created_by', {}).get('fullName', '-')}  {build.get('status')} \
{build.get('id')}")


def get_dependencies_from_pyproject(pyproject_toml):
    """
    Read the non-dev dependencies from the pyproject.toml file.

    Args:
        pyproject_toml (str): Path to the pyproject.toml file.

    Returns:
        dict: A dictionary containing the non-dev dependencies.
    """
    config = configparser.ConfigParser()
    config.read(pyproject_toml)

    dependencies = {}
    if config.has_section('tool.poetry.dependencies'):
        for key, value in config.items('tool.poetry.dependencies'):
            if key == 'python':
                continue
            # Strip any leading/trailing quotes from the value
            value = value.strip('"\'')
            dependencies[key] = value

    return dependencies


def create_requirements_file(dependencies, requirements_file):
    """
    Create a requirements.txt file with the non-dev dependencies.

    Args:
        dependencies (dict): A dictionary containing the non-dev dependencies.
        requirements_file (str): Path to the requirements.txt file.
    """
    with open(requirements_file, 'w') as f:
        for dependency, constraint in dependencies.items():
            # Strip any leading/trailing quotes from the dependency
            dependency = dependency.strip('"\'')
            # Remove '^' operator if present in the constraint
            constraint = constraint.lstrip('^')
            if constraint.startswith('>='):
                version_str = f'{dependency}{constraint}'
            elif constraint.startswith('<'):
                version_str = f'{dependency},{constraint}'
            else:
                version_str = f'{dependency}=={constraint}'
            f.write(f'{version_str}\n')


def install_dependencies(requirements_file, target_dir):
    """
    Install the non-dev dependencies in the target directory.

    Args:
        requirements_file (str): Path to the requirements.txt file.
        target_dir (str): Path to the target directory.
    """
    # Command to install dependencies
    cmd = ['poetry', 'run', 'pip', 'install', '--target', target_dir, '-r', requirements_file]

    # Run the command and capture the output
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check if the command was successful
    if result.returncode != 0:
        click.echo(f"Error installing dependencies: {result.stderr}")


def create_zip_file(app_folder, target_dir, zip_filename):
    """
    Create a zip file containing the app folder and its dependencies.

    Args:
        app_folder (str): Path to the app folder.
        target_dir (str): Path to the target directory containing the dependencies.
        zip_filename (str): Name of the zip file to be created.
    """
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        # Add the app folder
        for root, dirs, files in os.walk(app_folder):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path)

        # Add the dependencies from the target directory
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, target_dir))


def upload_zip_file_to_s3(content_type, file_path: str, s3_upload_file_credentials: S3UploadFileCredentials):
    """
    Upload a zip file to S3.
    :param content_type:
    :param file_path:
    :param s3_upload_file_credentials:
    :return:
    """
    api_client = APIClient(base_url=s3_upload_file_credentials.url)
    with open(file_path, 'rb') as f:
        data = asdict(s3_upload_file_credentials)
        data.pop('url')
        for key in list(data.keys()):
            if '_' in key:
                data[key.replace('_', '-')] = data[key]
                del data[key]
        data.pop('s3-build-url')
        data['Content-Type'] = content_type
        files = {'file': f}
        response = api_client.post("/", files=files, data=data)
        return response.status_code == client.NO_CONTENT


def package_and_upload_app_with_dependencies(s3_upload_file_credentials: S3UploadFileCredentials):
    """
    Package the app folder with its non-dev dependencies into a zip file and upload it to S3.
    :param s3_upload_file_credentials: S3UploadFileCredentials
    :return:
    """
    # Get the non-dev dependencies from pyproject.toml
    dependencies = get_dependencies_from_pyproject(PYPROJECT_TOML)

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a temporary requirements.txt file
        requirements_file = os.path.join(temp_dir, 'requirements.txt')
        create_requirements_file(dependencies, requirements_file)

        # Install the non-dev dependencies in the temporary directory
        install_dependencies(requirements_file, temp_dir)

        # Clean up the temporary requirements.txt file
        if os.path.exists(requirements_file):
            os.remove(requirements_file)
        # Create a zip file containing the app folder and its dependencies
        zip_filename = temp_dir + 'app_with_dependencies.zip'
        create_zip_file(APP_FOLDER, temp_dir, zip_filename)

        # Upload the zip file to S3
        upload_zip_file_to_s3('application/zip', zip_filename, s3_upload_file_credentials)

    return True


def validate_bundle(app_name: str, build_s3_url: str, oauth_token: str):
    """
    Validate the app bundle using the Rippling API.
    :param app_name:
    :param build_s3_url:
    :param oauth_token:
    :return:
    """
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    data = {
        "app_name": app_name,
        "build_s3_url": build_s3_url
    }
    response = api_client.post('/apps/api/app_builds/validate', data=data)

    if response.status_code not in [client.BAD_REQUEST, client.OK]:
        return False, None, None

    response_json = response.json()
    # Convert the validations dictionary to a list of Validation objects
    validations = {
        name: Validation(name=name, **validation_data)
        for name, validation_data in response_json["validations"].items()
    }

    suggested_build_name = response_json.get("suggested_build_name", None)
    # Create a ValidationSummary instance and print the summary
    summary = ValidationSummary(validations)

    return response.status_code == client.OK, suggested_build_name, summary


def create_build(app_name: str, build_s3_url: str, name: str, oauth_token: str):
    """
    This function creates a build for the app.
    :param app_name:
    :param build_s3_url:
    :param name:
    :param oauth_token:
    :return:
    """
    api_client = get_api_client_with_role_company(oauth_token)
    data = {
        "app_name": app_name,
        "build_s3_url": build_s3_url,
        "name": name,
        "developer_notes": ""
    }
    response = api_client.post('/apps/api/app_builds/upload', data=data)
    response.raise_for_status()
    return response.status_code == client.CREATED


def deploy_build(app_name: str, build_id: str, oauth_token: str):
    """
    This function deploys the build to the app.
    :param app_name:
    :param build_id:
    :param oauth_token:
    :return:
    """
    api_client = get_api_client_with_role_company(oauth_token)
    data = {
        "app_name": app_name,
        "build_id": build_id,
    }
    response = api_client.post('/apps/api/app_builds/deploy', data=data)
    response.raise_for_status()
    return response.status_code == client.ACCEPTED


def package_and_validate_bundle(oauth_token: str):
    """
    gets the s3 upload credentials, packages the app with its dependencies and validates the bundle.

    :param oauth_token:
    :return:
    """
    # get the s3 upload credentials

    s3_upload_file_credentials: Optional[S3UploadFileCredentials] = get_s3_upload_url_credentials("application/zip",
                                                                                        APP_BUILD_MODULE
                                                                                        , oauth_token)
    if not s3_upload_file_credentials:
        click.echo("Failed to get the s3 upload credentials.")
        return None, None

    # package and upload the app with dependencies to s3
    click.echo(click.style('Packaging and Uploading', fg='yellow'))
    loading_bar = start_circular_loading_bar(length=0)
    upload_steps = package_and_upload_app_with_dependencies(s3_upload_file_credentials)
    stop_loading_bar(loading_bar)
    if not upload_steps:
        click.echo("Failed to upload the app.")
        return None, None

    click.echo("Bundle uploaded successfully.")

    # get the app config
    app_config = get_app_config()

    # validate the build
    click.echo(click.style('Validating app bundle...', fg='cyan'))
    loading_bar = start_loading_bar(length=20, label="Validating", char='#')
    validation_successful, suggested_build_name, summary = validate_bundle(app_config.get("name"),
                                                                           s3_upload_file_credentials.s3_build_url,
                                                                           oauth_token)
    stop_loading_bar(loading_bar)
    if summary:
        # print the validation summary
        summary.print_summary()

    if not validation_successful:
        click.echo("Validation failed for the app bundle.")
        return None, None

    return suggested_build_name, s3_upload_file_credentials
