from http import client

from rippling_cli.constants import RIPPLING_API
from rippling_cli.core.api_client import APIClient


def get_data_by_id(item_id, oauth_token, endpoint: str):
    """
    Get data by id from the endpoint.
    :param item_id:
    :param oauth_token:
    :param endpoint:
    :return:
    """
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})

    response = api_client.post(endpoint, data={"query": f"id={item_id}&limit=1"})
    data_list = response.json() if response.status_code == client.OK else []

    if response.status_code != client.OK or len(data_list) == 0:
        return None
    return data_list[0]


def delete_data_by_id(oauth_token, endpoint: str):
    """
    Delete data by id from the endpoint.
    :param oauth_token:
    :param endpoint:
    :return:
    """
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    response = api_client.delete(endpoint)
    response.raise_for_status()
    return response.status_code == client.OK
