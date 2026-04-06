# Preprint Status Check

Check if arXiv, bioRxiv, or medRxiv preprints have been formally published.

## Dry Run (Default)

```bash
zot update-status
```

Checks all preprints in your library and shows which have been published, without making changes.

## Check a Single Item

```bash
zot update-status ABC123
```

## Check by Collection

```bash
zot update-status --collection "scRNA-seq" --limit 20
```

## Apply Updates

```bash
zot update-status --apply
```

Updates Zotero metadata (DOI, journal, date) for published items via Web API.

## API Key

Uses the [Semantic Scholar API](https://www.semanticscholar.org/product/api). Without an API key, requests are rate-limited (~1 per 3 seconds). Set a key for faster queries:

```bash
export S2_API_KEY=your_key_here
```

Apply for a free key at [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api#api-key-form).
