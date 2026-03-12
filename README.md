# Literature Review Skill

一个用于文献调研和综述生成的 AI Skill，支持本地文档分析和网络搜索混合调研方式。

## 功能特性

- 📄 **本地文档分析** - 支持分析多种格式的本地文档
- 🌐 **网络搜索** - 自动搜索相关网络资源
- 📊 **综合综述** - 生成包含摘要、分析、对比、结论的完整报告
- 🔍 **智能提取** - 自动提取关键点和核心观点
- 📝 **Markdown 输出** - 生成易于阅读和编辑的 Markdown 格式报告

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 作为 MCP Server 运行

```bash
python main.py
```

### 通过 Claude Code 调用

```
/literature-review --topic "人工智能在教育中的应用" --files ["doc1.pdf", "doc2.txt"] --web-search true --search-depth medium
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| topic | string | 是 | 研究主题 |
| files | list | 否 | 本地文档路径列表 |
| web_search | bool | 否 | 是否网络搜索（默认true） |
| search_depth | string | 否 | 搜索深度（basic/medium/deep） |

## 输出示例

综述报告将包含以下章节：

1. 研究背景与目标
2. 资料来源说明
3. 核心观点摘要
4. 详细分析（按来源）
5. 横向对比分析
6. 结论与建议
7. 参考资料列表

## 示例

```python
from main import ReviewGenerator

# 创建综述生成器
generator = ReviewGenerator()

# 生成综述
review = generator.generate_review(
    topic="机器学习在医疗诊断中的应用",
    files=["research_paper1.pdf", "case_study.docx"],
    web_search=True,
    search_depth="medium"
)

# 保存综述
with open("review.md", "w", encoding="utf-8") as f:
    f.write(review)
```

## 注意事项

- 当前版本为模拟搜索实现，实际使用需要接入真实搜索 API
- 支持的文档格式取决于文件内容是否可读为文本
- 建议对生成的综述进行人工审核和补充

## License

MIT
