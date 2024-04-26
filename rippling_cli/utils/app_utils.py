from http import client

import click

from rippling_cli.config.config import get_app_config
from rippling_cli.constants import RIPPLING_API
from rippling_cli.core.api_client import APIClient
from rippling_cli.utils.api_utils import delete_data_by_id


def get_starter_package_for_app(oauth_token):
    """
    Get the starter package for the app.
    :param oauth_token:
    :return:
    """
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    app_config = get_app_config()
    endpoint = f"/apps/api/flux_apps/get_starter_package?app_name={app_config.get('name')}"
    response = api_client.post(endpoint)
    response.raise_for_status()
    return response.json().get("link")


def display_apps(apps, page_number):
    """
    Display the apps.
    :param apps:
    :param page_number:
    :return:
    """
    click.echo(f"Page {page_number}: {len(apps)} apps")

    for app in apps:
        click.echo(f"- {app.get('displayName')} ({app.get('id')})")


def get_app_install_for_app(spoke_handle: str, company_id: str, oauth_token: str):
    """
    Delete the app install for the app by calling the app installs endpoint.
    :param spoke_handle:
    :param company_id:
    :param oauth_token:
    :return:
    """
    endpoint = "/hub/api/app_installs/?large_get_query=true"
    data = {"query": f"spoke__handle={spoke_handle}&installState=FINISH&company={company_id}&limit=1"}
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    response = api_client.post(endpoint, data=data)
    response_json = response.json()
    if response.status_code != client.OK or len(response_json) == 0:
        return None
    return response.json()[0]


def delete_app_install_for_app(spoke_handle: str, company_id: str, oauth_token: str):
    """
    Delete the app install for the app by calling the app installs endpoint.
    :param spoke_handle:
    :param company_id:
    :param oauth_token:
    :return:
    """
    app_install_json = get_app_install_for_app(spoke_handle, company_id, oauth_token)
    if not app_install_json:
        return None
    app_install_id = app_install_json.get("id")

    endpoint = f"/hub/api/app_installs/{app_install_id}"
    return delete_data_by_id(oauth_token, endpoint)
