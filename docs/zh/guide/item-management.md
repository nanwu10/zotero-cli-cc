# 条目管理

## 通过 DOI 添加

```bash
zot add --doi "10.1038/s41586-023-06139-9"
```

## 通过 URL 添加

```bash
zot add --url "https://arxiv.org/abs/2301.00001"
```

## 从本地 PDF 添加

```bash
zot add --pdf paper.pdf
```

从 PDF 中提取 DOI，创建条目并附加文件。

## 批量导入

```bash
zot add --from-file dois.txt
```

文件中每行一个 DOI 或 URL。

## 更新元数据

```bash
zot update ABC123 --title "Corrected Title"
zot update ABC123 --date "2024-01-15"
zot update ABC123 --field publicationTitle="Nature"
```

## 删除条目

```bash
zot delete ABC123                 # 确认提示
zot delete ABC123 --yes           # 跳过确认
zot --no-interaction delete ABC123  # 脚本模式
```

条目会移到 Zotero 回收站，不会被永久删除。

## 回收站管理

```bash
zot trash list                    # 查看回收站条目
zot trash restore ABC123          # 从回收站恢复
```

## 上传附件

```bash
zot attach ABC123 --file supplementary.pdf
```

## 查找重复

```bash
zot duplicates                         # DOI + 标题匹配
zot duplicates --by doi                # 仅 DOI
zot duplicates --by title              # 模糊标题匹配
zot duplicates --threshold 0.9         # 更严格的匹配
```
