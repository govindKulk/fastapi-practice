"""
    Sample tests for math operations.
    My first pytest test.
"""
import pytest
from app.core.math_operations import add, subtract


@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_add(a: int, b: int, expected: int):
    assert add(a, b) == expected

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 0) == 0
    assert subtract(-1, -1) == 0