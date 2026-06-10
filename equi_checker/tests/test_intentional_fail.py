from src.equivalence import compare_values
from src.loader import CompileLoader


def add_python_wrong(a: int, b: int) -> int:
    # Intentionally wrong implementation for demo/failure showcase.
    return a + b + 1


def test_loader_equivalence_intentional_fail():
    loader = CompileLoader(
        headers="./c_funcs/adder/add.h",
        sources=["./c_funcs/adder/add.c"],
        build_dir="build_test_add_intentional_fail",
        module_name="c_add_intentional_fail",
    )
    loader.load()

    c_add = loader.get("add")

    a, b = 5, 7
    py_result = add_python_wrong(a, b)
    c_result = c_add(a, b)

    passed, reason = compare_values(py_result, c_result)

    # Intentionally asserting equality to create a failing test.
    assert passed, f"Equivalence failed (intentional demo): {reason}"
