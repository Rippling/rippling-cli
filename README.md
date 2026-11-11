# rippling-cli
The Rippling Command Line Interface (Rippling CLI) is a unified tool to programmatically invoke Rippling services. The Flux commands as part of the Rippling CLI allow both first-party and third-party App developers to create, manage and deploy Rippling-hosted integrations. 

## Command groups

- `rippling login` / `rippling logout`
- `rippling flux ...` for app + build workflows
- `rippling hr ...` for employee directory, time-off, and payroll summaries
- `rippling reports ...` for reports list, run, and export workflows

## HR commands

### Employee directory

- `rippling hr employee list --search_query "<name or email>"`
- `rippling hr employee get --employee_id <id>`
- `rippling hr employee get --email <work-email>`

### Time-off and payroll

- `rippling hr time-off --search_query "<query>"`
- `rippling hr payroll --search_query "<query>"`

## Reports commands

- `rippling reports list --search_query "<query>"`
- `rippling reports run --report_id <report-id> --params_json '{"startDate":"2026-01-01","endDate":"2026-01-31"}'`
- `rippling reports export --report_id <report-id> --format csv --output ./report.csv`
- `rippling reports export --report_id <report-id> --format json --output ./report.json`

Notes:

- HR/Reports use authenticated internal endpoints and role/company-scoped headers where available.
- If an endpoint is unavailable in your org, commands will print a clear fallback error.

## Testing

Run tests:

```bash
poetry run pytest
```
