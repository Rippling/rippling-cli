import click

from rippling_cli.config.config import get_app_config
from rippling_cli.utils.build_utils import package_and_validate_bundle
from rippling_cli.utils.login_utils import ensure_logged_in


@click.command()
@click.pass_context
def check(ctx: click.Context):
    """
    Validates the current app bundle by packaging and uploading it to an S3 bucket

    This command creates a zip file of the current app, including all Poetry
    dependencies from the poetry.lock file. It then uploads the zip file to
    a specified s3 bucket, validates the bundle and prints the error
    or success message.

    """
    ensure_logged_in(ctx)
    app_config = get_app_config()
    if not app_config or len(app_config.keys()) == 0:
        click.echo("No app found for the context. Please set the app using the 'set' command")
        return
    package_and_validate_bundle(ctx.obj.oauth_token)
