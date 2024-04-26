import click

from rippling_cli.cli.commands.flux.app import app
from rippling_cli.cli.commands.flux.build import build
from rippling_cli.cli.commands.flux.check import check
from rippling_cli.cli.commands.flux.install import install
from rippling_cli.cli.commands.flux.uninstall import uninstall
from rippling_cli.utils.login_utils import ensure_logged_in


@click.group()
@click.pass_context
def flux(ctx: click.Context):
    """
    The flux command group.

    This command group is the entry point for the Flux CLI application. It
    serves as the base command group and provides access to various subcommands
    for managing and interacting with Flux apps, builds, and other related
    functionality.

    The flux command group itself does not perform any specific actions but
    acts as a container for its subcommands. It is responsible for setting up
    the initial context and ensuring that the user is logged in before
    executing any subcommands.

    Subcommands:
        - app: Manage Flux apps, including listing, setting, and displaying
               the current app.
        - build: Manage Flux builds, including initializing, listing,
                 downloading, deleting, uploading, and deploying builds.
        - check: Validates the current app bundle by packaging and uploading
                 it to an S3 bucket.
        - install: Install the current app by opening the app install url in
                   the browser.
        - uninstall: Uninstall the current app by removing it from the user's
                     account.

    Args:
        ctx (click.Context): The context object that holds state across the
            entire command execution.
    """
    ensure_logged_in(ctx)


flux.add_command(app)  # type: ignore
flux.add_command(build)  # type: ignore
flux.add_command(check)  # type: ignore
flux.add_command(install)  # type: ignore
flux.add_command(uninstall)  # type: ignore
