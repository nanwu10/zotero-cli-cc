# zotero-cli-cc Design Spec

**Date**: 2026-03-20
**Status**: Approved

## Overview

`zotero-cli-cc` is a Python CLI tool that provides full bidirectional interaction with Zotero from within Claude Code. It uses a hybrid data strategy: SQLite for reads (fast, offline, zero-config) and Zotero Web API for writes (safe, Zotero-aware).

**Package name**: `zotero-cli-cc`
**CLI entry point**: `zot`

## Market Analysis

No existing tool fills this niche:

| Tool | Stars | Approach | Gap |
|------|-------|----------|-----|
| pyzotero-cli | 11 | Web API only | Needs API key for reads, no SQLite |
| jbaiter/zotero-cli | 311 | Web API only | Unmaintained (2019), minimal features |
| dhondta/zotero-cli | 72 | Web API only | Read-only, no CRUD |
| pyzotero (lib) | 1200+ | Web API + Local API | Library, not CLI; Local API read-only |

**No tool uses SQLite reads + Web API writes. No tool is designed for Claude Code integration.**

## Architecture

```
┌─────────────────────────────────────┐
│           zot CLI (Click)           │
│  search │ list │ read │ note │ ...  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│          Core Service Layer         │
│  ZoteroReader  │  ZoteroWriter      │
│  (SQLite)      │  (pyzotero/WebAPI) │
└───────┬────────┴────────┬───────────┘
        │                 │
   ┌────▼────┐    ┌───────▼────────┐
   │ SQLite  │    │ Zotero Web API │
   │ (local) │    │ (api.zotero.org)│
   └─────────┘    └────────────────┘
        │
   ┌────▼──────────┐
   │ ~/Zotero/     │
   │ storage/*.pdf │
   └───────────────┘
```

### Layers

- **CLI layer**: `click` framework. Parses arguments, formats output (table/JSON).
- **Service layer**:
  - `ZoteroReader` — SQLite queries for all read operations
  - `ZoteroWriter` — `pyzotero` Web API calls for all write operations
- **Config**: `~/.config/zot/config.toml`

## Command Interface

```
zot <command> [subcommand] [options]
```

### Global flags

- `--json` — JSON output (default: human-readable table)
- `--limit N` — limit results
- `--verbose` — verbose output

### Commands

| Command | Purpose | Data path | Example |
|---------|---------|-----------|---------|
| `zot search <query>` | Full-library search (title/author/tag/fulltext) | SQLite | `zot search "transformer attention"` |
| `zot list` | List items with filters | SQLite | `zot list --collection "ML" --limit 20` |
| `zot read <key>` | View item details (metadata + abstract + notes) | SQLite | `zot read ABC123` |
| `zot note <key>` | Note operations | Read: SQLite / Write: Web API | `zot note ABC123 --add "..."` |
| `zot export <key>` | Export citation | SQLite | `zot export ABC123 --format bibtex` |
| `zot add` | Add item | Web API | `zot add --doi "10.1234/..."` |
| `zot delete <key>` | Delete item (with confirmation) | Web API | `zot delete ABC123` |
| `zot tag <key>` | Manage tags | Read: SQLite / Write: Web API | `zot tag ABC123 --add "important"` |
| `zot collection` | Manage collections | Read: SQLite / Write: Web API | `zot collection create "New Project"` |
| `zot summarize <key>` | Structured summary output | SQLite | `zot summarize ABC123` |
| `zot pdf <key>` | Extract PDF text | Local filesystem | `zot pdf ABC123 --pages 1-5` |
| `zot relate <key>` | Find related items | SQLite | `zot relate ABC123` |
| `zot config` | Configuration management | Local | `zot config init` |

### Priority

- **P0**: search, list, read, note, export
- **P1**: add, delete, tag, collection, summarize
- **P2**: pdf, relate

## Data Layer

### ZoteroReader (SQLite)

Zotero uses an EAV model. Core query pattern:

```sql
SELECT i.key, iv.value AS title, ...
FROM items i
JOIN itemData id ON i.itemID = id.itemID
JOIN itemDataValues iv ON id.valueID = iv.valueID
JOIN fields f ON id.fieldID = f.fieldID
WHERE f.fieldName = 'title'
```

Key methods:
- `search(query, fields=['title','creator','tag','fulltext'])` — cross-table fuzzy search
- `get_item(key)` → full metadata dict
- `get_notes(key)` → note list (HTML → Markdown conversion)
- `get_collections()` → tree structure
- `get_attachments(key)` → attachment path list
- `export_citation(key, format)` → generate BibTeX/APA/Nature etc. from metadata

SQLite path auto-detection:
1. Config file override
2. `~/Zotero/zotero.sqlite` (macOS/Linux)
3. `%APPDATA%\Zotero\zotero.sqlite` (Windows)

Connection: **read-only** — `sqlite3.connect("file:...?mode=ro", uri=True)`

### ZoteroWriter (Web API via pyzotero)

```python
from pyzotero import zotero
zot = zotero.Zotero(library_id, 'user', api_key)
```

Key methods:
- `add_item(doi=None, url=None, manual=None)` — auto-populate metadata via DOI
- `delete_item(key, confirm=True)` — move to trash
- `add_note(key, content)` / `update_note(note_key, content)`
- `add_tags(key, tags)` / `remove_tags(key, tags)`
- `create_collection(name, parent=None)` / `move_to_collection(key, collection)`

### PDF Extraction

Read PDF files from `~/Zotero/storage/<key>/`, extract text with `pymupdf`.

```python
def extract_pdf(key, pages=None):
    pdf_path = find_pdf_in_storage(key)
    doc = pymupdf.open(pdf_path)
    # Extract by page, support page range filtering
```

## Configuration

### File: `~/.config/zot/config.toml`

```toml
[zotero]
data_dir = "~/Zotero"
library_id = "12345678"
api_key = "xxxxxxxxxxxxxxxx"

[output]
default_format = "table"
limit = 50

[export]
default_style = "bibtex"
```

First run: `zot config init` guides setup (API key + library ID).

## Project Structure

```
zotero-cli-cc/
├── pyproject.toml
├── src/
│   └── zotero_cli_cc/
│       ├── __init__.py
│       ├── cli.py                 # Click command entry point
│       ├── commands/              # One file per command
│       │   ├── search.py
│       │   ├── list.py
│       │   ├── read.py
│       │   ├── note.py
│       │   ├── export.py
│       │   ├── add.py
│       │   ├── delete.py
│       │   ├── tag.py
│       │   ├── collection.py
│       │   ├── summarize.py
│       │   ├── pdf.py
│       │   ├── relate.py
│       │   └── config.py
│       ├── core/
│       │   ├── reader.py          # ZoteroReader (SQLite)
│       │   ├── writer.py          # ZoteroWriter (Web API)
│       │   └── pdf_extractor.py   # PDF text extraction
│       ├── models.py              # Data models (dataclasses)
│       ├── config.py              # Config load/save
│       └── formatter.py           # Output formatting (table/json)
├── tests/
└── README.md
```

## Dependencies

```
click          # CLI framework
pyzotero       # Web API writes
pymupdf        # PDF text extraction
rich           # Table/pretty print
tomli          # Config reading (Python <3.11 compat)
```

Package manager: `uv`
Install: `uv tool install zotero-cli-cc` or `pip install zotero-cli-cc`

## Error Handling

### SQLite Safety

- Always open in **read-only mode** (`?mode=ro`)
- Detect Zotero DB lock — retry up to 3 times (1s interval)
- Schema version check: read `version` table, warn on mismatch

### Web API Failures

- API key not configured → reads work, writes prompt `zot config init`
- Network unavailable → clear error: "Write operations require network"
- Rate limit → automatic backoff retry

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Item has no PDF | `zot pdf` returns clear message, no crash |
| Notes contain HTML | Convert to Markdown on read |
| Nested collections | Tree display, path-style access `"ML/Transformers"` |
| Duplicate DOI | Detect and warn |
| Errors in `--json` mode | JSON error format `{"error": "..."}` |
| DB file not found | Guide user to check data directory config |
