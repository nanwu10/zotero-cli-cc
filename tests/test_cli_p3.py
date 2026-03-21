from click.testing import CliRunner
from zotero_cli_cc.cli import main


def test_no_interaction_flag_exists():
    runner = CliRunner()
    result = runner.invoke(main, ["--no-interaction", "--help"])
    assert result.exit_code == 0


def test_delete_no_interaction_skips_prompt():
    """--no-interaction should auto-confirm delete without prompting."""
    runner = CliRunner()
    # Will fail at credentials check, but should NOT prompt for confirmation
    result = runner.invoke(main, ["--no-interaction", "delete", "FAKEKEY"])
    assert "Cancelled" not in result.output


def test_config_init_no_interaction_requires_options(tmp_path):
    """--no-interaction + config init without args should error."""
    runner = CliRunner()
    result = runner.invoke(main, ["--no-interaction", "config", "init",
                                   "--config-path", str(tmp_path / "config.toml")])
    assert "required" in result.output.lower() or "error" in result.output.lower()


def test_config_init_no_interaction_with_options(tmp_path):
    """--no-interaction + config init with all args should succeed."""
    config_file = tmp_path / "config.toml"
    runner = CliRunner()
    result = runner.invoke(main, ["--no-interaction", "config", "init",
                                   "--config-path", str(config_file),
                                   "--library-id", "123",
                                   "--api-key", "abc"])
    assert "saved" in result.output.lower()
    assert config_file.exists()
