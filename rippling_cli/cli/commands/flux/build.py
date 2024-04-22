import click

from rippling_cli.config.config import get_app_config
from rippling_cli.core.setup_project import setup_project
from rippling_cli.utils.app_utils import get_starter_package_for_app
from rippling_cli.utils.build_utils import (
    remove_existing_starter_package,
    starter_package_already_extracted_on_current_directory,
)
from rippling_cli.utils.file_utils import download_file_using_url, extract_zip_to_current_cwd
from rippling_cli.utils.login_utils import ensure_logged_in, get_current_role_name_and_email


@click.group()
@click.pass_context
def build(ctx: click.Context) -> None:
    """Manage flux builds"""
    ensure_logged_in(ctx)


@build.command()
def init() -> None:
    """This command downloads the starter package and extracts it into a specified folder."""
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
