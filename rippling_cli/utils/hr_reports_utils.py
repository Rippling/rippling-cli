import json
from http import HTTPStatus
from typing import Any, Optional

from rippling_cli.constants import RIPPLING_API
from rippling_cli.core.api_client import APIClient
from rippling_cli.utils.login_utils import get_api_client_with_role_company

HR_EMPLOYEE_LIST_ENDPOINTS = [
    "/api/hub/api/employment_roles_with_company",
    "/api/hub/api/employment_roles",
    "/api/hr/api/employees",
]

HR_TIME_OFF_ENDPOINTS = [
    "/api/hub/api/time_off_requests",
    "/api/time_off/api/requests",
]

HR_PAYROLL_ENDPOINTS = [
    "/api/payroll/api/payroll_runs",
    "/api/payroll/api/payroll_summary",
]

REPORTS_LIST_ENDPOINTS = [
    "/api/reports/api/reports",
    "/api/analytics/api/reports",
]

REPORTS_RUN_ENDPOINTS = [
    "/api/reports/api/reports/run",
    "/api/analytics/api/reports/run",
]

REPORTS_EXPORT_ENDPOINTS = [
    "/api/reports/api/reports/export",
    "/api/analytics/api/reports/export",
]


def get_authenticated_api_client(oauth_token: str) -> APIClient:
    role_company_client = get_api_client_with_role_company(oauth_token)
    if role_company_client:
        return role_company_client
    return APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})


def parse_json_option(value: Optional[str], field_name: str) -> Optional[dict[str, Any]]:
    if not value:
        return None
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError(f"{field_name} must be a JSON object")
    return parsed


def get_first_success(client: APIClient, endpoints: list[str], params: Optional[dict[str, Any]] = None) -> tuple[Optional[Any], Optional[str]]:
    for endpoint in endpoints:
        response = client.get(endpoint, params=params)
        if response.status_code == HTTPStatus.OK:
            return response, endpoint
    return None, None


def post_first_success(
    client: APIClient,
    endpoints: list[str],
    payload: Optional[dict[str, Any]] = None,
) -> tuple[Optional[Any], Optional[str]]:
    for endpoint in endpoints:
        response = client.post(endpoint, json=payload)
        if response.status_code in (HTTPStatus.OK, HTTPStatus.CREATED):
            return response, endpoint
    return None, None


def find_paginated_first_success(
    client: APIClient,
    endpoints: list[str],
    page_size: int = 10,
    search_query: str = "",
    data: Optional[dict[str, Any]] = None,
) -> tuple[Optional[list[dict[str, Any]]], Optional[str]]:
    for endpoint in endpoints:
        iterator = client.find_paginated(endpoint, page_size=page_size, search_query=search_query, data=data)
        first_page = next(iterator, None)
        if first_page:
            return first_page, endpoint
    return None, None
