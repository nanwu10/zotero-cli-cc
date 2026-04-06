# 集合

## 列出集合

```bash
zot collection list
```

以树形视图显示所有集合及其父子关系。

## 查看集合中的条目

```bash
zot collection items COLKEY01
```

## 创建集合

```bash
zot collection create "New Project"
```

## 移动条目到集合

```bash
zot collection move ITEMKEY COLKEY
```

## 重命名集合

```bash
zot collection rename COLKEY "Better Name"
```

## 删除集合

```bash
zot collection delete COLKEY --yes
```

## 批量重组

使用 JSON 计划将条目重新组织到新集合：

```bash
zot collection reorganize plan.json
```

示例 `plan.json`：

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
