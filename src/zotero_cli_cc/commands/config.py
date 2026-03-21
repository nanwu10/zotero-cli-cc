from __future__ import annotations

from pathlib import Path

import click

from zotero_cli_cc.config import AppConfig, load_config, save_config, CONFIG_FILE


@click.group("config")
def config_group() -> None:
    """Manage zot configuration."""
    pass


@config_group.command("init")
@click.option("--config-path", type=click.Path(), default=None, help="Config file path")
@click.option("--library-id", default=None, help="Zotero library ID")
@click.option("--api-key", default=None, help="Zotero API key")
@click.pass_context
def config_init(ctx: click.Context, config_path: str | None, library_id: str | None, api_key: str | None) -> None:
    """Initialize configuration interactively."""
    path = Path(config_path) if config_path else CONFIG_FILE
    no_interaction = ctx.obj.get("no_interaction", False) if ctx.obj else False
    json_out = ctx.obj.get("json", False) if ctx.obj else False
    if no_interaction:
        if not library_id or not api_key:
            from zotero_cli_cc.models import ErrorInfo
            from zotero_cli_cc.formatter import format_error
            click.echo(format_error(
                ErrorInfo(
                    message="--library-id and --api-key required with --no-interaction",
                    context="config init",
                    hint="Provide --library-id and --api-key, or run without --no-interaction",
                ),
                output_json=json_out,
            ))
            ctx.exit(1)
            return
    else:
        library_id = library_id or click.prompt("Zotero library ID")
        api_key = api_key or click.prompt("Zotero API key")
    cfg = AppConfig(library_id=library_id, api_key=api_key)
    save_config(cfg, path)
    click.echo(f"Configuration saved to {path}")


@config_group.command("show")
@click.option("--config-path", type=click.Path(), default=None, help="Config file path")
def config_show(config_path: str | None) -> None:
    """Show current configuration."""
    path = Path(config_path) if config_path else CONFIG_FILE
    cfg = load_config(path)
    click.echo(f"Library ID: {cfg.library_id}")
    click.echo(f"API Key:    {'***' + cfg.api_key[-4:] if len(cfg.api_key) > 4 else '(not set)'}")
    click.echo(f"Data Dir:   {cfg.data_dir or '(auto-detect)'}")
    click.echo(f"Format:     {cfg.default_format}")
    click.echo(f"Limit:      {cfg.default_limit}")
    click.echo(f"Export:     {cfg.default_export_style}")
