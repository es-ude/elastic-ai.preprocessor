# Equivalence Framework

A Python testing framework for validating that C and Python implementations of functions produce identical results. This framework uses CFFI (C Foreign Function Interface) to dynamically load C code and compare outputs with Python implementations.

## Overview

It provides two flexible loading strategies:

- **CompileLoader**: Compile C code on-the-fly during test runtime (ideal for development)
- **PrecompiledLoader**: Load pre-built shared libraries (ideal for production/stable code)

## Installation & Setup

### Prerequisites

- Python 3.13+
- A C compiler (gcc/clang)
- `uv` package manager

### Step 1: Install `uv`

If you don't have `uv` installed, install it with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on macOS using Homebrew:

```bash
brew install uv
```

Verify the installation:

```bash
uv --version
```

### Step 2: Install Dependencies

This project uses `pyproject.toml` to manage dependencies. Install them with:

```bash
uv sync
```

This command:

- Creates a virtual environment
- Installs all dependencies: `cffi`, `hypothesis`, `pytest`
- Makes the project ready for development and testing

### Step 3: Verify Setup

Test that everything is working:

```bash
uv run pytest tests/ -v
```

You should see the existing tests run successfully.

## Project Structure

```
.
├── README.md                          # This file
├── pyproject.toml                    # Project configuration & dependencies
├── src/
│   ├── __init__.py
│   ├── loader.py                     # CompileLoader & PrecompiledLoader
│   └── equivalence.py                # compare_values() for output validation
├── c_funcs/
│   ├── add.c / add.h                 # Simple integer addition
│   ├── clamp.c / clamp.h             # Value clamping function
│   └── windower/
│       ├── windower.c / windower.h   # Sliding window data structure
├── tests/
│   ├── test_equivalence_example.py   # Basic equivalence test
│   ├── test_clamp_property.py        # Property-based tests with Hypothesis
│   ├── test_windower.py              # Complex struct comparison
│   ├── test_intentional_fail.py      # Demonstrates test failure reporting
│   └── conftest.py                   # pytest fixtures (if needed)
```

## Quick Start: CompileLoader (On-the-Fly Compilation)

**Use CompileLoader** when you're actively developing C code and want automatic compilation during test runs.

### Workflow

1. Write C code in `c_funcs/`
2. Instantiate `CompileLoader` with header and source paths
3. Call `load()` to compile on-the-fly
4. Retrieve functions and start testing

### Example: Testing the `add()` function

Create a new test file `tests/test_add_compile.py`:

```python
from src.loader import CompileLoader
from src.equivalence import compare_values

# Initialize the loader with source and header files
loader = CompileLoader(
    header_path="c_funcs/add.h",
    source_paths=["c_funcs/add.c"]
)

# Load the C library (triggers compilation)
lib = loader.load()

# Retrieve the C function
c_add = loader.get("add")

def test_add_basic():
    """Test basic addition equivalence."""
    result_c = c_add(5, 7)
    expected = 5 + 7
    assert result_c == expected, f"Expected {expected}, got {result_c}"

def test_add_edge_cases():
    """Test edge cases."""
    test_cases = [
        (0, 0, 0),
        (-5, 5, 0),
        (1000000, 1000000, 2000000),
    ]
    for a, b, expected in test_cases:
        result = c_add(a, b)
        assert result == expected, f"add({a}, {b}) = {result}, expected {expected}"
```

Run the test:

```bash
uv run pytest tests/test_add_compile.py -v
```

### Example: Testing the `clamp()` function with property-based testing

Create `tests/test_clamp_compile.py`:

```python
from hypothesis import given, strategies as st
from src.loader import CompileLoader

# Load the clamp function
loader = CompileLoader(
    header_path="c_funcs/clamp.h",
    source_paths=["c_funcs/clamp.c"]
)
lib = loader.load()
c_clamp = loader.get("clamp_int")

def py_clamp(value, lower, upper):
    """Python reference implementation."""
    return max(lower, min(upper, value))

@given(
    value=st.integers(min_value=-1000, max_value=1000),
    lower=st.integers(min_value=-1000, max_value=500),
    upper=st.integers(min_value=500, max_value=1000)
)
def test_clamp_equivalence(value, lower, upper):
    """Test that C clamp matches Python implementation across many cases."""
    # Adjust so lower <= upper
    lower_adj = min(lower, upper)
    upper_adj = max(lower, upper)

    py_result = py_clamp(value, lower_adj, upper_adj)
    c_result = c_clamp(value, lower_adj, upper_adj)

    assert py_result == c_result, (
        f"Mismatch: clamp({value}, {lower_adj}, {upper_adj}) "
        f"Python={py_result}, C={c_result}"
    )
```

Run property-based tests:

```bash
uv run pytest tests/test_clamp_compile.py -v
```

Hypothesis will generate 100+ test cases automatically.

## Quick Start: PrecompiledLoader (Pre-Built Libraries)

**Use PrecompiledLoader** when you have a stable, pre-compiled C library (`.so` on Linux, `.dll` on Windows, `.dylib` on macOS).

### Prerequisites

Your C library must be pre-compiled. For example, using `gcc`:

```bash
# Compile to a shared library
gcc -shared -fPIC -o c_funcs/libadd.so c_funcs/add.c
gcc -shared -fPIC -o c_funcs/libclamp.so c_funcs/clamp.c
gcc -shared -fPIC -o c_funcs/windower/libwindower.so c_funcs/windower/windower.c
```

### Example: Testing with a pre-built library

Create `tests/test_add_precompiled.py`:

```python
from src.loader import PrecompiledLoader
from src.equivalence import compare_values

# Point to the pre-built .so file and the header
loader = PrecompiledLoader(
    library_path="c_funcs/libadd.so",
    header_path="c_funcs/add.h"
)

# Load the pre-compiled library
lib = loader.load()

# Retrieve the C function
c_add = loader.get("add")

def test_add_with_precompiled():
    """Test add function using pre-compiled library."""
    for a in range(-100, 101, 10):
        for b in range(-100, 101, 10):
            expected = a + b
            result = c_add(a, b)
            assert result == expected, f"add({a}, {b}) = {result}, expected {expected}"
```

Run the test:

```bash
uv run pytest tests/test_add_precompiled.py -v
```

### Quick Decision Guide

Choose **CompileLoader** if:

- You're actively modifying C code
- You want fast iteration and immediate feedback
- You don't want to manually manage build steps

Choose **PrecompiledLoader** if:

- Your C code is stable and production-ready
- You have pre-compiled binaries available
- You want faster test startup times
- You're building in CI/CD where compilation is separate

## Examples & References

Existing test files in this repository demonstrate different patterns:

### Basic Equivalence Test

See [tests/test_equivalence_example.py](tests/test_equivalence_example.py)

- Simple function calls with specific inputs
- Demonstrates PrecompiledLoader usage

### Property-Based Testing

See [tests/test_clamp_property.py](tests/test_clamp_property.py)

- Uses Hypothesis to generate test cases automatically
- Tests mathematical properties (clamp is idempotent)

### Complex State Comparison

See [tests/test_windower.py](tests/test_windower.py)

- Tests stateful C structs against Python implementations
- Demonstrates FFI struct creation and access
  ! DOESNT WORK RIGHT NOW -- IGNORE -- !

### Intentional Failure Example

See [tests/test_intentional_fail.py](tests/test_intentional_fail.py)

- Shows how the framework reports test failures

## Best Practices

### 1. Always Implement a Python Reference Function

```python
def python_function(x, y):
    """Python implementation (source of truth)."""
    return x + y
```

### 2. Test Edge Cases and Boundaries

```python
test_cases = [
    (0, 0),                          # Zero case
    (-MAX_INT, MAX_INT),             # Boundary
    (-1, -1),                        # Negative
    (1, 1),                          # Positive
]
```

### 3. Use Property-Based Testing for Coverage

```python
@given(x=st.integers(), y=st.integers())
def test_property(x, y):
    assert c_func(x, y) == py_func(x, y)
```

Hypothesis generates 100+ test cases automatically. It's more thorough than manual test cases.

### 4. Use `compare_values()` for Floats

Don't use `==` for floating-point comparisons:

```python
# ❌ Wrong
assert result == 3.14159265858979

# ✅ Correct
matches, reason = compare_values(result, 3.14159265858979, abs_tol=1e-9)
assert matches, reason
```

### 5. Document Non-Obvious Required Compilation

If your test file requires pre-compilation:

```python
"""Test the add function (requires: gcc -shared -fPIC -o c_funcs/libadd.so c_funcs/add.c)"""
```

## Troubleshooting

### Issue: "No module named 'src'"

**Cause**: pytest can't find the `src` package.

**Solution**: Ensure `pyproject.toml` has:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
```

Then run tests from the project root:

```bash
cd /path/to/function_equivalence_test
uv run pytest tests/
```

### Issue: "cannot find -lsomething" (CompileLoader)

**Cause**: C compiler can't find a required header or library.

**Solution**:

- Check that header files exist at the paths you specified
- Use absolute paths if relative paths fail
- Verify header syntax with `gcc -c your_header.h`

### Issue: "error: cannot find library libexample.so" (PrecompiledLoader)

**Cause**: The `.so` file doesn't exist or path is wrong.

**Solution**:

1. Verify the library exists:

    ```bash
    ls -la c_funcs/libexample.so
    ```

2. Pre-compile it:

    ```bash
    gcc -shared -fPIC -o c_funcs/libexample.so c_funcs/example.c
    ```

3. Use an absolute path if relative fails:
    ```python
    loader = PrecompiledLoader(
        library_path="/absolute/path/to/libexample.so",
        header_path="c_funcs/example.h"
    )
    ```

### Issue: "ModuleNotFoundError: No module named 'cffi', 'hypothesis', 'pytest'"

**Cause**: Dependencies aren't installed.

**Solution**: Run `uv sync` again:

```bash
uv sync
uv run pytest tests/
```
