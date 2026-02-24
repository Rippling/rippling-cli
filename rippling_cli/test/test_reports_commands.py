from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner

from rippling_cli.cli import main


def setup_auth_mocks() -> tuple[patch, patch]:
    token_patch = patch("rippling_cli.cli.main.get_oauth_token_data", return_value={"token": "fake-token"})
    expiry_patch = patch("rippling_cli.cli.main.OAuthToken.is_token_expired", return_value=False)
    return token_patch, expiry_patch


class FakeResponse:
    def __init__(self, text: str = "", content: bytes = b"", json_payload: list | dict | None = None):
        self.text = text
        self.content = content
        self._json_payload = json_payload if json_payload is not None else []

    def json(self):
        return self._json_payload


class TestReportsCommands:
    def test_reports_help(self):
        runner = CliRunner()
        token_patch, expiry_patch = setup_auth_mocks()
        with token_patch, expiry_patch, patch(
            "rippling_cli.cli.commands.reports.reports.ensure_logged_in", return_value=None
        ):
            result = runner.invoke(main.cli, ["reports", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "run" in result.output
        assert "export" in result.output

    def test_run_rejects_invalid_json_params(self):
        runner = CliRunner()
        token_patch, expiry_patch = setup_auth_mocks()
        with token_patch, expiry_patch, patch(
            "rippling_cli.cli.commands.reports.reports.ensure_logged_in", return_value=None
        ):
            result = runner.invoke(main.cli, ["reports", "run", "--report_id", "rep_1", "--params_json", "not-json"])
        assert result.exit_code == 0
        assert "Expecting value" in result.output

    def test_export_json_success(self):
        runner = CliRunner()
        token_patch, expiry_patch = setup_auth_mocks()
        with runner.isolated_filesystem():
            output_file = "reports/output.json"
            with (
                token_patch,
                expiry_patch,
                patch("rippling_cli.cli.commands.reports.reports.ensure_logged_in", return_value=None),
                patch("rippling_cli.cli.commands.reports.reports.get_authenticated_api_client", return_value=Mock()),
                patch(
                    "rippling_cli.cli.commands.reports.reports.post_first_success",
                    return_value=(FakeResponse(text='{"ok": true}', json_payload={"ok": True}), "/api/reports/api/reports/export"),
                ),
            ):
                result = runner.invoke(
                    main.cli,
                    ["reports", "export", "--report_id", "rep_1", "--format", "json", "--output", output_file],
                )
            assert result.exit_code == 0
            assert "Report exported to" in result.output
            assert Path(output_file).exists()
