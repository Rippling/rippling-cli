import click

from rippling_cli.config.config import get_app_config
from rippling_cli.utils.api_utils import get_data_by_id
from rippling_cli.utils.app_utils import delete_app_install_for_app
from rippling_cli.utils.login_utils import ensure_logged_in


@click.command()
@click.pass_context
def uninstall(ctx: click.Context):
    """
    Uninstall the current app by calling the uninstall endpoint.
    :param ctx:
    :return:
    """
    ensure_logged_in(ctx)
    app_config = get_app_config()
    endpoint = "/apps/api/apps/?large_get_query=true"
    app_json = get_data_by_id(app_config.get("id"), ctx.obj.oauth_token, endpoint)

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