import os
import random
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from visualizer.algorithms import ALGORITHMS, find_algorithm  # noqa: E402

CASES = {
    "empty": [],
    "single": [1],
    "two": [2, 1],
    "sorted": list(range(1, 61)),
    "reversed": list(range(60, 0, -1)),
    "duplicates": [3, 1, 3, 2, 1, 2, 3, 3, 1],
    "all_equal": [5] * 20,
    "random": random.Random(42).sample(range(1, 201), 100),
}


@pytest.mark.parametrize("name", list(ALGORITHMS))
@pytest.mark.parametrize("case", list(CASES))
def test_sorts_correctly(name, case):
    data = list(CASES[case])
    for _ in ALGORITHMS[name](data):
        pass
    assert data == sorted(CASES[case])


@pytest.mark.parametrize("name", list(ALGORITHMS))
def test_steps_are_well_formed(name):
    data = random.Random(1).sample(range(1, 51), 50)
    n = len(data)
    steps = 0
    for compared, written in ALGORITHMS[name](data):
        steps += 1
        assert isinstance(compared, tuple) and isinstance(written, tuple)
        assert all(0 <= i < n for i in compared + written)
    assert steps > 0


@pytest.mark.parametrize("name", list(ALGORITHMS))
def test_is_a_permutation_throughout(name):
    data = random.Random(7).sample(range(1, 31), 30)
    expected = sorted(data)
    for _ in ALGORITHMS[name](data):
        pass
    assert sorted(data) == expected


def test_find_algorithm():
    assert find_algorithm("quick") == "Quick Sort"
    assert find_algorithm("Merge Sort") == "Merge Sort"
    assert find_algorithm("heap_sort") == "Heap Sort"
    assert find_algorithm("nope") is None
