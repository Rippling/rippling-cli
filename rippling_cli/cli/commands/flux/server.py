
import click

from rippling_cli.core.flask_server import FlaskServer
from rippling_cli.utils.app_utils import get_app_install
from rippling_cli.utils.login_utils import ensure_logged_in


@click.group()
@click.pass_context
def server(ctx: click.Context):
    """
    Manage the server and port forwarding for local development by starting the server and forwarding
    the port using ngrok which sets the forwarding URL for the app install.

    Commands:
        - start: Start the server and forward the port using ngrok for local development and set the forwarding URL.
    :param ctx:
    :return:
    """
    ensure_logged_in(ctx)


@server.command()
@click.option("-d","--debug", is_flag=True, help="Start Flask in debug mode.")
@click.option("-p","--port", type=int, default=5000, help="Port number to run the server on.")
def start(debug: bool, port: str):
    """
    Start the server and forward the port using ngrok for local development and set the forwarding URL.
    :param port:
    :param debug:
    :return:
    """

    ctx: click.Context = click.get_current_context()
    app_install_json = get_app_install(ctx.obj.oauth_token)
    if not app_install_json:
        click.echo("No app install found for the current app. Please install the app using the 'install' command")
        return
    flask_server = FlaskServer(debug, port)
    try:
        flask_process = flask_server.start()
        flask_process.wait()
        flask_server.stop()
    except KeyboardInterrupt:
        flask_server.stop()
        return

