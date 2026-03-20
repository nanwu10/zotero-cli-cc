# zotero-cli-cc

[中文](#中文) | [English](#english)

---

<a id="中文"></a>

## 简介

`zotero-cli-cc` 是一个专为 [Claude Code](https://claude.ai/code) 设计的 Zotero 命令行工具。

**核心特性：**
- **读操作**：直接读取本地 SQLite 数据库，零配置、离线可用、毫秒级响应
- **写操作**：通过 Zotero Web API 安全写入，Zotero 完全感知变更
- **PDF 提取**：直接从本地存储提取 PDF 全文

**无需启动 Zotero 桌面端即可检索和阅读文献。**

## 安装

```bash
# 推荐
uv tool install zotero-cli-cc

# 或者
pip install zotero-cli-cc
```

## 配置

```bash
# 配置 Web API 凭证（仅写操作需要）
zot config init
```

读操作开箱即用，只要 Zotero 数据在默认目录（`~/Zotero`）。

写操作需要 API Key，在 https://www.zotero.org/settings/keys 获取。

## 命令一览

### 检索与浏览

```bash
# 全库搜索（标题、作者、标签、全文）
zot search "transformer attention"

# 按 collection 过滤搜索
zot search "BERT" --collection "NLP"

# 列出文献
zot list --collection "Machine Learning" --limit 10

# 查看文献详情（元数据 + 摘要 + 笔记）
zot read ABC123

# 查找相关文献
zot relate ABC123
```

### 笔记与标签

```bash
# 查看/添加笔记
zot note ABC123
zot note ABC123 --add "这篇论文提出了新的注意力机制"

# 查看/添加/删除标签
zot tag ABC123
zot tag ABC123 --add "重要"
zot tag ABC123 --remove "待读"
```

### 引用导出

```bash
zot export ABC123                  # BibTeX
zot export ABC123 --format json    # JSON
```

### 文献管理

```bash
zot add --doi "10.1038/s41586-023-06139-9"    # 通过 DOI 添加
zot add --url "https://arxiv.org/abs/2301.00001"  # 通过 URL 添加
zot delete ABC123 --yes                        # 删除（移入回收站）
```

### Collection 管理

```bash
zot collection list                # 列出所有 collection（树形展示）
zot collection items COLML01       # 查看 collection 内的文献
zot collection create "新项目"      # 创建新 collection
```

### AI 辅助功能

```bash
zot summarize ABC123               # 结构化摘要（专为 Claude Code 优化）
zot pdf ABC123                     # 提取 PDF 全文
zot pdf ABC123 --pages 1-5         # 提取指定页
```

### 全局选项

```bash
zot --json search "attention"      # JSON 输出
zot --limit 5 list                 # 限制结果数量
zot --version                      # 查看版本
```

## 架构

```
┌─────────────────────────────────┐
│        zot CLI (Click)          │
│  search │ list │ read │ ...     │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│        核心服务层                │
│  ZoteroReader  │  ZoteroWriter  │
│  (SQLite 只读) │  (Web API)     │
└───────┬────────┴────────┬───────┘
        │                 │
   ┌────▼────┐    ┌───────▼────────┐
   │ SQLite  │    │ Zotero Web API │
   │ (本地)   │    │ (远程)         │
   └─────────┘    └────────────────┘
        │
   ┌────▼──────────┐
   │ ~/Zotero/     │
   │ storage/*.pdf │
   └───────────────┘
```

## 在 Claude Code 中使用

在任何 Claude Code 会话中，直接用自然语言请求：

```
帮我搜索 Zotero 中关于 single cell 的论文
→ Claude 自动运行: zot --json search "single cell"

查看这篇论文的详情
→ Claude 自动运行: zot --json read ABC123

导出这篇论文的 BibTeX
→ Claude 自动运行: zot export ABC123
```

建议在 `~/.claude/CLAUDE.md` 中添加：

```markdown
### Zotero CLI
- 使用 `zot` 命令操作 Zotero（搜索、阅读、笔记、导出、添加、删除）
- 处理结果时使用 `--json` 标志
```

## 环境变量

| 变量 | 用途 |
|------|------|
| `ZOT_DATA_DIR` | 覆盖 Zotero 数据目录路径 |
| `ZOT_LIBRARY_ID` | 覆盖 Library ID（写操作） |
| `ZOT_API_KEY` | 覆盖 API Key（写操作） |

---

<a id="english"></a>

## English

`zotero-cli-cc` is a Zotero CLI designed for [Claude Code](https://claude.ai/code) — SQLite reads (offline, fast) + Web API writes (safe).

### Install

```bash
uv tool install zotero-cli-cc
# or
pip install zotero-cli-cc
```

### Setup

```bash
zot config init  # Configure API key (write operations only)
```

### Commands

| Command | Purpose |
|---------|---------|
| `zot search <query>` | Search library (title, author, tag, fulltext) |
| `zot list` | List items with filters |
| `zot read <key>` | View item details + notes |
| `zot note <key>` | View/add notes |
| `zot export <key>` | Export citation (BibTeX/JSON) |
| `zot add` | Add item by DOI or URL |
| `zot delete <key>` | Delete item (move to trash) |
| `zot tag <key>` | View/manage tags |
| `zot collection` | Manage collections |
| `zot summarize <key>` | Structured summary for AI consumption |
| `zot pdf <key>` | Extract PDF text |
| `zot relate <key>` | Find related items |
| `zot config` | Configuration management |

Global flags: `--json` (JSON output) · `--limit N` (limit results) · `--version`

---

## 支持作者 / Support

<table>
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/wechat-pay.png" width="180" alt="微信支付">
      <br>
      <b>微信支付</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/alipay.png" width="180" alt="支付宝">
      <br>
      <b>支付宝</b>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/Agents365-ai/images_payment/main/qrcode/buymeacoffee.png" width="180" alt="Buy Me a Coffee">
      <br>
      <b>Buy Me a Coffee</b>
    </td>
  </tr>
</table>

## 许可证 / License

[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — 免费用于非商业用途 / Free for non-commercial use.
