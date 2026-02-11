# PDF Ligature Stego-Sniffer 🔍

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A powerful security analysis tool that detects hidden steganographic data embedded in PDF documents through Unicode manipulation, specifically targeting invisible characters, ligatures, and font glyph anomalies in documents containing Arabic, Urdu, and mixed-script content.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [The Problem](#the-problem)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [Command Line](#command-line)
  - [Python API](#python-api)
- [Detection Methods](#detection-methods)
- [Examples](#examples)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## 🎯 Overview

PDF Ligature Stego-Sniffer is a specialized forensic tool designed to uncover covert communication channels in PDF documents. It analyzes PDFs at the character level to detect:

- **Invisible Unicode characters** (zero-width joiners, non-joiners, directional marks)
- **Bidirectional text manipulation** (RTL/LTR overrides and embeddings)
- **Font glyph anomalies** indicating suspicious font customization
- **Mixed-script patterns** that may hide encoded data

This tool is particularly effective for documents containing Arabic, Urdu, Persian, and other right-to-left scripts where Unicode manipulation is more common.

---

## ✨ Features

### 🔍 Character-Level Analysis
- Extracts every character from the PDF with full metadata (position, font, size, Unicode properties)
- Identifies suspicious invisible characters and format controls
- Maps character codepoints to Unicode names and categories

### 🎨 Font Inspection
- Extracts embedded fonts using PyMuPDF
- Analyzes glyph tables with fontTools
- Detects abnormal glyph mappings and script mismatches
- Flags fonts with suspiciously small or unusual glyph sets

### 📊 Comprehensive Reporting
- Quick summary statistics (total chars, invisible chars, RTL marks)
- Detailed suspicious character reports with page numbers and positions
- Font analysis with glyph counts and anomaly flags
- JSON export for integration with other tools

### 🖥️ Multiple Interfaces
- **Web UI**: Streamlit-based interface for easy PDF uploads and interactive analysis
- **CLI**: Command-line tool for batch processing and automation
- **Python API**: Import and use in your own Python scripts

---

## 🚨 The Problem

PDF documents can be used as covert channels to hide data using Unicode steganography techniques:

1. **Invisible Characters**: Zero-width characters (ZWJ, ZWNJ) and format controls that don't render visually but encode binary information through their presence/absence patterns.

2. **Bidirectional Overrides**: RTL/LTR marks and embeddings can be used to create invisible layers or alter the rendering without changing the underlying text.

3. **Font Manipulation**: Custom fonts with altered glyph mappings can make characters appear as something different from their actual Unicode values.

4. **Ligature Abuse**: Multi-character ligatures in Arabic/Urdu scripts can be manipulated to encode additional data.

These techniques are particularly dangerous because:
- They're invisible to the human eye
- They bypass traditional content filters
- They can carry significant data payloads
- They're difficult to detect without specialized tools

---

## 🔧 How It Works

The tool employs a multi-layered detection approach:

```
PDF Document
    ↓
┌─────────────────────────────────────┐
│  1. Character Extraction (pdfminer) │
│     • Extract every character       │
│     • Preserve layout & metadata    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  2. Unicode Analysis                │
│     • Check Unicode categories      │
│     • Identify invisible chars      │
│     • Detect bidi controls          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  3. Font Inspection (PyMuPDF)       │
│     • Extract embedded fonts        │
│     • Parse glyph tables            │
│     • Detect anomalies              │
└─────────────────────────────────────┘
    ↓
Analysis Report
```

---

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Step 1: Clone the Repository

```bash
git clone https://github.com/Ali-Nasir2/pdf-ligature-stego-sniffer.git
cd pdf-ligature-stego-sniffer
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

The required packages include:
- `streamlit` - Web interface
- `pdfminer.six` - PDF text extraction
- `pdfplumber` - PDF parsing
- `fonttools` - Font analysis
- `PyMuPDF` - Font extraction
- `pandas` - Data manipulation
- `regex` - Advanced pattern matching
- `jinja2` - Template rendering
- `pytest` - Testing framework

---

## 🚀 Usage

### Web Interface

Launch the Streamlit web application for an interactive analysis experience:

```bash
streamlit run app/main.py
```

This will open a browser window where you can:
1. Upload your PDF file
2. View the analysis summary
3. Explore character records
4. Review suspicious findings

### Command Line

Analyze a PDF from the command line:

```bash
python run_analyzer.py
```

By default, this analyzes the test file. To analyze a custom PDF, edit the `path` variable in `run_analyzer.py`:

```python
path = "your_file.pdf"
```

Or use the analyzer module directly:

```bash
python -m core.analyzer path/to/your/file.pdf
```

### Python API

Integrate the analyzer into your own Python scripts:

```python
from core.analyzer import analyze_pdf

# Analyze from file path
with open("document.pdf", "rb") as f:
    result = analyze_pdf(f)

# Access results
print(f"Total characters: {result['summary']['total_chars']}")
print(f"Suspicious chars: {result['summary']['suspicious_count']}")

# Iterate through suspicious characters
for suspicious in result['suspicious']:
    print(f"Page {suspicious['page']}: {suspicious['codepoint']} - {suspicious['name']}")

# Check font reports
for font in result['fonts_report']:
    print(f"Font: {font['font_name']} - {font['flag']}")
```

**API Response Structure:**

```python
{
    "summary": {
        "total_chars": int,
        "zero_width_count": int,
        "rtl_marks_count": int,
        "fonts_used_top": [(font_name, count), ...],
        "mixed_scripts_hint": bool,
        "suspicious_count": int,
        "fonts_checked": int,
        "fonts_flags": [str, ...]
    },
    "characters": [
        {
            "page": int,
            "char": str,
            "codepoint": str,
            "name": str,
            "fontname": str,
            "size": float,
            "x0": float, "y0": float,
            "x1": float, "y1": float
        },
        ...
    ],
    "suspicious": [
        {
            "page": int,
            "char": str,
            "codepoint": str,
            "name": str,
            "fontname": str,
            "position": (float, float)
        },
        ...
    ],
    "fonts_report": [
        {
            "font_name": str,
            "glyph_count": int,
            "flag": str
        },
        ...
    ]
}
```

---

## 🔬 Detection Methods

### Suspicious Unicode Characters

The tool detects the following categories of potentially malicious characters:

| Category | Unicode Range | Examples | Purpose in Steganography |
|----------|--------------|----------|--------------------------|
| Zero-Width Joiners | U+200D | ZWJ | Binary encoding via presence/absence |
| Zero-Width Non-Joiners | U+200C | ZWNJ | Binary encoding via presence/absence |
| Right-to-Left Marks | U+200F | RLM | Directional control manipulation |
| Left-to-Right Marks | U+200E | LRM | Directional control manipulation |
| Bidi Embeddings | U+202A-U+202E | RLE, LRE, PDF, RLO, LRO | Text rendering manipulation |
| Format Characters | Unicode Cf category | Various | Invisible formatting controls |

### Font Glyph Analysis

The tool performs heuristic analysis on embedded fonts:

- **Small Glyph Sets** (< 50 glyphs): May indicate a custom font designed for specific character substitution
- **Script Mismatches**: Fonts with Latin-dominant glyphs but used in Arabic/Urdu context (or vice versa)
- **Unusual Glyph Names**: Non-standard naming conventions in glyph tables

### Mixed Script Detection

Identifies documents that mix multiple scripts (e.g., Arabic + Latin), which can be used to hide data through:
- Script switching patterns
- Invisible character insertion at script boundaries
- Ligature manipulation across script boundaries

---

## 📝 Examples

### Example 1: Clean PDF

```bash
$ python run_analyzer.py

===== PDF SUMMARY =====
{
  "total_chars": 523,
  "zero_width_count": 0,
  "rtl_marks_count": 0,
  "suspicious_count": 0,
  "fonts_checked": 2,
  "fonts_flags": ["ok", "ok"]
}

No suspicious or hidden characters detected.
```

### Example 2: PDF with Hidden Characters

```bash
$ python run_analyzer.py

===== PDF SUMMARY =====
{
  "total_chars": 487,
  "zero_width_count": 8,
  "rtl_marks_count": 12,
  "suspicious_count": 20,
  "fonts_checked": 1,
  "fonts_flags": ["ok"]
}

===== SUSPICIOUS CHARACTERS FOUND =====
Page 1: U+200D (ZERO WIDTH JOINER)  Font=Arial  Pos=(120.5, 780.3)
Page 1: U+200F (RIGHT-TO-LEFT MARK)  Font=Arial  Pos=(145.2, 780.3)
Page 1: U+202B (RIGHT-TO-LEFT EMBEDDING)  Font=Arial  Pos=(98.7, 756.1)
...
```

### Example 3: PDF with Suspicious Font

```bash
===== FONT GLYPH REPORT =====
Font: CustomArabic                 | Glyphs: 45    | Arabic glyphs: 12   | Latin glyphs: 28   | very small glyph set
Font: Arial                        | Glyphs: 1234  | Arabic glyphs: —    | Latin glyphs: —    | ok
```

---

## 📁 Project Structure

```
pdf-ligature-stego-sniffer/
├── app/
│   └── main.py                    # Streamlit web interface
├── core/
│   └── analyzer.py                # Main analysis engine
├── fonts/                         # Font files for testing
├── templates/                     # HTML templates
├── tests/                         # Test suite
│   └── README.md
├── texts_file/                    # Sample text files
├── run_analyzer.py                # CLI interface
├── generate_urdu_test_pdf.py      # Test PDF generator
├── make_hidden_urdu_pdf.py        # Hidden character test PDF generator
├── generate_embedded_font_pdf.py  # Font embedding test generator
├── embed_font_fix.py              # Font embedding utility
├── requirements.txt               # Python dependencies
├── .gitignore
└── README.md
```

### Key Modules

- **`core/analyzer.py`**: Core analysis engine with character extraction, Unicode analysis, and font inspection
- **`app/main.py`**: Streamlit web UI for interactive analysis
- **`run_analyzer.py`**: Command-line interface with formatted output

---

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Generating Test PDFs

The repository includes utilities to generate test PDFs with various hidden character patterns:

```bash
# Generate Urdu test PDF with proper ligatures
python generate_urdu_test_pdf.py

# Generate PDF with hidden steganographic characters
python make_hidden_urdu_pdf.py

# Generate PDF with embedded fonts
python generate_embedded_font_pdf.py
```

### Adding New Detection Rules

To add new suspicious character detection rules, edit `core/analyzer.py`:

```python
def find_suspicious_characters(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    suspicious = []
    for r in records:
        ch = r["char"]
        code = ord(ch)
        
        # Add your custom detection logic here
        if your_condition:
            suspicious.append({
                "page": r["page"],
                "char": ch,
                "codepoint": r["codepoint"],
                "name": r["name"],
                "fontname": r["fontname"],
                "position": (r["x0"], r["y0"])
            })
    return suspicious
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs**: Open an issue with details about the problem
2. **Suggest Features**: Share your ideas for new detection methods
3. **Submit PRs**: Fix bugs or implement new features
4. **Improve Docs**: Help make this README even better
5. **Share Test Cases**: Contribute sample PDFs (sanitized) with interesting patterns

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure your code:
- Follows PEP 8 style guidelines
- Includes docstrings for new functions
- Passes existing tests
- Includes new tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **pdfminer.six**: For robust PDF text extraction
- **PyMuPDF (fitz)**: For font extraction capabilities
- **fontTools**: For comprehensive font analysis
- **Streamlit**: For the easy-to-use web interface
- The Unicode Consortium for comprehensive character documentation

---

## 📚 Further Reading

- [Unicode Steganography Techniques](https://en.wikipedia.org/wiki/Steganography#Unicode)
- [Bidirectional Text and Unicode](https://www.unicode.org/reports/tr9/)
- [Arabic Script and Ligatures](https://www.unicode.org/faq/arabic.html)
- [Zero-Width Characters in Security](https://www.npmjs.com/package/zero-width-detection)

---

## 📧 Contact

For questions, suggestions, or security concerns, please open an issue on GitHub.

---

## 🔒 Security Notice

This tool is intended for legitimate security research, forensic analysis, and PDF integrity verification. Users are responsible for ensuring their use complies with applicable laws and regulations. The authors are not responsible for any misuse of this tool.

---

<div align="center">

**⭐ If you find this tool useful, please consider giving it a star on GitHub! ⭐**

Made with ❤️ for the security research community

</div>
