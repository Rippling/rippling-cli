from http import client

import requests  # type: ignore


class APIClient:
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.headers = headers or {}

    def make_request(self, method, endpoint, params=None, json=None, data=None, stream=False, files=None):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, json=json, data=data, headers=self.headers,
                                    stream=stream, files=files)
        return response

    def get(self, endpoint, params=None, stream=False):
        return self.make_request("GET", endpoint, params=params, stream=stream)

    def post(self, endpoint, data=None, files=None):
        return self.make_request("POST", endpoint, data=data, files=files)

    def put(self, endpoint, data):
        return self.make_request("PUT", endpoint, data=data)

    def delete(self, endpoint, params=None, data=None):
        return self.make_request("DELETE", endpoint, params=params, data=data)

    def find_paginated(self, endpoint, page=1, page_size=10, read_preference="SECONDARY_PREFERRED", data=None):
        """
        Fetch paginated data from the API.

        Args:
            endpoint (str): The API endpoint.
            headers (dict): The headers for the API request.
            page (int): The page number to fetch.
            per_page (int): The number of items to fetch per page.

        Yields:
            dict: The data from the API response.
            :param endpoint:
            :param page:
            :param page_size:
            :param read_preference:
        """
        has_more = True
        cursor = None
        while has_more:
            payload = {
                "paginationParams": {
                    "page": page,
                    "cursor": cursor,
                    "sortingMetadata": {
                        "order": "DESC",
                        "column": {
                            "sortKey": "createdAt"
                        }
                    }
                },
                "pageSize": page_size,
                "readPreference": read_preference
            }
            if data:
                payload.update(data)
            response = self.make_request("POST", f"{endpoint}/find_paginated", json=payload)

            if response.status_code == client.OK:
                response_json = response.json()
                cursor = response_json.get("cursor")
                has_more = False if not cursor else True
                items = response_json["data"]
                page += 1
                yield items
            else:
                response.raise_for_status()
                break
