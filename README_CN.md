# 📚 Literature Review Skill (苏格拉底圆桌版)

<div align="center">

**一键生成专业学术文献综述 · 苏格拉底圆桌会议 · 四把手术刀方法论**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-v3.0.0%20Socratic-purple.svg)]()

从"文献综述"进化为"学术史侦探" 🔍

</div>

---

## ✨ v3.0.0 核心亮点：苏格拉底圆桌版

### 🔪 四把手术刀（深度研究方法论）

v3.0 版本强制要求 AI 放弃平庸的道德感悟，通过四种硬核逻辑路径进行推演：

| 手术刀 | 方法 | 目标 |
|--------|------|------|
| 🔪 政治史探针 | 将文本还原为权力博弈 | 剥离道德滤镜，分析利益分配与政治避险 |
| 🔪 六维解剖 | 拆解注疏的六个维度 | 揭示"解释机器"的运作原理 |
| 🔪 异常检测 | 扫描赘词、矛盾词、沉默区 | 寻找冷知识命题的突破口 |
| 🔪 变量替换 | 换动词/对象/时间 | 以"语义塌陷"反证原意图唯一性 |

### 🏛️ 苏格拉底圆桌会议

- **冲突点将**：自动识别 6 位代表学者，强制包含至少两组对立学术立场
- **苏格拉底固定席位**：使用助产术进行逻辑清洗，提出 3 个致命反问
- **检查点交互**：阶段 1 和阶段 3 设置用户确认点，确保研究方向不偏离

### 📊 证据分级协议

| 标签 | 含义 | 使用场景 |
|------|------|---------|
| [实证] | 古籍原文直接支持 | 版本校勘、字词训诂 |
| [推论] | 基于学派立场的推导 | 学者动机、时代背景 |
| [缺失] | 明确缺乏直接证据 | 研究空白、未解问题 |

### 🔥 老丁因子 (The Non-Consensus Factor)

- **异见捕捉器**：总结主流注疏中被共同忽略的细节
- **冷知识命题**："X 并不是 Y，而是 Z" — 违背常见理解但可被论证

---

## 📦 快速开始

### 前置要求

- Python 3.8 或更高版本
- pip 包管理器

### 一键安装

```bash
# 克隆仓库
git clone https://github.com/yshengding6/literature-review-skill.git
cd literature-review-skill

# 安装依赖
pip install -r requirements.txt
```

### Windows 用户快速上手

**1️⃣ 安装 Python**

访问 https://python.org 下载并安装 Python（勾选 "Add Python to PATH"）

**2️⃣ 安装依赖**

```cmd
cd D:\path\to\literature-review-skill
pip install -r requirements.txt
```

**3️⃣ 运行示例**

```cmd
# 基础用法
python main.py --topic "人工智能在医疗领域的应用" --files doc1.txt doc2.pdf

# 完整参数
python main.py --topic "AI医疗" --files doc1.txt doc2.pdf --lang zh --depth deep --bibtex

# 禁用 BibTeX 导出
python main.py --topic "AI研究" --files doc1.txt --no-bibtex
```

---

## 🎨 使用指南

### 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--topic` | 字符串 | 必填 | 研究主题/章句 |
| `--files` | 列表 | 可选 | 本地文档文件路径 |
| `--lang` | 字符串 | zh | 输出语言 (zh/en) |
| `--format` | 字符串 | md | 输出格式 (md/pdf/docx) |
| `--depth` | 字符串 | deep | 分析深度 (basic/medium/deep) |
| `--no-socratic` | 标志 | False | 跳过圆桌会议阶段 |
| `--no-web` | 标志 | False | 禁用网络搜索 |
| `--no-bibtex` | 标志 | False | 禁用 BibTeX 导出 |

### 使用示例

```bash
# 生成中文综述
python main.py --topic "机器学习在金融中的应用" --files examples/sample.txt

# 生成英文综述
python main.py --topic "Deep Learning" --lang en --files doc1.pdf doc2.txt

# 深度分析模式
python main.py --topic "AI伦理" --depth deep --files paper1.txt paper2.txt paper3.pdf

# 仅本地文档分析
python main.py --topic "研究主题" --no-web --files local_doc.txt
```

### 作为 MCP Server 运行

```bash
python main.py
```

---

## 📊 输出格式

### Markdown 综述报告

生成的报告包含以下部分：

1. **📖 研究背景与目标** - 研究背景与目标
2. **📁 资料来源说明** - 已分析文档列表
3. **💡 核心观点摘要** - 带引用的关键观点 `[Author, Year]`
4. **🔍 交叉验证分析**:
   - 共识观点 - 多来源支持的共识
   - 冲突观点 - 已识别的分歧
   - 研究空白 - 局限性与未来方向
5. **📋 详细分析** - 每个文档的详细分析
6. **📚 参考文献** - 格式化的参考文献

### BibTeX 文件

自动生成 `<topic>_references.bib`，兼容 Zotero/LaTeX：

```bibtex
@misc{ref1,
  author = {张三, 李四},
  title = {人工智能在医疗领域的应用},
  year = {2024},
  note = {paper.pdf}
}
```

---

## ⚙️ 配置选项

创建 `config.yaml` 文件进行自定义配置：

```yaml
# API 配置
web_search:
  enabled: true
  api_key: ""  # Google/Bing Search API 密钥
  provider: "mock"  # mock/google/bing

# 输出设置
output:
  language: "zh"  # zh 或 en
  generate_bibtex: true
  output_dir: "."

# 分析设置
analysis:
  similarity_threshold: 0.7  # 交叉验证阈值
  max_key_points: 15
  extract_research_gaps: true
```

---

## 💡 实战案例

### 案例 1: 古典文献研究

```bash
python main.py --topic "《论语》中'仁'的内涵对比" \
  --files "论语资料1.pdf" "论语资料2.pdf"
```

**输出：**
- `《论语》中'仁'的内涵对比_综述.md`
- `《论语》中'仁'的内涵对比_references.bib`

### 案例 2: 英文学术综述

```bash
python main.py --topic "Transformers in NLP" \
  --lang en \
  --files attention.pdf bert.pdf gpt.pdf
```

**输出：**
- `Transformers_in_NLP_Review.md`
- `Transformers_in_NLP_references.bib`

### 案例 3: 交叉验证分析

当你有多篇文档需要分析共识与分歧时：

```bash
python main.py --topic "AI伦理争议" \
  --files paper1.txt paper2.txt paper3.pdf
```

综述将包含详细的交叉验证分析，展示：
- 多来源支持的观点（共识）
- 各来源间的冲突观点（分歧）
- 所有论文的综合研究空白

---

## 📄 支持的文档格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| 纯文本 | .txt | 支持 UTF-8、GBK、Latin-1 编码 |
| PDF | .pdf | 需要 `pypdf` 包 |
| Markdown | .md | 作为纯文本读取 |
| 代码文件 | .py, .js 等 | 作为纯文本读取 |

---

## 🔍 引用格式

本工具严格执行 `[Author, Year]` 引用格式

这种格式的优势：
- 🔒 通过要求来源归属，防止 AI 幻觉
- 📝 兼容学术写作标准
- 🔗 链接到 BibTeX 条目以提供正确引用

---

## ❓ 常见问题

### Windows 编码问题

如果遇到编码错误：

```cmd
chcp 65001
set PYTHONIOENCODING=utf-8
python main.py --topic "主题" --files doc.txt
```

### PDF 解析错误

对于更好的 PDF 解析（特别是多列布局）：

1. 安装 `marker-pdf`:
```cmd
pip install marker-pdf
```

2. 在 `main.py` 中取消注释：
```python
# from pypdf import PdfReader  # 注释此行
from marker_pdf import convert_pdf  # 取消注释此行
```

### 未找到文件错误

- 确保文件路径正确
- 使用完整路径，而非相对路径
- 在 Windows 上使用正斜杠或转义反斜杠

---

## 🏗️ 项目结构

```
literature-review-skill/
├── main.py              # 核心实现
├── feishu_fetcher.py    # 飞书数据获取模块
├── requirements.txt     # Python 依赖
├── README.md            # 英文文档
├── README_CN.md         # 中文文档
├── SKILL.md             # Skill 定义文档
├── config.yaml.example  # 配置模板
├── examples/            # 示例文档
│   └── 《论语》中'仁'的内涵对比_综述.md
└── tests/               # 单元测试
    └── test_analyzer.py
```

---

## 🧪 开发

### 运行测试

```bash
# 运行所有测试
python tests/test_analyzer.py

# 运行特定测试
python -m pytest tests/ -v
```

---

## 📜 版本历史

### v3.0.0 (苏格拉底圆桌版) — 2026-03-27

代号：Socratic Roundtable

- 🔪 新增"四把手术刀"方法论（政治史探针、六维解剖、异常检测、变量替换）
- 🏛️ 新增苏格拉底圆桌会议系统（冲突点将 + 逻辑清洗 + 致命反问）
- ⏸️ 新增交互式检查点机制（检查点 A / 检查点 B）
- 📊 新增证据分级协议（[实证] / [推论] / [缺失]）
- 🔥 新增老丁因子（异见捕捉器 + 冷知识命题）
- 📝 PDF/Docx 导出支持标准学术脚注格式
- 🚫 幻觉控制强化：严禁混淆注者原话与 AI 解读
- ✅ 保留向后兼容（MCP 接口、飞书集成、BibTeX 导出）

### v2.2.1 (增强版) — 2026-03-13
- ✨ 添加简单读取模式 (`--simple-read`)
- ✨ 添加日志基础设施
- 🐛 改进异常处理和类型提示

### v2.0 (增强版)
- ✨ 添加共识/分歧交叉验证
- ✨ 添加研究空白检测
- ✨ 添加带来源追踪的严格引用格式
- ✨ 添加 PDF 解析支持
- ✨ 添加 Zotero/LaTeX BibTeX 导出
- ✨ 添加多语言支持 (zh/en)
- 🐛 改进 Windows 兼容性

### v1.0
- 🎉 初始发布，基础文档分析
- 🔍 模拟网络搜索功能
- 📝 Markdown 综述生成

---

## 📄 许可证

MIT License - 欢迎根据研究需要自由使用和修改

---

## 🤝 贡献

欢迎贡献！请：
1. Fork 本仓库
2. 创建功能分支
3. 提交 Pull Request

---

## 🙏 致谢

本项目构建于：
- `fastmcp` - MCP 框架
- `pypdf` / `pdfplumber` - PDF 解析
- Python 标准库 - 文本处理

---

<div align="center">

**Made with ❤️ by @yshengding6**

[GitHub](https://github.com/yshengding6/literature-review-skill) · [Issues](https://github.com/yshengding6/literature-review-skill/issues)

⭐ 如果这个项目对你有帮助，请给个 Star！

</div>
