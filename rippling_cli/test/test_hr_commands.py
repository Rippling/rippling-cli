from unittest.mock import Mock, patch

from click.testing import CliRunner

from rippling_cli.cli import main


def setup_auth_mocks() -> tuple[patch, patch]:
    token_patch = patch("rippling_cli.cli.main.get_oauth_token_data", return_value={"token": "fake-token"})
    expiry_patch = patch("rippling_cli.cli.main.OAuthToken.is_token_expired", return_value=False)
    return token_patch, expiry_patch


class TestHrCommands:
    def test_hr_help(self):
        runner = CliRunner()
        token_patch, expiry_patch = setup_auth_mocks()
        with token_patch, expiry_patch, patch("rippling_cli.cli.commands.hr.hr.ensure_logged_in", return_value=None):
            result = runner.invoke(main.cli, ["hr", "--help"])
        assert result.exit_code == 0
        assert "time-off" in result.output
        assert "payroll" in result.output
        assert "employee" in result.output

    def test_employee_get_requires_identifier(self):
        runner = CliRunner()
        token_patch, expiry_patch = setup_auth_mocks()
        with token_patch, expiry_patch, patch("rippling_cli.cli.commands.hr.hr.ensure_logged_in", return_value=None):
            result = runner.invoke(main.cli, ["hr", "employee", "get"])
        assert result.exit_code == 0
        assert "Provide either --employee_id or --email." in result.output

    def test_employee_list_success(self):
        runner = CliRunner()
        token_patch, expiry_patch = setup_auth_mocks()
        with (
            token_patch,
            expiry_patch,
            patch("rippling_cli.cli.commands.hr.hr.ensure_logged_in", return_value=None),
            patch("rippling_cli.cli.commands.hr.hr.get_authenticated_api_client", return_value=Mock()),
            patch(
                "rippling_cli.cli.commands.hr.hr.find_paginated_first_success",
                return_value=([{"id": "emp_123", "fullName": "Test Employee", "workEmail": "test@example.com"}], "/api/hub/api/employment_roles_with_company"),
            ),
        ):
            result = runner.invoke(main.cli, ["hr", "employee", "list"])
        assert result.exit_code == 0
        assert "Using endpoint: /api/hub/api/employment_roles_with_company" in result.output
        assert "Test Employee" in result.output
