import click

from rippling_cli.cli.commands.flux.app import app
from rippling_cli.cli.commands.flux.build import build
from rippling_cli.utils.login_utils import ensure_logged_in


@click.group()
@click.pass_context
def flux(ctx: click.Context) -> None:
    """Manage flux apps"""
    ensure_logged_in(ctx)


flux.add_command(app)  # type: ignore
flux.add_command(build)  # type: ignore
