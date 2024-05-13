from rippling_cli.constants import RIPPLING_API
from rippling_cli.core.api_client import APIClient


def logout_api(oauth_token):
    """
    Log out of the Rippling CLI by revoking the current OAuth token.
    :param oauth_token:
    :return:
    """
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    response = api_client.post("/auth_ext/logout/")
    logout_successful = response.json().get("logout", False) if response.status_code else None
    return logout_successful

