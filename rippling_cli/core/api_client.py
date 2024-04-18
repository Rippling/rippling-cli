import requests


class APIClient:
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.headers = headers or {}

    def make_request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, json=data, headers=self.headers)
        return response

    def get(self, endpoint, params=None):
        return self.make_request("GET", endpoint, params=params)

    def post(self, endpoint, data):
        return self.make_request("POST", endpoint, data=data)

    def put(self, endpoint, data):
        return self.make_request("PUT", endpoint, data=data)

    def delete(self, endpoint, params=None):
        return self.make_request("DELETE", endpoint, params=params)

    def find_paginated(self, endpoint, page=1, page_size=10, read_preference="SECONDARY_PREFERRED"):
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
            response = self.make_request("POST", f"{endpoint}/find_paginated", data=payload)

            if response.status_code == 200:
                data = response.json()
                cursor = data.get("cursor")
                has_more = False if not cursor else True
                items = data["data"]
                page += 1
                print(page)
                yield items
            else:
                response.raise_for_status()
                break
