import sys
from typing import Union

import click

from rippling_cli.cli.commands.login import login
from rippling_cli.config.config import get_client_id, get_oauth_token_data
from rippling_cli.constants import EXIT_UNKNOWN_EXCEPTION
from rippling_cli.core.oauth_token import OAuthToken
from rippling_cli.core.rippling_context import RipplingContext


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.pass_context
@click.version_option()
def cli(ctx):
    """
    rippling cli

    This is a command-line interface (CLI) tool for interacting with Rippling services. The Flux commands as part of
    the Rippling CLI allow both first-party and third-party App developers to create, manage and deploy
    Rippling-hosted integrations.

    Available Commands:
      login   Authenticate and authorize with Rippling services.

    Options:
      -h, --help     Show this message and exit.
      --version      Show the version and exit.
    """

    # Initialize the context object
    ctx.obj = RipplingContext()

    # Load the OAuth credentials from the config.py file
    ctx.obj.oauth_credentials = get_client_id()

    # Load the OAuth token from the config directory
    oauth_token_dict = get_oauth_token_data()
    ctx.obj.oauth_token = oauth_token_dict.get("token") if not OAuthToken.is_token_expired() else None


COMMANDS_LIST: list[Union[click.Command, click.Group]] = [
    login
]


# Initialize the CLI
def initialize_cli() -> None:
    for command in COMMANDS_LIST:
        # Add the commands to the CLI
        cli.add_command(command)


if __name__ == "__main__":
    exit_code = 0
    try:
        initialize_cli()
        cli()
    except Exception:
        exit_code = EXIT_UNKNOWN_EXCEPTION
    finally:
        sys.exit(exit_code)
