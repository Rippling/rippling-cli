import click

from rippling_cli.config.config import get_app_config
from rippling_cli.core.setup_project import setup_project
from rippling_cli.utils.api_utils import delete_data_by_id, get_data_by_id
from rippling_cli.utils.app_utils import get_starter_package_for_app
from rippling_cli.utils.build_utils import (
    create_build,
    deploy_build,
    display_builds,
    package_and_validate_bundle,
    remove_existing_starter_package,
    starter_package_already_extracted_on_current_directory,
)
from rippling_cli.utils.file_utils import download_file_using_url, extract_zip_to_current_cwd
from rippling_cli.utils.login_utils import ensure_logged_in, get_current_role_name_and_email
from rippling_cli.utils.pagination_utils import paginate_data


@click.group()
@click.pass_context
def build(ctx: click.Context):
    """
    Manage flux builds.

    This command group is the entry point for managing flux builds. It provides
    subcommands for various build-related operations, such as initializing a new
    project, listing all builds, downloading a specific build, deleting a build,
    uploading a new build, and deploying a build.

    Args:
        ctx (click.Context): The context object that holds state across the
            entire command execution.

    """
    ensure_logged_in(ctx)


@build.command()
def init() -> None:
    """
    Initialize a new project by downloading and extracting the starter package.

    This command downloads the starter package for the app and extracts it into
    the current working directory. If a starter package has already been
    extracted, it prompts the user to confirm whether to replace it or not.

    After extracting the starter package, it sets up the project by configuring
    the necessary files and settings with the current user's name and email.

    """
    ctx: click.Context = click.get_current_context()

    if starter_package_already_extracted_on_current_directory():
        if not click.confirm("Starter package already extracted. Do you want to replace?"):
            return
        remove_existing_starter_package()

    # get the starter package for the app
    download_url: str = get_starter_package_for_app(ctx.obj.oauth_token)
    if not download_url:
        click.echo("No starter package found.")
        return
    app_config = get_app_config()
    app_display_name = app_config.get('displayName')
    filename = app_display_name + ".zip"
    # download the starter package
    is_file_downloaded = download_file_using_url(download_url, filename)
    if not is_file_downloaded:
        click.echo("Failed to download the starter package.")
        return

    # extract the starter package
    extract_zip_to_current_cwd(filename)

    name, email = get_current_role_name_and_email(ctx.obj.oauth_token)

    # setup the project
    setup_project(name, email)


@build.command()
def list() -> None:
    """
    List all builds along with their statuses.

    This command retrieves and displays a list of all builds for the current
    app, along with their respective statuses (e.g., draft, deploying, deployed,
    deploy_failed).

    """
    ctx: click.Context = click.get_current_context()
    endpoint = "/apps/api/app_builds"
    app_name = get_app_config().get("name")
    data = {"app_name": app_name}
    paginate_data(endpoint, ctx.obj.oauth_token, display_builds, data=data)


@build.command()
@click.option("--build_id", required=True, type=str, help="The build id to be downloaded on the cwd.")
def download(build_id: str):
    """
    Download a specific build identified by its build ID.

    This command fetches and downloads a specific build identified by its
    build ID. The build is downloaded and saved in the current working
    directory.

    Args:
        build_id (str): The ID of the build to be downloaded.

    """
    ctx: click.Context = click.get_current_context()
    endpoint = "/apps/api/app_builds/?large_get_query=true"
    build_json = get_data_by_id(build_id, ctx.obj.oauth_token, endpoint)
    build_url = build_json.get("build_file")
    build_name = build_json.get("name")
    build_file_name = build_name + ".zip"
    download_file_using_url(build_url, build_file_name)


@build.command()
@click.option("--build_id", required=True, type=str, help="The build id to be deleted.")
def delete(build_id: str):
    """
    Delete a specific build identified by its build ID.

    This command deletes a specific build identified by its build ID.

    Args:
        build_id (str): The ID of the build to be deleted.

    """
    ctx: click.Context = click.get_current_context()
    endpoint = f"/apps/api/app_builds/{build_id}"
    is_build_deleted = delete_data_by_id(ctx.obj.oauth_token, endpoint)
    if not is_build_deleted:
        click.echo("Failed to delete the build.")
        return
    click.echo(f"Build {build_id} deleted successfully.")


@build.command()
def upload() -> None:
    """
    Upload a new build for the current app.

    This command creates a zip file of the current app, including all Poetry
    dependencies from the poetry.lock file. It then uploads the zip file to
    a specified s3 bucket, validates the bundle and creates a new build for
    the app.

    """
    ctx: click.Context = click.get_current_context()

    click.echo(click.style('Uploading app build...', fg='yellow'))

    app_config = get_app_config()
    suggested_build_name, s3_upload_file_credentials = package_and_validate_bundle(ctx.obj.oauth_token)

    if not s3_upload_file_credentials or not suggested_build_name:
        return

    click.echo(click.style('Creating app build...', fg='magenta'))

    # create the build
    build_created = create_build(app_config.get("name"), s3_upload_file_credentials.s3_build_url, suggested_build_name,
                                 ctx.obj.oauth_token)

    if not build_created:
        click.echo("Failed to create the build.")
        return

    click.echo(click.style('App build created successfully!', fg='green', bold=True))


@build.command()
@click.option("--build_id", required=True, type=str, help="The build id to be deployed.")
def deploy(build_id: str):
    """
    Deploy a specific build identified by its build ID.

    This command deploys a specific build identified by its build ID. It
    triggers the deployment process for the specified build.

    Args:
        build_id (str): The ID of the build to be deployed.

    """
    ctx: click.Context = click.get_current_context()
    # deploy the build
    app_config = get_app_config()
    is_deployed = deploy_build(app_config.get("name"), build_id, ctx.obj.oauth_token)
    if not is_deployed:
        click.echo("Failed to deploy the build.")
        return

    click.echo("Build deployed successfully.")