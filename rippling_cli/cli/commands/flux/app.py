import click

from rippling_cli.config.config import get_app_config, save_app_config
from rippling_cli.constants import RIPPLING_BASE_URL
from rippling_cli.utils.api_utils import get_data_by_id
from rippling_cli.utils.app_utils import (
    delete_app_install_for_app,
    display_apps,
    get_app_install,
    install_app_for_company,
)
from rippling_cli.utils.login_utils import ensure_logged_in
from rippling_cli.utils.pagination_utils import paginate_data
from rippling_cli.utils.server import set_forwarding_url, validate_forwarding_url_set


@click.group()
@click.pass_context
def app(ctx: click.Context):
    """
    Manage Flux apps, including listing, setting, and displaying the current app.

    This command group is the entry point for managing flux apps. It provides
    subcommands for various app-related operations, such as listing all apps,
    setting the current app for the directory, and displaying the currently
    selected app.

    """
    ensure_logged_in(ctx)


@app.command()
@click.option("--search_query", type=str, help="search query to filter apps.")
def list(search_query: str) -> None:
    """
    Display a list of all apps owned by the developer.

    This command retrieves and displays a list of all apps owned by the
    currently logged-in developer. It paginates the data and displays the
    app ID, display name, and app name for each app.

    """
    ctx: click.Context = click.get_current_context()
    endpoint = "/apps/api/integrations"
    paginate_data(endpoint, ctx.obj.oauth_token, display_apps, search_query=search_query)


@app.command()
@click.option("--app_id", required=True, type=str, help="The app id to set for the current directory.")
def set(app_id: str):
    """
    Set the current app context within the directory.

    This command sets the current app context within the directory.
    """
    ctx: click.Context = click.get_current_context()
    endpoint = f"/apps/api/apps/{app_id}"
    app_json = get_data_by_id(ctx.obj.oauth_token, endpoint)

    if not app_json:
        click.echo(f"Invalid app id: {app_id}")
        return

    display_name = app_json.get("displayName")
    app_name = app_json.get("name")

    save_app_config(app_id, display_name, app_name)
    click.echo(f"Current app set to {display_name} ({app_id})")


@app.command()
def current():
    """
    Display the currently selected app.

    This command indicates the current app selected by the developer within
    the directory. It displays the display name and ID of the currently
    selected app.

    """
    app_config = get_app_config()
    if not app_config or len(app_config.keys()) == 0:
        click.echo("No app selected.")
        return

    click.echo(f"{app_config.get('displayName')} ({app_config.get('id')})")


@app.command()
def install() -> None:
    """
    Install the current app by opening the url on the browser.
    """
    ctx: click.Context = click.get_current_context()
    app_config = get_app_config()
    if not app_config or len(app_config.keys()) == 0:
        click.echo("No app found for the context. Please set the app using the 'set' command")
        return

    resp_json, continue_installation = install_app_for_company(app_config.get("name"), ctx.obj.oauth_token)
    message = resp_json and resp_json.get("message")
    if not resp_json:
        message = "Failed to install the app."

    click.echo(message)

    if not continue_installation:
        return

    installation_url = resp_json.get("installation_url")
    click.echo(
        click.style("Opening the installation url: ", fg="green", bold=True)
        + click.style(RIPPLING_BASE_URL + installation_url, fg="blue", underline=True)
    )
    click.launch(RIPPLING_BASE_URL + installation_url)


@app.command()
def uninstall() -> None:
    """
    Uninstall the current app by calling the uninstall endpoint.
    """
    ctx: click.Context = click.get_current_context()
    app_config = get_app_config()
    if not app_config or len(app_config.keys()) == 0:
        click.echo("No app found for the context. Please set the app using the 'set' command")
        return

    endpoint = f"/apps/api/apps/{app_config.get('id')}"
    app_json = get_data_by_id(ctx.obj.oauth_token, endpoint)

    if not app_json:
        click.echo("Failed to uninstall the app.")
        return

    spoke_handle = app_json.get("spoke", {}).get("handle")
    company_id = app_json.get("spoke", {}).get("company")

    if not spoke_handle or not company_id:
        click.echo("Failed to uninstall the app.")
        return

    uninstall_succeeded = delete_app_install_for_app(spoke_handle, company_id, ctx.obj.oauth_token)
    if not uninstall_succeeded:
        click.echo("Failed to uninstall the app.")
        return

    click.echo("Successfully uninstalled the app.")


@app.command()
@click.option("--forwarding_url", "-fu", required=True, type=str,
              help="The URL to which the request should be forwarded.")
@click.option("--timeout", "-t", type=int, default=3600, help="Timeout for port forwarding (in seconds).")
def connect(forwarding_url, timeout) -> None:
    """
    Set the forwarding URL for the app install using the specified URL and timeout and validate the URL
    by checking if it is forwarding to the local server.
    """
    ctx: click.Context = click.get_current_context()

    app_install_json = get_app_install(ctx.obj.oauth_token)
    if not app_install_json:
        click.echo("No app install found for the current app. Please install the app using the 'install' command")
        return

    is_valid = validate_forwarding_url_set(forwarding_url)

    if not is_valid:
        click.echo("Url not forwarding to local server. Please check the URL and try again.")
        return

    # Set the forwarding URL with a timeout
    forwarding_url_set, message = set_forwarding_url(app_install_json.get("id"), forwarding_url,
                                                     timeout, ctx.obj.oauth_token)

    if not forwarding_url_set:
        message = "Failed to set the forwarding URL" if not message else message
        click.echo(message)
        return

    click.echo("Successfully set the forwarding URL.")
