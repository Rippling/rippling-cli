import click

from rippling_cli.cli.commands.login import login
from rippling_cli.core.oauth_token import OAuthToken


def ensure_logged_in(ctx: click.Context):
    if OAuthToken.is_token_expired():
        click.echo("You are not logged in. Please log in first.")
        ctx.invoke(login)
