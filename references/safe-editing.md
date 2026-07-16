# Backslash-Heavy Content: Safe Edit Workflow

Backslash-heavy regular expressions, shell fragments, and configuration strings
are easy to corrupt when text passes through multiple parsers. The risk depends
on the editing interface, shell, programming language, and target syntax; do not
assume that any one tool always adds or removes escapes.

## Safe Workflow

1. **Inspect the exact target text.** Read the smallest useful region and
   identify which layers will interpret it: edit interface, shell, language
   literal, and regex or replacement engine.
2. **Prefer a structured patch or editor operation.** Match surrounding context
   and change only the intended lines. Avoid whole-file rewrites for a small
   escape-sensitive change.
3. **Use literal-safe quoting.** In Python, raw strings help with regex patterns
   but cannot end in a single backslash. In POSIX shells, single quotes preserve
   literal characters except a single quote itself. Account separately for the
   target regex or replacement syntax.
4. **Avoid in-place `sed` for portable automation.** GNU and BSD `sed -i` use
   different syntax. Prefer a project-native formatter, a structured edit, or a
   small reviewed script when portability matters.
5. **Review the diff immediately.** Confirm that only intended bytes and lines
   changed before running broader verification.

## Focused Python Transformation

When a structured edit is unavailable and an exact transformation is clearer in
Python, keep the operation explicit and fail if the expected input is absent or
ambiguous:

```python
from pathlib import Path

path = Path("path/to/file")
text = path.read_text(encoding="utf-8")
old = r"expected literal text"
new = r"replacement literal text"

if text.count(old) != 1:
    raise SystemExit(f"expected exactly one match, found {text.count(old)}")

path.write_text(text.replace(old, new), encoding="utf-8")
```

Use this only when file writes are authorized by the active environment and the
repository has no preferred editing mechanism. Preserve the original encoding
and line-ending policy.

## Byte-Level Diagnostic

If visual review is ambiguous, inspect a narrow region as bytes with Python:

```python
from pathlib import Path

data = Path("path/to/file").read_bytes()
start = data.find(b"nearby unique marker")
if start < 0:
    raise SystemExit("marker not found")
print(data[start : start + 80].hex(" "))
```

Useful byte values include `5c` for backslash, `28` for `(`, and `29` for `)`.
Do not dump an entire file that may contain credentials or other sensitive
content.

## Verification Checklist

- The expected source text existed exactly where intended.
- The resulting diff contains no doubled, dropped, or newly interpreted escapes.
- The file still follows its repository line-ending and encoding policy.
- The smallest relevant parser, syntax, or project-native test passes.
- No temporary backup or generated file remains in the working tree.
