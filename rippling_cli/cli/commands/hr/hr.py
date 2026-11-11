import click

from rippling_cli.utils.hr_reports_utils import (
    HR_EMPLOYEE_LIST_ENDPOINTS,
    HR_PAYROLL_ENDPOINTS,
    HR_TIME_OFF_ENDPOINTS,
    find_paginated_first_success,
    get_authenticated_api_client,
    get_first_success,
)
from rippling_cli.utils.login_utils import ensure_logged_in


def display_employees(rows: list[dict]) -> None:
    for row in rows:
        employee_id = row.get("id") or row.get("_id") or row.get("employeeId")
        email = row.get("workEmail") or row.get("email") or "-"
        full_name = row.get("fullName") or row.get("name") or row.get("displayName") or "Unknown"
        click.echo(f"- {full_name} ({employee_id}) [{email}]")


@click.group()
@click.pass_context
def employee(ctx: click.Context) -> None:
    """
    Employee directory operations.
    """
    ensure_logged_in(ctx)


@employee.command("list")
@click.option("--search_query", type=str, default="", help="Search query for employee list.")
@click.pass_context
def list_employees(ctx: click.Context, search_query: str) -> None:
    """
    List/search employees.
    """
    api_client = get_authenticated_api_client(ctx.obj.oauth_token)
    first_page, matched_endpoint = find_paginated_first_success(
        client=api_client,
        endpoints=HR_EMPLOYEE_LIST_ENDPOINTS,
        search_query=search_query,
    )

    if not first_page:
        click.echo("No employees found or no accessible employee endpoint.")
        return

    click.echo(f"Using endpoint: {matched_endpoint}")
    display_employees(first_page)


@employee.command("get")
@click.option("--employee_id", type=str, required=False, help="Employee identifier.")
@click.option("--email", type=str, required=False, help="Employee work email.")
@click.pass_context
def get_employee(ctx: click.Context, employee_id: str, email: str) -> None:
    """
    Get employee details by id or email.
    """
    if not employee_id and not email:
        click.echo("Provide either --employee_id or --email.")
        return

    api_client = get_authenticated_api_client(ctx.obj.oauth_token)

    if employee_id:
        endpoint_candidates = [f"/api/hub/api/employment_roles_with_company/{employee_id}"]
        response, _ = get_first_success(api_client, endpoint_candidates)
        if not response:
            click.echo("Employee not found.")
            return
        click.echo(response.text)
        return

    params = {"email": email}
    response, matched_endpoint = get_first_success(api_client, HR_EMPLOYEE_LIST_ENDPOINTS, params=params)
    if not response:
        click.echo("Employee not found.")
        return

    click.echo(f"Using endpoint: {matched_endpoint}")
    click.echo(response.text)


@click.group()
@click.pass_context
def hr(ctx: click.Context) -> None:
    """
    Manage HR operations.
    """
    ensure_logged_in(ctx)


@hr.command("time-off")
@click.option("--search_query", type=str, default="", help="Search query for time-off records.")
@click.pass_context
def time_off(ctx: click.Context, search_query: str) -> None:
    """
    Show time-off balances/requests.
    """
    api_client = get_authenticated_api_client(ctx.obj.oauth_token)
    first_page, matched_endpoint = find_paginated_first_success(
        client=api_client,
        endpoints=HR_TIME_OFF_ENDPOINTS,
        search_query=search_query,
    )

    if not first_page:
        click.echo("No time-off records found or no accessible time-off endpoint.")
        return

    click.echo(f"Using endpoint: {matched_endpoint}")
    for row in first_page:
        request_id = row.get("id") or row.get("_id") or "-"
        status = row.get("status") or "unknown"
        employee = row.get("employeeName") or row.get("employee") or "unknown"
        click.echo(f"- {request_id} | {employee} | {status}")


@hr.command("payroll")
@click.option("--search_query", type=str, default="", help="Search query for payroll summaries.")
@click.pass_context
def payroll(ctx: click.Context, search_query: str) -> None:
    """
    Show payroll summaries.
    """
    api_client = get_authenticated_api_client(ctx.obj.oauth_token)
    first_page, matched_endpoint = find_paginated_first_success(
        client=api_client,
        endpoints=HR_PAYROLL_ENDPOINTS,
        search_query=search_query,
    )

    if not first_page:
        click.echo("No payroll records found or no accessible payroll endpoint.")
        return

    click.echo(f"Using endpoint: {matched_endpoint}")
    for row in first_page:
        payroll_id = row.get("id") or row.get("_id") or "-"
        run_date = row.get("runDate") or row.get("payDate") or "-"
        status = row.get("status") or "-"
        click.echo(f"- {payroll_id} | {run_date} | {status}")


hr.add_command(employee)  # type: ignore
