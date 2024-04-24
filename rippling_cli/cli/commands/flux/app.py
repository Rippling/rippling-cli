
import click

from rippling_cli.config.config import get_app_config, save_app_config
from rippling_cli.constants import RIPPLING_API
from rippling_cli.core.api_client import APIClient
from rippling_cli.utils.app_utils import get_app_from_id
from rippling_cli.utils.login_utils import ensure_logged_in


@click.group()
@click.pass_context
def app(ctx: click.Context) -> None:
    """Manage flux apps"""
    ensure_logged_in(ctx)


@app.command()
def list() -> None:
    """This command displays a list of all apps owned by the developer."""
    ctx: click.Context = click.get_current_context()
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {ctx.obj.oauth_token}"})
    endpoint = "/apps/api/integrations"

    for page in api_client.find_paginated(endpoint):
        click.echo(f"Page: {len(page)} apps")

        for app in page:
            click.echo(f"- {app.get('displayName')} ({app.get('id')})")

        if not click.confirm("Continue"):
            break

    click.echo("End of apps list.")


@app.command()
@click.option("--app_id", required=True, type=str, help="The app id to set for the current directory.")
def set(app_id: str) -> None:
    """This command sets the current app within the app_config.json file located in the .rippling directory."""
    ctx: click.Context = click.get_current_context()
    app_json = get_app_from_id(app_id, ctx.obj.oauth_token)

    if not app_json:
        click.echo(f"Invalid app id: {app_id}")
        return

    display_name = app_json.get("displayName")
    app_name = app_json.get("name")

    save_app_config(app_id, display_name, app_name)
    click.echo(f"Current app set to {display_name} ({app_id})")


@app.command()
def current() -> None:
    """This command indicates the current app selected by the developer within the directory."""
    app_config = get_app_config()
    if not app_config or len(app_config.keys()) == 0:
        click.echo("No app selected.")
        return

    click.echo(f"{app_config.get('displayName')} ({app_config.get('id')})")
