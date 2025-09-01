# Markdown Tags 更新脚本

这个脚本用于简化 `src/posts/` 目录下所有 markdown 文件的 `tags` 元属性。它会将每个文件的 tags 更新为对应文件夹的名称。

## 脚本功能

- 自动遍历 `src/posts/` 目录下的所有子目录
- 读取每个 markdown 文件的 frontmatter 中的 tags 属性
- 将 tags 更新为对应文件夹的名称（转换为 kebab-case 格式）
- 保留其他 frontmatter 属性不变

## 使用方法

在项目根目录下运行以下命令：

```bash
node update-tags.cjs
```

## 脚本说明

脚本会处理以下目录结构：

```
src/
└── posts/
    ├── api-gateway/
    │   ├── file1.md
    │   └── file2.md
    ├── async-event-driven/
    │   ├── file1.md
    │   └── file2.md
    └── ...
```

处理后，`api-gateway` 目录下的所有文件的 tags 会被更新为 `[api-gateway]`，`async-event-driven` 目录下的所有文件的 tags 会被更新为 `[async-event-driven]`，以此类推。

## 注意事项

- 脚本只会修改 markdown 文件中的 tags 属性
- 其他 frontmatter 属性保持不变
- 脚本会自动将文件夹名称转换为 kebab-case 格式作为 tag