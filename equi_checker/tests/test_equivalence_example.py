from pathlib import Path
import subprocess

from src.loader import PrecompiledLoader, CompileLoader

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "c_funcs" / "adder"
HEADER = FIXTURE_DIR / "add.h"
SOURCE = FIXTURE_DIR / "add.c"
PRECOMPILED_BUILD_DIR = FIXTURE_DIR / "build_precompiled"
PRECOMPILED_LIBRARY = PRECOMPILED_BUILD_DIR / "libadd.so"

# --- python implementation ---
def add(a, b):
    return a + b


# --- precompiled version ---

PRECOMPILED_BUILD_DIR.mkdir(exist_ok=True)
subprocess.run(
    ["cc", "-shared", "-fPIC", "-o", str(PRECOMPILED_LIBRARY), str(SOURCE)],
    check=True,
)

loader = PrecompiledLoader(
    library_path=str(PRECOMPILED_LIBRARY), headers=str(HEADER)
)

lib = loader.load()  # returns the loaded shared library

c_add = loader.get("add")  # alternatively: lib.add


def test_equivalence_precompiled():
    a = 5
    b = 7
    assert add(a, b) == c_add(a, b)


# --- compiled version ---

compile_loader = CompileLoader(
    headers=str(HEADER),
    sources=[str(SOURCE)],
    build_dir=str(FIXTURE_DIR / "build_compile_loader"),
)

lib2 = compile_loader.load()  # compiles the C code and returns a library

c_add2 = compile_loader.get("add")  # alternatively: lib2.add


def test_equivalence_compiled():
    a = 10
    b = 15
    assert add(a, b) == c_add2(a, b)
