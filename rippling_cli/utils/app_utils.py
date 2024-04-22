from rippling_cli.config.config import get_app_config
from rippling_cli.constants import RIPPLING_API
from rippling_cli.core.api_client import APIClient


def get_app_from_id(app_id, oauth_token):
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})

    endpoint = "/apps/api/apps/?large_get_query=true"
    response = api_client.post(endpoint, data={"query": f"id={app_id}&limit=1"})
    app_list = response.json() if response.status_code == 200 else []

    if response.status_code != 200 or len(app_list) == 0:
        return None
    return app_list[0]


def get_starter_package_for_app(oauth_token):
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    app_config = get_app_config()
    endpoint = f"/apps/api/flux_apps/get_starter_package?app_name={app_config.get('name')}"
    response = api_client.post(endpoint)
    response.raise_for_status()
    return response.json().get("link")