from http import HTTPStatus

import click

from rippling_cli.cli.commands.login import login
from rippling_cli.cli.commands.logout import logout
from rippling_cli.constants import RIPPLING_API
from rippling_cli.core.api_client import APIClient
from rippling_cli.core.oauth_token import OAuthToken


def ensure_logged_in(ctx: click.Context):
    if OAuthToken.is_token_expired():
        ctx.invoke(logout)
        ctx.invoke(login)


def get_account_info(oauth_token):
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    endpoint = "/auth_ext/get_account_info_v2/"
    response = api_client.get(endpoint)
    if response.status_code != HTTPStatus.OK:
        return {}
    return response.json()


def get_employee_details(role_id, oauth_token):
    api_client = APIClient(base_url=RIPPLING_API, headers={"Authorization": f"Bearer {oauth_token}"})
    endpoint = f"/api/hub/api/employment_roles_with_company/{role_id}"
    response = api_client.get(endpoint)
    if response.status_code != HTTPStatus.OK:
        return {}
    return response.json()


def get_current_role_name_and_email(oauth_token):
    account_info_dict = get_account_info(oauth_token)
    if not account_info_dict and len(account_info_dict) == 0:
        return None, None
    role_id = account_info_dict[0].get("id")
    employee_details = get_employee_details(role_id, oauth_token)
    return employee_details.get("fullName"), employee_details.get("workEmail")


def get_role_and_company_id(oauth_token):
    account_info_dict = get_account_info(oauth_token)
    if not account_info_dict and len(account_info_dict) == 0:
        return None, None
    role_id = account_info_dict[0].get("id", None)
    company_id = account_info_dict[0].get("company", {}).get("_id", {}).get("$oid", None)
    return role_id, company_id


def get_api_client_with_role_company(oauth_token):
    role_id, company_id = get_role_and_company_id(oauth_token)
    if not role_id or not company_id:
        return None
    return APIClient(base_url=RIPPLING_API, headers={
        "Authorization": f"Bearer {oauth_token}",
        "role": role_id,
        "company": company_id,
    })