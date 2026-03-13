# Literature Review Skill (Enhanced Edition)

A professional-grade tool for academic research, supporting document analysis, cross-verification, and comprehensive literature review generation.

## Features

### Core Capabilities
- [x] **Document Analysis** - Analyze multiple document formats (TXT, PDF)
- [x] **Cross-Verification** - Identify consensus and disagreements across papers
- [x] **Research Gap Detection** - Automatically detect research gaps and limitations
- [x] **Source Tracing** - Strict citation format [Author, Year, Page] to prevent hallucinations
- [x] **Web Search** - Integrate with web resources (**Note: Currently mock implementation only**)
   > The web search functionality returns simulated results. For real search functionality, integrate with Google Search API, Bing API, or other search services and configure in `config.yaml`.

### Advanced Features
- [x] **PDF Parsing** - Support for academic PDF papers with pypdf
- [x] **BibTeX Export** - Generate Zotero/LaTeX compatible references
- [x] **Multi-Language** - Support for Chinese and English output
- [x] **Windows Compatible** - Full Windows path and encoding support

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yshengding6/literature-review-skill.git
cd literature-review-skill

# Install dependencies
pip install -r requirements.txt
```

### Windows Quick Start

For Windows users, follow these steps:

1. **Install Python** from https://python.org (include pip in installation)

2. **Open Command Prompt** or PowerShell:

```cmd
# Navigate to the project directory
cd D:\path\to\literature-review-skill

# Install dependencies
pip install -r requirements.txt
```

3. **Run the tool**:

```cmd
# Basic usage
python main.py --topic "Artificial Intelligence in Healthcare" --files doc1.txt doc2.pdf

# With options
python main.py --topic "AI in Healthcare" --files doc1.txt doc2.pdf --lang en --depth deep

# Disable BibTeX export
python main.py --topic "AI Research" --files doc1.txt --no-bibtex
```

## Usage

### Command Line Interface

```bash
# Basic review generation
python main.py --topic "<research_topic>" --files file1.txt file2.pdf

# With language selection (zh/en)
python main.py --topic "<topic>" --lang en --files file1.txt

# With search depth (basic/medium/deep)
python main.py --topic "<topic>" --depth deep --files file1.txt

# Disable web search
python main.py --topic "<topic>" --no-web --files file1.txt

# Disable BibTeX export
python main.py --topic "<topic>" --no-bibtex --files file1.txt
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|--------|----------|-------------|
| `--topic` | string | Required | Research topic |
| `--files` | list | Optional | Local document file paths |
| `--lang` | string | zh | Output language (zh/en) |
| `--depth` | string | medium | Web search depth (basic/medium/deep) |
| `--no-web` | flag | False | Disable web search |
| `--no-bibtex` | flag | False | Disable BibTeX export |

### As MCP Server

```bash
python main.py
```

## Output

### Markdown Review Report

The tool generates a comprehensive Markdown report including:

1. **Research Background** - Context and objectives
2. **Source Description** - List of analyzed documents
3. **Key Findings** - Key points with citations [Author, Year]
4. **Cross-Verification Analysis**:
   - Consensus Views - Agreements across sources
   - Conflicting Views - Disagreements identified
   - Research Gaps - Limitations and future directions
5. **Detailed Analysis** - Per-document breakdown
6. **References** - Formatted bibliography

### BibTeX File

Automatically generates `<topic>_references.bib` with Zotero/LaTeX compatible format:

```bibtex
@misc{ref1,
  author = {Smith, John},
  title = {Artificial Intelligence in Healthcare},
  year = {2024},
  note = {paper.pdf}
}
```

## Configuration

### Optional: config.yaml

Create a `config.yaml` file for custom settings:

```yaml
# API Configuration
web_search:
  enabled: true
  api_key: ""  # For Google/Bing Search API
  provider: "mock"  # mock/google/bing

# Output Settings
output:
  language: "zh"  # zh or en
  generate_bibtex: true
  output_dir: "."

# Analysis Settings
analysis:
  similarity_threshold: 0.7  # For cross-verification
  max_key_points: 15
  extract_research_gaps: true
```

## Examples

### Example 1: Basic Review

```bash
python main.py --topic "Machine Learning in Finance" --files examples/sample_document.txt
```

Output:
- `Machine_Learning_in_Finance_综述.md` (Chinese)
- `Machine_Learning_in_Finance_references.bib`

### Example 2: English Output

```bash
python main.py --topic "Deep Learning" --lang en --files doc1.pdf doc2.txt
```

Output:
- `Deep_Learning_Review.md` (English)
- `Deep_Learning_references.bib`

### Example 3: Cross-Verification Only

When you have multiple documents and want to analyze consensus:

```bash
python main.py --topic "AI Ethics" --files paper1.txt paper2.txt paper3.pdf
```

The review will include a "Cross-Verification Analysis" section showing:
- Views supported by multiple sources (Consensus)
- Conflicting opinions across sources (Disagreements)
- Combined research gaps across all papers

## Document Formats Supported

| Format | Extension | Notes |
|---------|------------|--------|
| Plain Text | .txt | UTF-8, GBK, Latin-1 encoding support |
| PDF | .pdf | Requires `pypdf` package |
| Markdown | .md | Read as plain text |
| Code files | .py, .js, etc. | Read as plain text |

## Citation Format

The tool enforces strict citation format: `[Author, Year]`

This format:
- Prevents AI hallucinations by requiring source attribution
- Is compatible with academic writing standards
- Links to BibTeX entries for proper references

## Troubleshooting

### Windows Encoding Issues

If you see encoding errors:

```cmd
chcp 65001
set PYTHONIOENCODING=utf-8
python main.py --topic "Your Topic" --files doc.txt
```

### PDF Parsing Errors

For better PDF parsing (especially multi-column layouts):

1. Install `marker-pdf`:
```cmd
pip install marker-pdf
```

2. Uncomment the line in `main.py`:
```python
# from pypdf import PdfReader  # Comment this
from marker_pdf import convert_pdf  # Uncomment this
```

### Empty Directory Error

If you get "No files found" error:
- Ensure file paths are correct
- Use full paths, not relative paths
- On Windows, use forward slashes or escape backslashes

## Development

### Running Tests

```bash
# Run all tests
python tests/test_analyzer.py

# Run specific test
python -m pytest tests/ -v
```

### Project Structure

```
literature-review-skill/
├── main.py              # Core implementation
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── config.yaml.example   # Configuration template
├── examples/             # Example documents
│   ├── sample_document.txt
│   └── sample_document2.txt
└── tests/               # Unit tests
    └── test_analyzer.py
```

## License

MIT License - feel free to use and modify for your research needs.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Acknowledgments

Built with:
- `fastmcp` - MCP framework
- `pypdf` - PDF parsing
- Standard Python libraries for text processing

## Version History

### v2.0 (Enhanced Edition)
- Added cross-verification for consensus/disagreement
- Added research gap detection
- Added strict citation format with source tracing
- Added PDF parsing support
- Added BibTeX export for Zotero/LaTeX
- Added multi-language support (zh/en)
- Improved Windows compatibility

### v1.0
- Initial release with basic document analysis
- Mock web search functionality
- Markdown review generation
