# Code Extraction Best Practices in Python

## Overview

This document outlines best practices for extracting, analyzing, and working with code in Python applications. It covers
techniques for static analysis, code transformation, and safe code manipulation that are relevant to building developer
tools and agent skills.

## Key Areas

### 1. Abstract Syntax Tree (AST) Manipulation

Python's `ast` module provides powerful capabilities for analyzing and transforming code safely.

**Best Practices:**

- Always use `ast.parse()` with `mode='exec'` for modules, `mode='eval'` for expressions, and `mode='single'` for
  interactive statements
- Use `ast.NodeVisitor` or `ast.NodeTransformer` for traversing and modifying ASTs
- Preserve line numbers and column offsets when transforming nodes for better error reporting
- Use `ast.fix_missing_locations()` after tree modifications
- Consider using `ast.unparse()` (Python 3.9+) for converting AST back to source code
- For older Python versions, use `astor` or `blackd` for unparsing

**Example:**

```python
import ast
import sys

def extract_function_calls(code):
    """Extract all function calls from Python code."""
    tree = ast.parse(code)
    calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Get the function being called
            if isinstance(node.func, ast.Name):
                calls.append({
                    'func': node.func.id,
                    'args': [ast.unparse(arg) for arg in node.args],
                    'keywords': {kw.arg: ast.unparse(kw.value) for kw in node.keywords},
                    'lineno': node.lineno,
                    'col_offset': node.col_offset
                })
            elif isinstance(node.func, ast.Attribute):
                calls.append({
                    'func': f"{ast.unparse(node.func.value)}.{node.func.attr}",
                    'args': [ast.unparse(arg) for arg in node.args],
                    'keywords': {kw.arg: ast.unparse(kw.value) for kw in node.keywords},
                    'lineno': node.lineno,
                    'col_offset': node.col_offset
                })

    return calls
```

### 2. Tokenization for Precise Text Manipulation

When you need to make precise text changes while preserving formatting, use the `tokenize` module.

**Best Practices:**

- Use `tokenize.generate_tokens()` to convert source to tokens
- Modify token strings carefully, preserving token types
- Use `tokenize.untokenize()` to convert back to source
- Always work with logical lines, not physical lines
- Preserve whitespace and comments when possible
- Handle encoding declarations properly

**Example:**

```python
import tokenize
import io

def rename_variable(source, old_name, new_name):
    """Rename a variable in source code while preserving formatting."""
    result = []
    g = tokenize.generate_tokens(io.StringIO(source).readline)

    for toknum, tokval, _, _, _ in g:
        if toknum == tokenize.NAME and tokval == old_name:
            result.append((toknum, new_name))
        else:
            result.append((toknum, tokval))

    return tokenize.untokenize(result)
```

### 3. Regular Expressions with Caution

While regex can be useful for simple patterns, avoid using it for complex code manipulation.

**Best Practices:**

- Only use regex for simple, well-defined patterns (e.g., finding TODO comments)
- Never use regex to parse Python syntax - use AST instead
- Compile regex patterns with `re.compile()` for reuse
- Use verbose flag (`re.VERBOSE`) for complex patterns
- Consider using the `regex` module for advanced features
- Always test regex against a variety of code samples

**Appropriate Uses:**

- Finding comment patterns: `# TODO:`, `# FIXME:`, `# HACK:`
- Extracting simple metadata: `__version__ = "1.0.0"`
- Matching specific import patterns: `from .module import *`
- Detecting specific function call patterns with known signatures

### 4. File Discovery and Processing

Safely discovering and processing Python files in a project.

**Best Practices:**

- Use `pathlib.Path` for cross-platform path handling
- Respect `.gitignore` patterns when discovering files
- Use pathspec library or pathspec-like functionality for ignore patterns
- Process files in a deterministic order (sorted by path)
- Handle encoding explicitly (UTF-8 default, but detect when needed)
- Skip binary files and virtual environment directories
- Consider file size limits to prevent memory issues
- Use try/except blocks for individual file processing to continue on errors

**Example:**

```python
from pathlib import Path
import pathspec

def find_python_files(root_dir, ignore_patterns=None):
    """Find all Python files respecting ignore patterns."""
    root = Path(root_dir)

    # Default ignore patterns
    default_patterns = [
        '**/__pycache__/**',
        '**/.*',
        '**/build/**',
        '**/dist/**',
        '**/*.egg-info/**',
        '**/venv/**',
        '**/.env/**',
        '**/.git/**'
    ]

    if ignore_patterns:
        default_patterns.extend(ignore_patterns)

    spec = pathspec.PathSpec.from_lines('gitwildmatch', default_patterns)

    python_files = []
    for file_path in root.rglob('*.py'):
        # Convert to relative path for matching
        try:
            rel_path = file_path.relative_to(root)
            if not spec.match_file(rel_path):
                python_files.append(file_path)
        except ValueError:
            # Path is not relative to root (shouldn't happen with rglob)
            continue

    return sorted(python_files)
```

### 5. Safe Code Execution and Testing

When extracting code snippets for analysis or testing.

**Best Practices:**

- Never execute untrusted code directly
- Use restricted execution environments if execution is necessary
- Use `ast.literal_eval()` for safely evaluating literals
- For testing extracted code, use subprocesses with timeouts and resource limits
- Consider using Docker containers or virtual environments for isolation
- Capture and log execution results without exposing sensitive information
- Always clean up temporary files and processes

### 6. Dependency Analysis

Understanding and extracting dependency information from Python projects.

**Best Practices:**

- Parse `pyproject.toml` using `tomli` (Python 3.11+) or `tomllib`
- For `setup.py`, avoid direct execution - use metadata extraction tools
- Parse `requirements.txt` files with proper handling of comments and options
- Use `importlib.metadata` for installed package info (available in Python 3.8 and later)
- Consider using `pipdeptree` or `pip-tools` for dependency resolution
- Distinguish between runtime dependencies, dev dependencies, and build dependencies
- Check for dependency conflicts and version incompatibilities

**Example:**

```python
import tomli
from pathlib import Path

def extract_dependencies(pyproject_path):
    """Extract dependencies from pyproject.toml."""
    with open(pyproject_path, 'rb') as f:
        data = tomli.load(f)

    dependencies = {
        'runtime': data.get('project', {}).get('dependencies', []),
        'dev': data.get('project', {}).get('optional-dependencies', {}).get('dev', []),
        'build': data.get('build-system', {}).get('requires', [])
    }

    return dependencies
```

### 7. Import Analysis

Understanding module dependencies and import structures.

**Best Practices:**

- Use AST to find all `import` and `import from` statements
- Resolve relative imports to absolute module names when possible
- Distinguish between standard library, third-party, and local imports
- Use `importlib.util.find_spec()` to check if modules can be imported
- Consider using `modulefinder` or `zipextimporter` for complex cases
- Handle conditional imports and try/except ImportError patterns
- Track import aliases (`import module as alias`)

**Example:**

```python
import ast
from typing import Set, Tuple

def extract_imports(code) -> Set[Tuple[str, str, int]]:
    """Extract all imports from Python code.
    Returns set of (module_name, imported_name, line_number) tuples.
    """
    tree = ast.parse(code)
    imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add((alias.name, alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            level = '.' * node.level if node.level > 0 else ''
            full_module = level + module

            for alias in node.names:
                if alias.name == '*':
                    imports.add((full_module, '*', node.lineno))
                else:
                    imports.add((full_module, alias.name, node.lineno))

    return imports
```

### 8. Code Quality Metrics Extraction

Extracting metrics that indicate code quality and maintainability.

**Best Practices:**

- Cyclomatic complexity: count decision points (if, for, while, and, or, etc.)
- Maintainability index: combine lines of code, cyclomatic complexity, and Halstead volume
- Halstead metrics: operators and operands counting
- Lines of code: distinguish between logical lines, physical lines, and comment lines
- Dependency coupling: count imports and external dependencies
- Cohesion metrics: analyze how closely related methods and attributes are
- Use existing tools like `radon`, `mccabe`, or `pylint` when possible rather than reinventing

### 9. Documentation Extraction

Extracting and analyzing docstrings and comments.

**Best Practices:**

- Parse docstrings using `ast.get_docstring()` for module, class, and function docstrings
- Consider using `docstring-parser` for standardized docstring formats (Google, NumPy, Sphinx)
- Extract comment blocks that precede significant code elements
- Distinguish between docstrings and comment blocks
- Parse `__all__` lists to understand public API
- Extract type comments and inline comments when relevant
- Consider using `typing.get_type_hints()` for runtime type information

### 10. Security Considerations in Code Extraction

Ensuring that code analysis tools themselves are secure.

**Best Practices:**

- Never execute code from untrusted sources during analysis
- Sanitize file paths to prevent directory traversal attacks
- Limit file sizes to prevent DoS through large files
- Use timeouts for any external tool invocations
- Consider using sandboxes or restricted environments for any necessary execution
- Keep dependencies up to date to avoid vulnerability exposure
- Log analysis activities for audit trails
- Consider memory limits for processing large codebases

### 11. Performance Optimization

Making code extraction tools efficient for large codebases.

**Best Practices:**

- Process files in batches or streams rather than loading all into memory
- Use caching for expensive operations (AST parsing, import resolution)
- Consider incremental analysis for frequently changing codebases
- Use multiprocessing for CPU-bound tasks (AST parsing) when safe
- Implement progress reporting for long-running operations
- Use efficient data structures for storing analysis results
- Consider database storage for persistent analysis results across runs
- Profile and optimize hot paths in extraction algorithms

### 12. Integration with Development Workflows

Making extracted information useful in developer workflows.

**Best Practices:**

- Provide machine-readable output (JSON, YAML) for integration with other tools
- Consider incremental updates rather than full reanalysis
- Integrate with pre-commit hooks, CI/CD pipelines, or IDE plugins
- Provide configurable severity levels for findings
- Allow suppression of specific findings with comments or configuration
- Generate actionable reports with clear remediation steps
- Consider visualization capabilities for complex metrics
- Provide APIs or CLI interfaces for tool consumption

## Recommended Libraries and Tools

### Standard Library

- `ast`: AST parsing and manipulation
- `tokenize`: Token-level source manipulation
- `pathlib`: Cross-platform path handling
- `importlib`: Import system introspection
- `tomllib`/`tomli`: TOML parsing (PyProject)
- `typing`: Type hint introspection
- `dis`: Bytecode analysis (advanced)

### Third-Party Libraries

- `radon`: Complexity metrics
- `mccabe`: McCabe complexity checker
- `docstring-parser`: Docstring parsing
- `pathspek`: Gitignore-style pattern matching
- `blackd`/`astor`: AST to source conversion (for older Python)
- `importlib_metadata`: Package metadata (backport)
- `asttokens`: AST nodes to source text mapping
- `libcst`: Concrete syntax tree for lossless transformations
- `parso`: Python parser used by Jedi
- `lib2to3`: Python 2/3 conversion tool (can be used for analysis)

## Application to Hermes Skill Development

For the Python Best Practices Hermes skill, code extraction techniques can be applied to:

1. **Project Inspection**: Extracting metadata from `pyproject.toml`, `setup.py`, and other configuration files
2. **Code Analysis**: Identifying anti-patterns, checking for proper use of context managers, etc.
3. **Template Generation**: Creating properly formatted code snippets based on extracted patterns
4. **Verification**: Checking that suggested changes maintain the same AST structure (where appropriate)
5. **Documentation**: Ensuring docstrings follow conventions and are present where expected
6. **Dependency Analysis**: Verifying that dependencies are correctly specified and compatible
7. **Import Checking**: Ensuring imports follow project conventions and don't create circular dependencies

The key principle is to use the safest, most precise tool for each job: AST for structural analysis, tokenize for
precise text modifications, and only resort to regex for simple, well-defined patterns where the alternatives would be
over-engineering.

## References

- Python AST Documentation: https://docs.python.org/3/library/ast.html
- Python Tokenize Documentation: https://docs.python.org/3/library/tokenize.html
- "Python Cookbook" by David Beazley and Brian K. Jones (Chapter on Metaprogramming)
- "Effective Python" by Brett Slatkin (Items on introspection)
- Groner's "Astroid" library documentation (used by Pylint)
- LibCST documentation: https://libcst.readthedocs.io/
