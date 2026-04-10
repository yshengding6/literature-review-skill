# Literature Review Agent | 文献综述智能体

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Version](https://img.shields.io/badge/version-4.2.0-purple.svg)]()

## English / [中文](#中文说明)

---

## English

**A professional AI agent for classical Chinese literature review featuring "Socratic Roundtable" methodology, political history probing, and evidence-graded synthesis.**

This intelligent agent helps researchers systematically reconstruct the academic history of classical texts through four hardcore analytical methods: Political History Probe, 6-Dimension Deconstruction, Anomaly Detection, and Counterfactual Testing. It features an interactive checkpoint system and a Socratic roundtable debate for rigorous scholarly analysis.

### Key Features (v4.2.0 — Socratic Roundtable + Cultural Comparison)

#### 📜 Omni-Classic Protocol (v4.0.0+)
- **Stage 1 - Textual Analysis (考据层)**: Character-level interpretation, variant collation, establishing physical fact base
- **Stage 2 - Scholarly Debate (博弈层)**: 6-Dimension commentary deconstruction, political history probing, deep historical motivation analysis
- **Stage 3 - Philosophical Synthesis (义理层)**: Dynamic roundtable conference triggering scholarly stance collision
- **Stage 4 - Evidence-Based Translation (转译层)**: Evidence-graded comprehensive synthesis, multi-format output
- **Checkpoint B0 (v4.0.0)**: Pause for user confirmation after all commentaries are analyzed before entering roundtable debate phase

#### 🌍 Cultural Comparison Module (v4.1.0+)
- **Zhuzi (诸子百家) vs Western Philosophy**: Automated cross-cultural analysis between Confucian/Daoist/Mohist/Legalist schools and Greek/Kantian/Stoic traditions
- **Concept Mapping**: Automatic alignment of Chinese philosophical concepts with Western equivalents (e.g., 仁 ↔ agape/phronesis)
- **Three Document Types**: Generate Annotation (注疏解读), Roundtable Minutes (圆桌纪要), and Literature Review (文献综述)
- **Get笔记 Integration**: Auto-save documents to GetNote knowledge base with smart tagging

#### 🔪 Four Surgical Knives (Core Methodology)
- **Political History Probe**: Restore text to Spring-Autumn power dynamics, analyzing interest distribution, political risk aversion, and legitimacy construction
- **6-Dimension Deconstruction**: Dissect commentaries across textual interpretation, methodology, conceptual reconstruction, stance assumptions, implicit premises, and era motivation
- **Anomaly Detection**: Scan for "unnecessary but deliberately preserved" vocabulary to find logical breakpoints as "cold knowledge" breakthrough points
- **Counterfactual Testing**: Execute minimal substitution experiments (verb/object/time) to prove the uniqueness of original intent through "semantic collapse"

#### 🏛️ Interactive Socratic Roundtable
- **Conflict-driven role selection**: 6 representative scholars with at least 2 opposing academic stances
- **Socrates (fixed seat)**: Uses elenchus (midwifery method) for logical cleansing with 3 fatal counter-questions
- **Checkpoint system**: User confirmation at key stages ensures research path accuracy

#### 📊 Evidence-Graded Synthesis Protocol
- **[Empirical]**: Content directly from ancient texts or reliable historical sources
- **[Inference]**: Logical deductions based on scholarly stance, must attribute to specific school
- **[Missing]**: Explicit acknowledgment of gaps in existing evidence

#### 🔥 The Non-Consensus Factor (老丁因子)
- Forces discovery of a "non-consensus" observation point for content uniqueness
- **Heresy Detector**: Summarizes details collectively ignored by mainstream commentaries
- **Cold Knowledge Proposition**: Generate conclusions in "X is not Y, but Z" format

#### 🌐 Multi-Source Integration (Inherited)
- **Local PDF Mode**: Analyze PDF, TXT, MD files with advanced parsing
- **Feishu Bitable Mode**: Direct integration with Feishu/Lark multidimensional tables
- **Web Search**: Fetch literature from online sources (API integration ready)

### Installation

```bash
# Clone the repository
git clone https://github.com/yshengding6/literature-review-skill.git
cd literature-review-skill

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Local PDF Mode

Analyze documents stored locally on your computer:

```bash
# Basic review with local files
python main.py --topic "Artificial Intelligence in Healthcare" \
  --files doc1.pdf doc2.txt doc3.pdf

# English output
python main.py --topic "Deep Learning Applications" \
  --files paper1.pdf paper2.pdf \
  --lang en --depth deep
```

**Supported Formats**: PDF, TXT, MD, DOCX

#### Feishu Bitable Mode

Leverage collaborative research data from Feishu multidimensional tables:

```bash
# Step 1: Set up Feishu credentials
# Option A: Via environment variables
export FEISHU_APP_ID="cli_xxxxxxxx"
export FEISHU_APP_SECRET="your_app_secret"

# Option B: Via config.yaml
# Copy config.example.yaml to config.yaml and fill in credentials

# Step 2: Enable Feishu in config.yaml
feishu:
  enabled: true

# Step 3: Run MCP server mode
python main.py
```

**Feishu Integration Features**:
- Fetch records from Feishu bases and spreadsheets
- Parse URLs automatically (baseinfo, tables, spreadsheets)
- Paginated data fetching for large datasets
- Retry mechanism with exponential backoff

### MCP Server Mode

Run as a Model Context Protocol server for seamless AI integration:

```bash
python main.py
```

The server exposes the following tools:
- `generate_literature_review` - Generate comprehensive literature review
- `analyze_document` - Analyze single document
- `cross_verify_documents` - Cross-verify multiple documents
- `fetch_feishu_data` - Fetch data from Feishu Bitable
- `list_feishu_tables` - List tables in Feishu base

### Multi-Format Output

Generate reviews in multiple formats:

```bash
# Markdown (default)
python main.py --topic "论语·八佾" --format md

# PDF with academic footnotes
python main.py --topic "论语·八佾" --format pdf

# Word document
python main.py --topic "论语·八佾" --format docx
```

### Configuration

Create `config.yaml` from `config.example.yaml`:

```yaml
# Feishu Integration
feishu:
  enabled: false  # Set to true to enable
  app_id: "cli_xxxxxxxx"
  app_secret: "your_app_secret"
  api_base_url: "https://open.feishu.cn/open-apis"
  timeout: 30

# Analysis Settings
analysis:
  similarity_threshold: 0.7
  max_key_points: 15
  max_consensus: 8
  max_disagreements: 8
  max_research_gaps: 10
  detailed_analysis: true

# Output Settings
output:
  default_language: zh  # zh or en
  generate_bibtex: true
  output_dir: "./output"
```

### Output Format

The agent generates:

1. **Markdown Review Report** (`{topic}_综述.md` / `{topic}_Review.md`)
   - Research background and objectives
   - Source description
   - Key findings with citations
   - Cross-verification analysis (consensus, disagreements, gaps)
   - Detailed per-document analysis
   - Formatted references

2. **BibTeX File** (`{topic}_references.bib`)
   - Zotero/LaTeX compatible format
   - Strict citation standards

3. **Log File** (`literature_review.log`)
   - Detailed processing logs for debugging

### Document Formats Supported

| Format | Extension | Notes |
|---------|------------|--------|
| PDF | .pdf | CJK character support |
| Plain Text | .txt | UTF-8, GBK, Latin-1 |
| Markdown | .md | Direct parsing |
| Code Files | .py, .js, .json | Plain text mode |

### Examples

See the `examples/` directory for sample documents:
- `sample_document.txt` - Basic text example
- `sample_document2.txt` - Extended example
- `quantum_paper1.txt` - Quantum computing example

#### 📜 Featured Example: 《论语·乞醯章》深度分析

位于 `examples/qixi-analysis/` 的完整案例展示了本工具对中国古典文献的深度分析能力：

**分析对象**：《论语·公冶长第五·乞醯章》"孰谓微生高直？或乞醯焉，乞诸其邻而与之。"

**分析内容**：
1. **历代注疏原文** - 从孔安国到程树德，梳理2000年注疏史
2. **注疏六维解剖** - 深度解构朱熹、刘宝楠等注家的方法论
3. **诸子百家对比** - 儒/道/墨/法四家对"直"的不同理解
4. **东西方哲学对比** - 苏格拉底、康德、亚里士多德的视角
5. **苏格拉底圆桌会议** - 跨时空学术辩论，9位学者+苏格拉底
6. **完整文献综述报告** - 包含老丁因子（非共识观察）

**核心发现**：
> "乞醯章"不是在批评微生高，而是在批评那个给他"直名"的社会——以及我们今天还在用"直/不直"二元标签评判他人的习惯。

**冷知识命题**：
> 微生高不是不直，而是"直"这个概念本身就不足以描述人性的复杂。孔子此章，是在邀请我们放下标签，看见具体的人。

这个案例完美展示了本工具的四大核心方法论：
- 🔪 **政治史探针**：还原春秋时代的权力博弈
- 🔪 **六维解剖法**：拆解历代注疏的解释逻辑
- 🔪 **异常检测**：发现文本中被忽略的"赘词"
- 🔪 **变量替换实验**：验证原文意图的唯一性

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

### License

MIT License - see [LICENSE](LICENSE) for details

---

## 中文说明

**学术文献综述智能体：具备《论语》级深度分析与飞书多维表格集成的专业研究助手。**

本智能体帮助研究人员系统分析学术论文，识别多篇文献间的共识与分歧，检测研究空白，并生成符合严格引用标准的综合文献综述。

### 核心特性

#### 📜 Omni-Classic Protocol（v4.0.0 新增）
- **阶段 1 - 考据层**：字词校释、异文校勘，建立物理事实基础
- **阶段 2 - 博弈层**：注疏六维解剖、政治史探针，深度挖掘历史动机
- **阶段 3 - 义理层**：动态圆桌会议，触发学术立场对立碰撞
- **阶段 4 - 转译层**：证据分级综述合成，多格式输出
- **检查点 B0（NEW）**：所有注疏解读完成后，暂停确认后再进入圆桌论辩阶段

#### 🔬 《论语》级深度分析
- **交叉验证系统**：识别多篇文献中的共识观点与分歧
- **研究空白检测**：自动发现局限性、未解决问题及未来研究方向
- **主题分析**：提取关键主题并进行频率分析与置信度评分
- **严格引用格式**：强制 `[作者, 年份, 页码]` 格式，防止 AI 幻觉

#### 📊 多源集成
- **本地 PDF 模式**：分析本地存储的 PDF、TXT、MD 文件
- **飞书多维表格模式**：直接集成飞书/ Lark 多维表格进行协作研究
- **网络搜索**：从在线来源获取文献（API 接入就绪）

#### 🌐 双语支持
- 完整的中英文输出支持
- PDF 解析中的 CJK（中日韩）字符处理
- 两种语言的学术格式规范

### 安装

```bash
# 克隆仓库
git clone https://github.com/yshengding6/literature-review-skill.git
cd literature-review-skill

# 安装依赖
pip install -r requirements.txt
```

### 使用方法

#### 本地 PDF 模式

分析本地存储的文档：

```bash
# 基本综述（本地文件）
python main.py --topic "人工智能在医疗中的应用" \
  --files doc1.pdf doc2.txt doc3.pdf

# 英文输出
python main.py --topic "深度学习应用" \
  --files paper1.pdf paper2.pdf \
  --lang en --depth deep
```

**支持的格式**：PDF, TXT, MD, DOCX

#### 飞书多维表格模式

利用飞书多维表格的协作研究数据：

```bash
# 步骤 1：设置飞书凭证
# 选项 A：通过环境变量
export FEISHU_APP_ID="cli_xxxxxxxx"
export FEISHU_APP_SECRET="your_app_secret"

# 选项 B：通过 config.yaml
# 复制 config.example.yaml 为 config.yaml 并填写凭证

# 步骤 2：在 config.yaml 中启用飞书
feishu:
  enabled: true

# 步骤 3：运行 MCP 服务器模式
python main.py
```

**飞书集成功能**：
- 从飞书多维表格和电子表格获取记录
- 自动解析 URL（baseinfo、表格、电子表格）
- 大数据集的分页获取
- 指数退避重试机制

### MCP 服务器模式

作为模型上下文协议服务器运行，实现无缝 AI 集成：

```bash
python main.py
```

服务器提供以下工具：
- `generate_literature_review` - 生成综合文献综述
- `analyze_document` - 分析单个文档
- `cross_verify_documents` - 交叉验证多个文档
- `fetch_feishu_data` - 从飞书多维表格获取数据
- `list_feishu_tables` - 列出飞书多维表格中的表

### 配置

从 `config.example.yaml` 创建 `config.yaml`：

```yaml
# 飞书集成
feishu:
  enabled: false  # 设置为 true 以启用
  app_id: "cli_xxxxxxxx"
  app_secret: "your_app_secret"
  api_base_url: "https://open.feishu.cn/open-apis"
  timeout: 30

# 分析设置
analysis:
  similarity_threshold: 0.7
  max_key_points: 15
  max_consensus: 8
  max_disagreements: 8
  max_research_gaps: 10
  detailed_analysis: true

# 输出设置
output:
  default_language: zh  # zh 或 en
  generate_bibtex: true
  output_dir: "./output"
```

### 输出格式

智能体生成：

1. **Markdown 综述报告** (`{topic}_综述.md` / `{topic}_Review.md`)
   - 研究背景与目标
   - 资料来源说明
   - 带引用的核心观点
   - 交叉验证分析（共识、分歧、空白）
   - 详细文档分析
   - 格式化参考文献

2. **BibTeX 文件** (`{topic}_references.bib`)
   - Zotero/LaTeX 兼容格式
   - 严格引用标准

3. **日志文件** (`literature_review.log`)
   - 详细处理日志用于调试

### 支持的文档格式

| 格式 | 扩展名 | 说明 |
|---------|------------|--------|
| PDF | .pdf | CJK 字符支持 |
| 纯文本 | .txt | UTF-8, GBK, Latin-1 |
| Markdown | .md | 直接解析 |
| 代码文件 | .py, .js, .json | 纯文本模式 |

### 示例

查看 `examples/` 目录中的示例文档：
- `sample_document.txt` - 基本文本示例
- `sample_document2.txt` - 扩展示例
- `quantum_paper1.txt` - 量子计算示例

#### 📜 精选案例：《论语·乞醯章》深度分析

位于 `examples/qixi-analysis/` 的完整案例展示了本工具对中国古典文献的深度分析能力：

**分析对象**：《论语·公冶长第五·乞醯章》"孰谓微生高直？或乞醯焉，乞诸其邻而与之。"

**分析内容**：
1. **历代注疏原文** - 从孔安国到程树德，梳理2000年注疏史
2. **注疏六维解剖** - 深度解构朱熹、刘宝楠等注家的方法论
3. **诸子百家对比** - 儒/道/墨/法四家对"直"的不同理解
4. **东西方哲学对比** - 苏格拉底、康德、亚里士多德的视角
5. **苏格拉底圆桌会议** - 跨时空学术辩论，9位学者+苏格拉底
6. **完整文献综述报告** - 包含老丁因子（非共识观察）

**核心发现**：
> "乞醯章"不是在批评微生高，而是在批评那个给他"直名"的社会——以及我们今天还在用"直/不直"二元标签评判他人的习惯。

**冷知识命题**：
> 微生高不是不直，而是"直"这个概念本身就不足以描述人性的复杂。孔子此章，是在邀请我们放下标签，看见具体的人。

这个案例完美展示了本工具的四大核心方法论：
- 🔪 **政治史探针**：还原春秋时代的权力博弈
- 🔪 **六维解剖法**：拆解历代注疏的解释逻辑
- 🔪 **异常检测**：发现文本中被忽略的"赘词"
- 🔪 **变量替换实验**：验证原文意图的唯一性

### 贡献

欢迎贡献！请：
1. Fork 仓库
2. 创建功能分支
3. 提交 Pull Request

### 许可证

MIT 许可证 - 详情请参阅 [LICENSE](LICENSE)

---

## Acknowledgments / 致谢

Built with:
- `fastmcp` - MCP 框架
- `httpx` - HTTP 客户端
- `pdfplumber` / `pypdf` - PDF 解析
- `reportlab` - PDF 生成
- `python-docx` - DOCX 生成
- `pyyaml` - YAML 配置

## Contact / 联系

- GitHub: [yshengding6](https://github.com/yshengding6)
- Issues: [Report Issues](https://github.com/yshengding6/literature-review-skill/issues)
