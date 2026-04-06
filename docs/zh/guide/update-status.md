# 预印本状态检查

检查 arXiv、bioRxiv 或 medRxiv 预印本是否已正式发表。

## 试运行（默认）

```bash
zot update-status
```

检查文献库中的所有预印本，显示哪些已发表，但不做任何修改。

## 检查单个条目

```bash
zot update-status ABC123
```

## 按集合检查

```bash
zot update-status --collection "scRNA-seq" --limit 20
```

## 应用更新

```bash
zot update-status --apply
```

通过 Web API 更新已发表条目的 Zotero 元数据（DOI、期刊、日期）。

## API 密钥

使用 [Semantic Scholar API](https://www.semanticscholar.org/product/api)。无 API 密钥时请求频率受限（约每 3 秒 1 次）。设置密钥以加快查询速度：

```bash
export S2_API_KEY=your_key_here
```

在 [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api#api-key-form) 申请免费密钥。
