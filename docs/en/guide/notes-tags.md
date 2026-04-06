# Notes & Tags

## View Notes

```bash
zot note ABC123
```

Displays all notes attached to an item, converted from HTML to Markdown.

## Add a Note

```bash
zot note ABC123 --add "This paper proposes a new attention mechanism"
```

!!! note "Write operations require API credentials"
    See [Setup](../getting-started/setup.md#api-credentials) to configure your API key.

## Update a Note

Notes can be updated via the MCP tools (`note_update`). See [MCP Tools Reference](../mcp/tools.md).

## View Tags

```bash
zot tag ABC123
```

## Add Tags

```bash
zot tag ABC123 --add "important"
zot tag ABC123 --add "to-read" --add "attention"
```

## Remove Tags

```bash
zot tag ABC123 --remove "to-read"
```

## Batch Tag Operations

Tags can be added to or removed from multiple items at once via MCP tools (`tag_add`, `tag_remove`). See [MCP Tools Reference](../mcp/tools.md).
