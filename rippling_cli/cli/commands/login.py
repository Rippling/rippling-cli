
import click

from rippling_cli.config.config import save_oauth_token
from rippling_cli.constants import CODE_CHALLENGE_METHOD, DEFAULT_CODE_VERIFIER_LENGTH
from rippling_cli.core.oauth_pkce import PKCE
from rippling_cli.core.oauth_token import OAuthToken


@click.command()
@click.pass_context
def login(ctx) -> None:
    """
    Authenticate and authorize with Rippling services.

    This command logs in to the Rippling by starting the OAuth authorization flow, getting the authorization code
    and exchanging it for an access token.
    """
    client_id = ctx.obj.oauth_credentials
    if client_id:
        if ctx.obj.oauth_token:
            click.echo("Already logged in")
        else:
            click.echo("Initiating login flow...")
            code_verifier, code_challenge = PKCE.generate_pkce_pair(DEFAULT_CODE_VERIFIER_LENGTH)

            token = OAuthToken(client_id, code_challenge, CODE_CHALLENGE_METHOD)
            token.start_authorization_flow()
            access_token = token.exchange_for_token(code_verifier)
            ctx.obj.oauth_token = access_token

            save_oauth_token(access_token, token.expires_in)
            click.echo("Login successful!")
    else:
        click.echo("OAuth credentials not configured")
