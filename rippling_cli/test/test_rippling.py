from pathlib import Path

import certifi
from click.testing import CliRunner

from rippling_cli.cli import main

# DEFVULN-51432: 2024.2.2 still trusts emSign ECC Root CA - G3.
COMPROMISED_EMUDHRA_ROOT = "emSign ECC Root CA - G3"


class TestRipplingCommand:

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main.cli, ['--help'])
        assert result.exit_code == 0
        assert result.output


def test_certifi_bundle_drops_compromised_emudhra_root():
    bundle = Path(certifi.where()).read_text()
    assert certifi.__version__ == "2026.10.19"
    assert COMPROMISED_EMUDHRA_ROOT not in bundle
    assert "GlobalSign Root CA" in bundle
