from pathlib import Path

import click

from rippling_cli.utils.hr_reports_utils import (
    REPORTS_EXPORT_ENDPOINTS,
    REPORTS_LIST_ENDPOINTS,
    REPORTS_RUN_ENDPOINTS,
    get_authenticated_api_client,
    get_first_success,
    parse_json_option,
    post_first_success,
)
from rippling_cli.utils.login_utils import ensure_logged_in


@click.group()
@click.pass_context
def reports(ctx: click.Context) -> None:
    """
    Manage reports operations.
    """
    ensure_logged_in(ctx)


@reports.command("list")
@click.option("--search_query", type=str, default="", help="Search query for reports.")
@click.pass_context
def list_reports(ctx: click.Context, search_query: str) -> None:
    """
    List available reports.
    """
    api_client = get_authenticated_api_client(ctx.obj.oauth_token)
    params = {"searchQuery": search_query} if search_query else None
    response, matched_endpoint = get_first_success(api_client, REPORTS_LIST_ENDPOINTS, params=params)

    if not response:
        click.echo("No reports found or no accessible reports endpoint.")
        return

    click.echo(f"Using endpoint: {matched_endpoint}")
    rows = response.json() if response.text else []
    if not isinstance(rows, list):
        rows = rows.get("data", [])

    for row in rows:
        report_id = row.get("id") or row.get("_id") or "-"
        name = row.get("name") or row.get("title") or "Unnamed report"
        click.echo(f"- {name} ({report_id})")


@reports.command("run")
@click.option("--report_id", required=True, type=str, help="Report identifier.")
@click.option(
    "--params_json",
    required=False,
    type=str,
    help='JSON object parameters, e.g. \'{"startDate":"2026-01-01"}\'',
)
@click.pass_context
def run_report(ctx: click.Context, report_id: str, params_json: str) -> None:
    """
    Run report and print response.
    """
    try:
        parsed_params = parse_json_option(params_json, "params_json")
    except ValueError as error:
        click.echo(str(error))
        return

    api_client = get_authenticated_api_client(ctx.obj.oauth_token)
    payload = {"reportId": report_id, "parameters": parsed_params or {}}
    response, matched_endpoint = post_first_success(api_client, REPORTS_RUN_ENDPOINTS, payload=payload)

    if not response:
        click.echo("Failed to run report or no accessible run endpoint.")
        return

    click.echo(f"Using endpoint: {matched_endpoint}")
    click.echo(response.text)


@reports.command("export")
@click.option("--report_id", required=True, type=str, help="Report identifier.")
@click.option("--format", "output_format", type=click.Choice(["csv", "json"]), default="csv", show_default=True)
@click.option("--output", required=True, type=str, help="Output file path.")
@click.option(
    "--params_json",
    required=False,
    type=str,
    help='JSON object parameters, e.g. \'{"startDate":"2026-01-01"}\'',
)
@click.pass_context
def export_report(ctx: click.Context, report_id: str, output_format: str, output: str, params_json: str) -> None:
    """
    Export report to CSV or JSON.
    """
    try:
        parsed_params = parse_json_option(params_json, "params_json")
    except ValueError as error:
        click.echo(str(error))
        return

    payload = {
        "reportId": report_id,
        "format": output_format,
        "parameters": parsed_params or {},
    }

    api_client = get_authenticated_api_client(ctx.obj.oauth_token)
    response, matched_endpoint = post_first_success(api_client, REPORTS_EXPORT_ENDPOINTS, payload=payload)

    if not response:
        click.echo("Failed to export report or no accessible export endpoint.")
        return

    output_path = Path(output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = response.text if output_format == "json" else response.content

    write_mode = "w" if output_format == "json" else "wb"
    with output_path.open(write_mode) as file_handle:
        file_handle.write(content)

    click.echo(f"Using endpoint: {matched_endpoint}")
    click.echo(f"Report exported to {output_path}")
