# Citations & Export

## Export Citations

```bash
zot export ABC123                    # BibTeX (default)
zot export ABC123 --format csl-json  # CSL-JSON
zot export ABC123 --format ris       # RIS
zot export ABC123 --format json      # Raw JSON
```

## Format and Copy to Clipboard

```bash
zot cite ABC123                      # APA (default)
zot cite ABC123 --style nature       # Nature
zot cite ABC123 --style vancouver    # Vancouver
zot cite ABC123 --no-copy            # Print only, don't copy
```

The formatted citation is automatically copied to your clipboard.

## Supported Styles

| Style | Format |
|-------|--------|
| **APA** (default) | Author, A. B. (Year). Title. *Journal*, Volume(Issue), Pages. |
| **Nature** | Author, A. B. Title. *Journal* **Volume**, Pages (Year). |
| **Vancouver** | Author AB. Title. Journal. Year;Volume(Issue):Pages. |

## Batch Export via Workspace

For exporting multiple papers at once, use [workspace export](workspace.md):

```bash
zot workspace export my-project --format bibtex
```
