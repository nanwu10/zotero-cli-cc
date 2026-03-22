# MCP Server Layer for zotero-cli-cc

## Problem

zotero-cli-cc is a CLI tool only. Users of MCP-compatible clients (LM Studio, Claude Desktop, Cursor, Continue) cannot use it. Adding an MCP server layer makes the tool accessible to any MCP client with zero code changes on the client side.

## Architecture

A thin MCP server module wraps the existing core modules. No logic duplication — the server calls the same `ZoteroReader`, `ZoteroWriter`, `PdfExtractor`, and `PdfCache` that the CLI uses.

```
MCP Client (LM Studio, Claude Desktop, Cursor, etc.)
    | stdio (JSON-RPC)
MCP Server (mcp_server.py)
    | direct Python calls
Core modules (reader.py, writer.py, pdf_extractor.py, pdf_cache.py)
    |
SQLite (reads) / Zotero Web API (writes)
```

## Transport

stdio only. This is the standard for local MCP servers and covers all major clients.

## SDK

Official `mcp` Python SDK (from Anthropic). Well-maintained, handles protocol details.

## Files

| File | Purpose |
|------|---------|
| `src/zotero_cli_cc/mcp_server.py` | MCP server with all tool handlers |
| `src/zotero_cli_cc/commands/mcp.py` | `zot mcp serve` CLI subcommand |
| `tests/test_mcp_server.py` | Tool handler unit tests |

## Dependencies

Add `mcp` as optional dependency in `pyproject.toml`:

```toml
[project.optional-dependencies]
mcp = ["mcp>=1.0"]
```

Install: `pip install zotero-cli-cc[mcp]` or `uv pip install zotero-cli-cc[mcp]`

## MCP Tools (17 tools)

All tools return structured JSON-serializable dicts/lists, not formatted text.

### Read Operations (zero-config, offline)

| Tool | Parameters | Returns |
|------|-----------|---------|
| `search` | `query: str`, `collection?: str`, `limit?: int` | `{items: [...], total: int, query: str}` |
| `list_items` | `collection?: str`, `limit?: int` | `{items: [...], total: int}` |
| `read` | `key: str`, `detail?: str` | `{item: {...}, notes: [...]}` |
| `pdf` | `key: str`, `pages?: str` | `{text: str, pages: str}` |
| `summarize` | `key: str` | `{summary: {...}}` |
| `export` | `key: str`, `format?: str` | `{citation: str, format: str}` |
| `relate` | `key: str`, `limit?: int` | `{items: [...]}` |
| `note_view` | `key: str` | `{notes: [...]}` |
| `tag_view` | `key: str` | `{tags: [...]}` |
| `collection_list` | — | `{collections: [...]}` |
| `collection_items` | `key: str` | `{items: [...]}` |

### Write Operations (requires API credentials)

| Tool | Parameters | Returns |
|------|-----------|---------|
| `note_add` | `key: str`, `content: str` | `{note_key: str}` |
| `tag_add` | `key: str`, `tags: list[str]` | `{success: true}` |
| `tag_remove` | `key: str`, `tags: list[str]` | `{success: true}` |
| `add` | `doi?: str`, `url?: str` | `{item_key: str}` |
| `delete` | `key: str` | `{success: true}` |
| `collection_create` | `name: str`, `parent?: str` | `{collection_key: str}` |

## Configuration

Reuses existing `AppConfig` from `config.py`. No separate MCP configuration needed. The server reads the same `~/.config/zot/config.toml` and respects the same environment variables (`ZOT_DATA_DIR`, `ZOT_LIBRARY_ID`, `ZOT_API_KEY`, `ZOT_PROFILE`).

## Error Handling

Errors are returned as MCP error responses preserving the existing `ErrorInfo` structure:

```json
{
  "error": "Item 'ABC123' not found",
  "context": "read",
  "hint": "Run search tool to find valid item keys"
}
```

Write operations that fail due to missing credentials return a clear error with setup instructions.

## Server Lifecycle

- Stateless: creates `ZoteroReader`/`ZoteroWriter` instances as needed
- No background tasks or persistent connections
- Graceful shutdown on stdio close

## CLI Integration

New `mcp` command group under the existing CLI:

```bash
zot mcp serve    # Start MCP server on stdio
```

## Client Configuration

### LM Studio / Claude Desktop

```json
{
  "mcpServers": {
    "zotero": {
      "command": "zot",
      "args": ["mcp", "serve"]
    }
  }
}
```

### Cursor

```json
{
  "mcpServers": {
    "zotero": {
      "command": "zot",
      "args": ["mcp", "serve"]
    }
  }
}
```

## Testing Strategy

Unit tests for each tool handler using mocked `ZoteroReader`/`ZoteroWriter`. Tests verify:

1. Correct parameters are passed to core modules
2. Return values are properly structured
3. Errors are handled and formatted correctly
4. Missing optional parameters use defaults
