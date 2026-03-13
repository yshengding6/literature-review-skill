---
name: literature-review
version: 2.2.1
description: 文献综述工具，用于学术研究和论文写作。支持 PDF 解析、交叉验证、研究空白检测、引用溯源、BibTeX 导出和飞书数据集成。适用于需要系统梳理多篇文献、识别共识与分歧、生成结构化综述报告的场景。
tags: [research, documentation, analysis, review, academic, cross-verification, pdf, bibtex, feishu]
author: Claude
---

# Literature Review Skill (Enhanced Edition)

A professional-grade tool for academic research that supports document analysis, cross-verification, and comprehensive literature review generation.

## New Features (v2.1)

### Feishu Integration
- [x] **Feishu Data Fetching** - Fetch data from Feishu bases/spreadsheets for literature review

### New Features (v2.0)

### Logic Enhancement
- [x] **Cross-Verification** - Identify consensus and disagreements across multiple papers
- [x] **Research Gap Detection** - Automatically detect research gaps and limitations in each review
- [x] **Source Tracing** - Enforce strict citation format [Author, Year, Page] to prevent AI hallucinations

### Tooling & Compatibility
- [x] **PDF Parsing** - Integrated pypdf for better handling of multi-column academic layouts
- [x] **BibTeX Support** - Automatically generate references.bib file for Zotero/LaTeX
- [x] **Windows Compatible** - All file I/O operations use encoding='utf-8' and pathlib for cross-platform handling

### Documentation
- [x] **README.md** - Updated with Quick Start guide for Windows users
- [x] **config.yaml.example** - Configuration template for API keys and default output languages (supports zh/en)

### Testing
- [x] **Unit Tests** - Added tests for PDF text extraction, citation extraction, and error handling

## Usage Scenarios

Use this skill when you need to:
- Conduct academic literature reviews
- Analyze multiple papers and identify consensus/disagreement
- Detect research gaps across sources
- Generate properly formatted citations and BibTeX files
- Analyze PDF academic papers
- Work in Chinese or English

## Capabilities

### Feishu Integration
- **Data Fetching**: Fetch records from Feishu bases and tables
- **URL Parsing**: Support for Feishu baseinfo and spreadsheet URLs
- **Pagination**: Automatic pagination for large datasets
- **Configurable**: Environment variable or config file authentication

### Feishu Integration Example
```bash
# Configure Feishu credentials (set as environment variables or in config.yaml)
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"

# Or add to config.yaml:
feishu:
  enabled: true
  app_id: "your_app_id"
  app_secret: "your_app_secret"

# Use Feishu data in your review
# The skill will automatically fetch data from your Feishu base
```

**Note**: Feishu API requires valid credentials. Configure in `config.yaml` or set as environment variables before use.

### Document Analysis
- **Formats Supported**: TXT, PDF (with pypdf), MD, code files
- **Encoding Support**: UTF-8, GBK, Latin-1 (automatic detection)
- **Citation Extraction**: Automatically extracts author, year, and title
- **Research Gap Detection**: Identifies limitations and future work needed

### Cross-Verification
- **Consensus Detection**: Finds views supported by multiple sources (with similarity threshold)
- **Disagreement Detection**: Identifies conflicting opinions across papers
- **Research Gap Aggregation**: Combines gaps from all documents

### Output Generation
- **Markdown Review**: Comprehensive report with citations
- **BibTeX File**: Zotero/LaTeX compatible references
- **Multi-Language**: Support for Chinese (zh) and English (en) output
- **Web Search Note**: Currently uses mock implementation. For real search functionality, integrate with Google Search API, Bing API, or configure in `config.yaml`.

## Input Parameters

### generate_literature_review
- `topic` - Research topic (required)
- `files` - Local document file paths (optional)
- `web_search` - Enable web search (default: true)
- `search_depth` - Search depth: basic/medium/deep (default: medium)
- `language` - Output language: zh/en (default: zh)
- `output_bibtex` - Generate BibTeX file (default: true)

### analyze_document
- `file_path` - Document file path (required)
- `language` - Output language: zh/en (default: zh)

### cross_verify_documents
- `files` - List of document file paths (required)
- `language` - Output language: zh/en (default: zh)

## Output Format

### Markdown Review Report Structure

1. Research Background & Objectives
2. Source Description (with statistics)
3. Key Findings (with citations [Author, Year])
4. Cross-Verification Analysis:
   - Consensus Views (with source count)
   - Conflicting Views (side-by-side comparison)
   - Research Gaps (aggregated from all sources)
5. Detailed Analysis (per-document breakdown)
6. References (formatted bibliography)

### BibTeX Format

```bibtex
@misc{ref1,
  author = {Smith, John},
  title = {Artificial Intelligence in Healthcare},
  year = {2024},
  note = {paper.pdf}
}
```

## Citation Format

The skill enforces strict citation format: `[Author, Year]` or `[Author, Year, Page]`

This format:
- Prevents AI hallucinations by requiring source attribution
- Is compatible with academic writing standards
- Links to BibTeX entries for proper references

## Configuration

Optional `config.yaml` file for custom settings:

```yaml
web_search:
  enabled: true
  api_key: ""
  provider: "mock"

output:
  language: "zh"  # zh or en
  generate_bibtex: true

analysis:
  similarity_threshold: 0.7
  max_key_points: 15
  extract_research_gaps: true
```

## Usage Examples

### Example 1: Basic Literature Review

Generate a comprehensive review from three local documents:

```bash
python main.py --topic "人工智能在医疗领域的应用" \
  --files examples/paper1.txt examples/paper2.txt examples/paper3.txt \
  --lang zh
```

**Output**:
- `人工智能在医疗领域的应用_综述.md` - Comprehensive review with background, findings, consensus, gaps
- `人工智能在医疗领域的应用_references.bib` - BibTeX references for Zotero/LaTeX

### Example 2: Cross-Verification Analysis

Analyze consensus and disagreements across multiple papers:

```bash
python main.py --topic "量子计算研究方向" \
  --files examples/quantum_paper1.txt examples/quantum_paper2.txt \
  --lang zh
```

**Output**:
- Review with explicit consensus/disagreement sections
- Comparison of viewpoints with source attribution

### Example 3: Simple File Read (Fast Mode)

Just read file contents without full analysis:

```bash
python main.py --topic "读取文件" \
  --files examples/sample.txt \
  --simple-read
```

**Output**:
- Basic file information only (type, summary, author, year)
- Faster processing for large files

### Example 4: English Review with BibTeX Export

Generate English review from PDF documents:

```bash
python main.py --topic "Deep Learning in Computer Vision" \
  --files docs/cv_paper1.pdf docs/cv_paper2.pdf \
  --lang en --output-bibtex
```

### Example 5: Disable Web Search

Use only local documents without web search:

```bash
python main.py --topic "区块链技术应用" \
  --files examples/blockchain_papers/ \
  --no-web
```

## Installation

```bash
pip install -r requirements.txt
```

## Dependencies

- `fastmcp>=0.10.0` - MCP framework
- `httpx>=0.27.0` - HTTP client
- `pypdf>=4.0.0` - PDF parsing

## Installation

```bash
pip install -r requirements.txt
```

## Dependencies

- `fastmcp>=0.10.0` - MCP framework
- `httpx>=0.27.0` - HTTP client
- `pypdf>=4.0.0` - PDF parsing
