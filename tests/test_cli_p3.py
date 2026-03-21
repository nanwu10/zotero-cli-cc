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


def test_detail_minimal_flag():
    runner = CliRunner()
    result = runner.invoke(main, ["--detail", "minimal", "--help"])
    assert result.exit_code == 0


def test_detail_invalid_value():
    runner = CliRunner()
    result = runner.invoke(main, ["--detail", "invalid", "search", "test"])
    assert result.exit_code != 0


def test_profile_flag():
    runner = CliRunner()
    result = runner.invoke(main, ["--profile", "test", "--help"])
    assert result.exit_code == 0


def test_cache_clear_command():
    runner = CliRunner()
    result = runner.invoke(main, ["config", "cache", "clear"])
    assert result.exit_code == 0


def test_cache_stats_command():
    runner = CliRunner()
    result = runner.invoke(main, ["config", "cache", "stats"])
    assert result.exit_code == 0
    assert "Cached PDFs" in result.output


def test_profile_list_no_profiles():
    runner = CliRunner()
    result = runner.invoke(main, ["config", "profile", "list"])
    # Either shows profiles or says none configured
    assert result.exit_code == 0
