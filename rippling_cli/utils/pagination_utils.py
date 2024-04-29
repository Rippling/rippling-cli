from typing import Callable, Optional

import click

from rippling_cli.constants import DEFAULT_PAGE_SIZE, RIPPLING_API
from rippling_cli.core.api_client import APIClient


def paginate_data(endpoint: str, oauth_token: str, display_function: Callable, data: Optional[dict] = None,
                  search_query: Optional[str]=None):
    """
    Paginate the data using the endpoint and display the data using the display function provided.
    :param search_query:
    :param endpoint:
    :param oauth_token:
    :param display_function:
    :param data:
    :return:
    """
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    page_number = 1

    for page in api_client.find_paginated(endpoint, data=data, search_query=search_query):
        if not page:
            break

        display_function(page)

        if len(page) < DEFAULT_PAGE_SIZE or not click.confirm("Load more ?"):
            break

        page_number += 1
