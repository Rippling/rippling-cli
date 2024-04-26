import click

from rippling_cli.utils.build_utils import package_and_validate_bundle
from rippling_cli.utils.login_utils import ensure_logged_in


@click.command()
@click.pass_context
def check(ctx: click.Context):
    """
    Check the bundle for the current app.

    This command creates a zip file of the current app, including all Poetry
    dependencies from the poetry.lock file. It then uploads the zip file to
    a specified s3 bucket, validates the bundle and prints the error
    or success message.

    Args:
        ctx (click.Context): The context object that holds state across the
    """
    ensure_logged_in(ctx)

    ctx: click.Context = click.get_current_context()
    package_and_validate_bundle(ctx.obj.oauth_token)
