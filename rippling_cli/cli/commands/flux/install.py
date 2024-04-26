import click

from rippling_cli.config.config import get_app_config
from rippling_cli.constants import RIPPLING_BASE_URL
from rippling_cli.utils.api_utils import get_data_by_id
from rippling_cli.utils.app_utils import get_app_install_for_app
from rippling_cli.utils.login_utils import ensure_logged_in


@click.command()
@click.pass_context
def install(ctx: click.Context):
    """
    Install the current app by opening the url on the browser.
    :param ctx:
    :return:
    """
    ensure_logged_in(ctx)
    app_config = get_app_config()
    endpoint = "/apps/api/apps/?large_get_query=true"
    app_json = get_data_by_id(app_config.get("id"), ctx.obj.oauth_token, endpoint)

    if not app_json:
        click.echo("Failed to install the app.")
        return

    spoke_handle = app_json.get("spoke", {}).get("handle")
    company_id = app_json.get("spoke", {}).get("company")

    app_install_json = get_app_install_for_app(spoke_handle, company_id, ctx.obj.oauth_token)
    if app_install_json:
        click.echo("App is already installed.")
        return None

    installation_url = app_json.get("installation_url")
    click.echo(
        click.style("Opening the installation url: ", fg="green", bold=True)
        + click.style(RIPPLING_BASE_URL + installation_url, fg="blue", underline=True)
    )
    click.launch(RIPPLING_BASE_URL + installation_url)
