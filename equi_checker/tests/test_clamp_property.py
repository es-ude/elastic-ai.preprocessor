from hypothesis import given, strategies as st

from equi_checker.src.loader import CompileLoader


def py_clamp_int(value: int, lower: int, upper: int) -> int:
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


loader = CompileLoader(
    headers="./c_funcs/clamp/clamp.h",
    sources=["./c_funcs/clamp/clamp.c"],
    build_dir="build_test_clamp",
    module_name="c_clamp",
)
loader.load()
c_clamp_int = loader.get("clamp_int")


@given(
    value=st.integers(min_value=-10_000, max_value=10_000),
    lower=st.integers(min_value=-10_000, max_value=10_000),
    upper=st.integers(min_value=-10_000, max_value=10_000),
)
def test_clamp_equivalence_property(value: int, lower: int, upper: int):
    if lower > upper:
        lower, upper = upper, lower

    py_result = py_clamp_int(value, lower, upper)
    c_result = c_clamp_int(value, lower, upper)

    assert py_result == c_result


@given(
    value=st.integers(min_value=-10_000, max_value=10_000),
    lower=st.integers(min_value=-10_000, max_value=10_000),
    upper=st.integers(min_value=-10_000, max_value=10_000),
)
def test_clamp_range_property(value: int, lower: int, upper: int):
    if lower > upper:
        lower, upper = upper, lower

    result = c_clamp_int(value, lower, upper)

    assert lower <= result <= upper


@given(
    value=st.integers(min_value=-10_000, max_value=10_000),
    lower=st.integers(min_value=-10_000, max_value=10_000),
    upper=st.integers(min_value=-10_000, max_value=10_000),
)
def test_clamp_idempotence_property(value: int, lower: int, upper: int):
    if lower > upper:
        lower, upper = upper, lower

    once = c_clamp_int(value, lower, upper)
    twice = c_clamp_int(once, lower, upper)

    assert once == twice
