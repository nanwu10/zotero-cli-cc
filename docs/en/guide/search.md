# Search & Browse

## How Search Works

`zot search` matches keywords across four layers:

1. **Titles & abstracts** — direct text match
2. **Author names** — first and last name matching
3. **Tags** — exact tag matching
4. **PDF fulltext index** — Zotero's built-in fulltext index

For deeper content search with BM25 ranking and optional semantic matching, use [workspace query](workspace.md).

## Basic Search

```bash
zot search "transformer attention"
```

## Filter by Collection

```bash
zot search "BERT" --collection "NLP"
```

## Filter by Item Type

```bash
zot search "protein" --type journalArticle
```

Common types: `journalArticle`, `conferencePaper`, `preprint`, `book`, `bookSection`, `thesis`

## Sort Results

```bash
zot search "attention" --sort dateAdded --direction desc
zot search "attention" --sort title --direction asc
```

Sort fields: `dateAdded`, `dateModified`, `title`, `creator`

## List All Items

```bash
zot list --limit 20
zot list --collection "Machine Learning"
```

## Recently Added Items

```bash
zot recent                    # Last 7 days (default)
zot recent --days 30          # Last 30 days
zot recent --days 7 --modified  # Recently modified
```

## View Item Details

```bash
zot read ABC123
```

Shows metadata, abstract, and notes. Use `--detail full` for extra fields.

## Find Related Items

```bash
zot relate ABC123
```

Finds items sharing tags, collections, or explicit relations.

## Detail Levels

```bash
zot --detail minimal search "attention"   # Key, title, authors, year only
zot --detail standard read ABC123         # Default — includes abstract, tags, DOI
zot --detail full read ABC123             # All fields including extra metadata
```

## JSON Output

```bash
zot --json search "attention"
```

All commands support `--json` for machine-readable output.

## Library Statistics

```bash
zot stats
```

Shows total items, PDFs, notes, breakdown by type, collections, and top tags.
