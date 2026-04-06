# PDF 提取

## 提取全文

```bash
zot pdf ABC123
```

从条目的 PDF 附件中提取文本。结果会缓存以加速后续访问。

## 提取指定页面

```bash
zot pdf ABC123 --pages 1-5     # 第 1 至 5 页
zot pdf ABC123 --pages 3       # 仅第 3 页
```

## 提取标注

```bash
zot pdf ABC123 --annotations
```

提取 PDF 中的高亮、批注和笔记，包含页码信息。

## 缓存管理

PDF 文本在首次提取后会本地缓存：

```bash
zot config cache stats    # 查看缓存大小
zot config cache clear    # 清除所有缓存
```

## 在系统查看器中打开 PDF

```bash
zot open ABC123
```

使用默认应用程序打开 PDF（如果没有 PDF 则打开 URL）。
