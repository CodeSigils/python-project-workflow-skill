# Core Python Footguns

Common Python pitfalls, ordered by frequency. This is a quick reference for awareness —
not a code review checklist. For structured code review rules with impact levels and
code examples, install [nathan-gage/python-skills](https://github.com/nathan-gage/python-skills).

> **Note:** Items covered by nathan-gage/python-skills (mutable defaults, context managers,
> bare `except:`) are omitted here — that skill has more thorough treatment with impact
> levels and code examples.

## Late Binding in Closures

Loop variables captured by closures reference the final value, not the value at capture time.

```python
funcs = []
for i in range(5):
    funcs.append(lambda: i)   # all return 4

# Fix with default argument or functools.partial
for i in range(5):
    funcs.append(lambda i=i: i)
```

## `__init__` vs `__new__`

- `__new__` is a static method that creates the instance (rarely overridden)
- `__init__` initializes the already-created instance
- If you override `__new__`, you usually also need `__init__`

## `is` vs `==`

- `is` is identity (same object in memory)
- `==` is equality (value comparison)
- Use `is` for `None`, `True`, `False`, and sentinels
- Use `==` for value comparison (numbers, strings, etc.)

## Float Equality

Floating-point arithmetic produces small rounding errors. Use `math.isclose()` or a tolerance:

```python
import math
math.isclose(a, b, rel_tol=1e-9)
```

## Mutating a List While Iterating

Iterate over a copy instead:

```python
for item in list(original):   # iterate over a copy
    if condition(item):
        original.remove(item)

# Or use a list comprehension
original = [x for x in original if not condition(x)]
```

## `import *`

Pollutes the namespace, obscures where names come from, triggers linters. Use explicit imports.

## Dict Ordering (Pre-3.7)

Before CPython 3.6 / Python 3.7, dict insertion order was not guaranteed. If order matters for older Pythons, use `OrderedDict`.

## String Concatenation in Loops

```python
# WRONG - O(n^2)
s = ""
for chunk in chunks:
    s += chunk

# RIGHT - O(n)
parts = []
for chunk in chunks:
    parts.append(chunk)
result = "".join(parts)
```

## `IOError` is `OSError`

Since Python 3.3 (PEP 3151), `IOError` was merged into `OSError`. Catching both is redundant:

```python
# Wrong (redundant since 3.3)
except (IOError, OSError):

# Right
except OSError:
```

## Guard-Condition Ordering: Classify Before Allow-List

When filtering items that need both a structural classification (what IS this thing?) and an allow-list check (is it one of the known exceptions?), apply the structural check first:

```python
# WRONG — allow-list check before structural classification
if key in ALLOWED_TRAILERS:
    continue              # ← prematurely accepts things that also match
if not key.endswith("-by"):
    continue

# RIGHT — structural classification first, then allow-list
if not key.endswith("-by"):
    continue              # ← skip anything that isn't a -by trailer
if key in ALLOWED_TRAILERS:
    continue              # ← now this is safe
violations.append(trailer)
```

The one-line mnemonic: **"What is it?" before "Is it allowed?"**

## Shared Config Duplication Across Sibling Scripts

When two or more Python scripts define the same hardcoded paths, file lists, or configuration values, each copy is a drift surface. Different names (`MISSING_FILES` vs `KEY_FILES`) across files can conceal the duplication.

**Fix:** extract shared values to a `_paths.py` or `_config.py` module imported by all scripts.

## Review Sibling Scripts After Editing

If you changed one Python script, also review its immediate siblings in the same directory — especially scripts that share constants, are called via `subprocess.run`, or implement complementary functions. A `ROOT = Path(".")` or `SCRIPT_DIR` defined independently in two sibling scripts is a drift surface that a single-file review misses.

## Threading and Multiprocessing Pitfalls

- **Threading:** GIL, race conditions on shared state, deadlocks
- **Multiprocessing:** pickling issues for shared objects, state synchronization
- Prefer `concurrent.futures` for straightforward parallelism
