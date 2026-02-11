# Contributing to PDF Ligature Stego-Sniffer

First off, thank you for considering contributing to PDF Ligature Stego-Sniffer! 🎉

It's people like you that make this tool better for everyone in the security research community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by common sense and mutual respect. By participating, you are expected to uphold this standard. Please be kind, considerate, and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (sample PDFs if possible, but sanitize any sensitive data)
- **Describe the behavior you observed** and what you expected to see
- **Include screenshots or error messages** if applicable
- **Specify your environment**: OS, Python version, dependency versions

**Bug Report Template:**

```markdown
**Description:**
A clear description of the bug.

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
What you expected to happen.

**Actual Behavior:**
What actually happened.

**Environment:**
- OS: [e.g., Ubuntu 22.04, Windows 11]
- Python version: [e.g., 3.9.7]
- Package versions: [run `pip freeze`]

**Additional Context:**
Any other relevant information.
```

### Suggesting Enhancements

Enhancement suggestions are welcome! When suggesting an enhancement:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful** to most users
- **List any similar tools or features** for reference
- **Provide examples** of how it would work

### Contributing Code

We love code contributions! Here are the areas where you can help:

#### Detection Rules
- Add new suspicious character patterns
- Improve Unicode category detection
- Enhance font anomaly detection algorithms

#### Features
- Add new analysis capabilities
- Improve the web UI
- Add export formats (CSV, HTML reports, etc.)
- Batch processing improvements

#### Performance
- Optimize character extraction
- Speed up font analysis
- Reduce memory usage for large PDFs

#### Documentation
- Improve README examples
- Add code comments
- Create tutorials or guides
- Translate documentation

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/pdf-ligature-stego-sniffer.git
cd pdf-ligature-stego-sniffer
```

### 2. Create a Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Using conda
conda create -n pdf-stego python=3.9
conda activate pdf-stego
```

### 3. Install Dependencies

```bash
# Install all dependencies including dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some flexibility:

- **Line length**: 100 characters (not strict 79)
- **Quotes**: Use double quotes for strings
- **Indentation**: 4 spaces (no tabs)
- **Naming**:
  - Functions and variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`

### Code Formatting

We use `black` for automatic formatting:

```bash
# Format all Python files
black .

# Check without modifying
black --check .
```

### Linting

Use `flake8` to check code quality:

```bash
flake8 core/ app/ tests/
```

### Type Hints

We encourage type hints for better code clarity:

```python
def analyze_pdf(pdf_file) -> Dict[str, Any]:
    """Analyze a PDF file for suspicious content."""
    ...
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types:
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic changes)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples:

```
feat(analyzer): add detection for Unicode category Mc

Add detection for combining marks (category Mc) which can be used
for steganography in Urdu/Arabic text.

Closes #123
```

```
fix(fonts): handle missing glyph tables gracefully

Some embedded fonts don't expose glyph tables through fontTools.
Added try-catch to prevent crashes and provide meaningful error messages.
```

```
docs(readme): add example for batch processing
```

## Pull Request Process

1. **Update Documentation**: If you've changed APIs or added features, update the README.md

2. **Add Tests**: Add tests for new features or bug fixes

3. **Run Tests**: Ensure all tests pass
   ```bash
   pytest tests/
   ```

4. **Update CHANGELOG**: Add a note about your changes (if applicable)

5. **Commit Your Changes**: Follow the commit guidelines

6. **Push to Your Fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**:
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template

### Pull Request Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have updated the documentation accordingly
- [ ] I have added tests that prove my fix is effective or my feature works
- [ ] New and existing unit tests pass locally
- [ ] Any dependent changes have been merged and published

## Related Issues
Closes #issue_number
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=app tests/

# Run specific test file
pytest tests/test_analyzer.py

# Run specific test
pytest tests/test_analyzer.py::test_find_suspicious_characters
```

### Writing Tests

Place tests in the `tests/` directory. Follow the naming convention:

```
tests/
├── test_analyzer.py
├── test_fonts.py
└── test_integration.py
```

Test function naming:

```python
def test_function_name_scenario():
    """Test that function handles scenario correctly."""
    # Arrange
    input_data = ...
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result == expected_value
```

### Test Coverage

We aim for >80% test coverage. Check coverage with:

```bash
pytest --cov=core --cov=app --cov-report=html tests/
# Open htmlcov/index.html in browser
```

## Documentation

### Code Comments

- Use docstrings for all public functions, classes, and modules
- Follow [PEP 257](https://pep257.readthedocs.io/) docstring conventions
- Include examples in docstrings when helpful

Example:

```python
def find_suspicious_characters(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identify suspicious or invisible characters in PDF records.
    
    Searches for zero-width characters, directional marks, and format controls
    that could be used for steganography.
    
    Args:
        records: List of character records from iter_pdf_chars()
        
    Returns:
        List of suspicious character records with page, codepoint, and position
        
    Example:
        >>> records = iter_pdf_chars("document.pdf")
        >>> suspicious = find_suspicious_characters(records)
        >>> print(f"Found {len(suspicious)} suspicious characters")
    """
    ...
```

### README Updates

When adding features:
1. Update the Features section
2. Add usage examples
3. Update the API documentation if applicable
4. Add to the Table of Contents if adding a major section

## Questions?

Don't hesitate to ask questions by:
- Opening an issue with the "question" label
- Starting a discussion in GitHub Discussions (if enabled)
- Reaching out to maintainers

## Recognition

Contributors will be recognized in:
- The project README (if significant contributions)
- Release notes
- Git commit history

Thank you for contributing! 🙏
