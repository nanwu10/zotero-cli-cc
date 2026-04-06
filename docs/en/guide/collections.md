# Collections

## List Collections

```bash
zot collection list
```

Displays all collections in a tree view showing parent-child relationships.

## View Collection Items

```bash
zot collection items COLKEY01
```

## Create a Collection

```bash
zot collection create "New Project"
```

## Move Item to Collection

```bash
zot collection move ITEMKEY COLKEY
```

## Rename a Collection

```bash
zot collection rename COLKEY "Better Name"
```

## Delete a Collection

```bash
zot collection delete COLKEY --yes
```

## Batch Reorganize

Reorganize items into new collections using a JSON plan:

```bash
zot collection reorganize plan.json
```

Example `plan.json`:

```json
{
  "collections": [
    {
      "name": "Transformers",
      "items": ["KEY1", "KEY2", "KEY3"]
    },
    {
      "name": "Self-Attention",
      "parent": "Transformers",
      "items": ["KEY4", "KEY5"]
    }
  ]
}
```
