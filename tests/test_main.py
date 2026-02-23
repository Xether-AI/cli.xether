import pytest
from typer.testing import CliRunner
from xether_cli.main import app

runner = CliRunner()

def test_info_command():
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "Xether AI CLI" in result.stdout
