# Installation

## Requirements

- Python 3.10 or later
- A local Zotero installation (for the SQLite database)

## Install

=== "uv (recommended)"

    ```bash
    uv tool install zotero-cli-cc
    ```

=== "pipx"

    ```bash
    pipx install zotero-cli-cc
    ```

=== "pip"

    ```bash
    pip install zotero-cli-cc
    ```

## Upgrade

=== "uv"

    ```bash
    uv tool upgrade zotero-cli-cc
    ```

=== "pipx"

    ```bash
    pipx upgrade zotero-cli-cc
    ```

=== "pip"

    ```bash
    pip install -U zotero-cli-cc
    ```

## MCP Support

To use zotero-cli-cc as an MCP server (for Claude Desktop, Cursor, LM Studio):

```bash
pip install zotero-cli-cc[mcp]
```

## Verify Installation

```bash
zot --version
```
