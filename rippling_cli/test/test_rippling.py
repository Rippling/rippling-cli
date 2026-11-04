from click.testing import CliRunner

from rippling_cli.cli import main


class TestRipplingCommand:

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main.cli, ['--help'])
        assert result.exit_code == 0
        assert result.output
