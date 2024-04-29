from http import client

from rippling_cli.constants import RIPPLING_API
from rippling_cli.core.api_client import APIClient


def get_data_by_id(oauth_token, endpoint: str):
    """
    Get data by id from the endpoint.
    :param item_id:
    :param oauth_token:
    :param endpoint:
    :return:
    """
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})

    response = api_client.get(endpoint)
    data_list = response.json() if response.status_code == client.OK else []
    if response.status_code != client.OK or len(data_list) == 0:
        return None
    return data_list


def delete_data_by_id(oauth_token, endpoint: str):
    """
    Delete data by id from the endpoint.
    :param oauth_token:
    :param endpoint:
    :return:
    """
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    response = api_client.delete(endpoint)
    return response.status_code == client.OK
