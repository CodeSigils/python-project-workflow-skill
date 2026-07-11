# Backslash-Heavy Content: Safe Edit Workflow

Editing files with dense backslash patterns (e.g. sed BRE capture groups `\(...\)`, grep ERE, or shell regex) is a recurring corruption site. Three independent layers each interpret backslashes differently:

| Layer | `\(` becomes | Mechanism |
|-------|-------------|-----------|
| `patch` tool `old_string`/`new_string` | `\\(` (doubled) | Tool applies its own escape pass |
| Python regular string `"\\([^}]*\\)"` | `\([^}]*\)` (correct) | `\\\\` -> `\\`, `\(` -> `(` |
| Python raw string `r"\([^}]*\)"` | `\([^}]*\)` (correct) | Raw = literal |

**The core problem:** no single reliable escape-free path through `patch` or Python strings for backslash-heavy content.

## Safe Workflow (Ranked by Reliability)

### 1. First Resort: Python stdlib read/write

Use Python stdlib — open the file, read, replace, write — zero escaping layers:

```python
# Read raw file (no escaping, no format wrapping)
with open("/path/to/file") as f:
    content = f.read()

# Python string replacement — backslashes in your replacement are literal
content = content.replace(
    'old_backslash_pattern',   # literal bytes from the file
    'new_backslash_pattern'    # literal bytes you want
)

# Write back
with open("/path/to/file", "w") as f:
    f.write(content)
```

Use raw strings `r'...'` so Python doesn't process the backslashes. Verify the result with `od -A x -t x1z | grep '5c'` (see Diagnostic below).

### 2. Second Resort: `sed -i` in Single Quotes

Bash single quotes preserve backslashes literally — zero unexpected escaping:

```bash
# Replace `\(` with `\(` (correct BRE capture group)
sed -i 's/\(/\(/g' file
```

### 3. Third Resort: Python Byte-Level (Binary Mode)

When the edit is too complex for `sed` but `write_file` from `terminal("cat")` has issues, use binary I/O with explicit hex escapes:

```python3 << 'PYEOF'
data = open('file', 'rb').read()
data = data.replace(b"\x5c\x28", b"\x5c\x29")  # \( and \)
open('file', 'wb').write(data)
PYEOF
```

Note: `b"\x5c\x28"` is hex value 0x5c (backslash), 0x28 (open paren) — no backslash escaping confusion.

### 4. Diagnostic: Verify Bytes Before and After Every Backslash Edit

```bash
# Before editing
sed -n '<LINE_NUM>p' <file> | od -A x -t x1z | grep '5c'

# After editing — confirm single not doubled:
#   5c 28 = \( (correct)
#   5c 5c 28 = two backslashes + paren (doubled)
sed -n '<LINE_NUM>p' <file> | od -A x -t x1z | grep '5c'
```

> **Note:** `xxd` (Linux vim package) is not available on all systems.
> `od -A x -t x1z` is POSIX and works on Linux, macOS, and other Unix systems.

### sed -i Portability

The `sed -i` flag differs between GNU sed (Linux) and BSD sed (macOS):

- GNU: `sed -i 's/old/new/g' file` (in-place, no backup)
- BSD: `sed -i '' 's/old/new/g' file` (requires empty backup extension)

Portable form: use `sed -i.bak` (creates a `file.bak` backup on both), or use Python for in-place edits.
