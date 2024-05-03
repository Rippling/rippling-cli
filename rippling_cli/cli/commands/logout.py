import click

from rippling_cli.config.config import remove_oauth_token
from rippling_cli.utils.logout import logout_api


@click.command()
@click.pass_context
def logout(ctx) -> None:
    """
    Log out of the Rippling CLI by revoking the current OAuth token.
    """
    oauth_token = ctx.obj.oauth_token

    if not oauth_token:
        click.echo("You are not logged in. Please log in first.")
        return

    logout_successful = logout_api(oauth_token)
    if not logout_successful:
        click.echo("Logout failed.")
        return

    remove_oauth_token()
    click.echo("Logout successful!")
