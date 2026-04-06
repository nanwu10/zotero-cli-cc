# Using with Claude Code

## Install the Skill

Copy the zotero-cli-cc skill so Claude Code automatically recognizes literature-related requests:

```bash
cp -r skill/zotero-cli-cc ~/.claude/skills/
```

## How It Works

With the skill installed, Claude Code automatically uses `zot` commands when you ask about papers:

```
Search my Zotero for single cell papers
→ Claude runs: zot --json search "single cell"

Show me details of this paper
→ Claude runs: zot --json read ABC123

Export BibTeX for these papers
→ Claude runs: zot export ABC123

Create a workspace for my ICML submission
→ Claude runs: zot workspace new icml-2026 --description "ICML 2026 submission"
```

## Workspace + RAG Workflow

A typical research workflow with Claude Code:

1. **Create a workspace** for your project
2. **Import papers** from collections, tags, or search
3. **Build the RAG index** for semantic search
4. **Query** the workspace with natural language

```
Create a workspace called "llm-safety" and import all papers tagged "alignment"
→ Claude creates workspace and imports items

Index the workspace
→ Claude runs: zot workspace index llm-safety

What methods do these papers use for reward hacking detection?
→ Claude queries the workspace RAG index and synthesizes an answer
```

## Shell Completions

Enable tab completions for faster CLI use:

=== "Zsh"

    ```bash
    zot completions zsh >> ~/.zshrc
    ```

=== "Bash"

    ```bash
    zot completions bash >> ~/.bashrc
    ```

=== "Fish"

    ```bash
    zot completions fish > ~/.config/fish/completions/zot.fish
    ```
