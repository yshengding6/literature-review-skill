---
name: literature-review
version: 2.1.0
description: 学术级文献调研综述工具。支持 PDF 解析、交叉验证、研究空白检测、引用溯源、BibTeX 导出和飞书数据集成。
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

## Installation

```bash
pip install -r requirements.txt
```

## Dependencies

- `fastmcp>=0.10.0` - MCP framework
- `httpx>=0.27.0` - HTTP client
- `pypdf>=4.0.0` - PDF parsing
