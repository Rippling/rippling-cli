from pathlib import Path

import click

from rippling_cli.config.config import save_oauth_token
from rippling_cli.constants import CODE_CHALLENGE_METHOD
from rippling_cli.core.oauth_client import OAuthClient
from rippling_cli.core.oauth_pkce import PKCE
from rippling_cli.core.oauth_token import OAuthToken


@click.command()
@click.pass_context
def login(ctx) -> None:
    """
    Log in to the application using OAuth
    """
    client_id, client_secret = ctx.obj.oauth_credentials
    if client_id and client_secret:
        if not ctx.obj.oauth_token:
            client_id, client_secret = OAuthClient.get_client_credentials()

            code_verifier = PKCE.generate_code_verifier()
            code_challenge = PKCE.get_code_challenge(code_verifier)

            token = OAuthToken(client_id, code_challenge, CODE_CHALLENGE_METHOD)
            token.start_authorization_flow()
            access_token = token.exchange_for_token(client_secret, code_verifier)
            ctx.obj.oauth_token = access_token

            save_oauth_token(access_token, token.expires_in)
            click.echo(f"Login successful!")
    else:
        click.echo("OAuth credentials not configured")
