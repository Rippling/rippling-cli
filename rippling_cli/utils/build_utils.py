import os
import shutil

import click


def starter_package_already_extracted_on_current_directory():
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
    return f"""
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="Flask (flux_dev_tools.server.flask)" type="Python.FlaskServer" \ 
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
    return f"""
[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = ""
authors = ["{authors}"]

[tool.poetry.dependencies]
python = "^3.10"
rippling-flux-sdk = "^0.16.40"
rippling-flux-dev-tools = "^0.1.12"
flask = "^2"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""


def create_pyproject_toml(project_name="my-project", authors="developer <developer@example.com>"):
    click.echo("Creating pyproject.toml file...")
    with open("pyproject.toml", "w") as toml_file:
        toml_file.write(get_pyproject_toml_content(project_name, authors))
    click.echo("pyproject.toml file created.")

