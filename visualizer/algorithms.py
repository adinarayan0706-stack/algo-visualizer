"""Sorting algorithms written as *generators*, so a UI can step through them.

Every algorithm sorts the list **in place** and yields a tuple
``(compared, written)`` after each elementary operation:

* ``compared`` - indices that were just compared (may be empty)
* ``written``  - indices whose values were just changed (may be empty)

To add a new algorithm: write a generator with that signature and register
it in ``ALGORITHMS`` and ``COMPLEXITY`` at the bottom of this file.
"""
from __future__ import annotations

from typing import Callable, Dict, Iterator, List, Optional, Tuple

Step = Tuple[Tuple[int, ...], Tuple[int, ...]]
Algorithm = Callable[[List[int]], Iterator[Step]]


def bubble_sort(a: List[int]) -> Iterator[Step]:
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            yield (j, j + 1), ()
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
                yield (), (j, j + 1)
        if not swapped:
            break


def selection_sort(a: List[int]) -> Iterator[Step]:
    n = len(a)
    for i in range(n - 1):
        smallest = i
        for j in range(i + 1, n):
            yield (smallest, j), ()
            if a[j] < a[smallest]:
                smallest = j
        if smallest != i:
            a[i], a[smallest] = a[smallest], a[i]
            yield (), (i, smallest)


def insertion_sort(a: List[int]) -> Iterator[Step]:
    for i in range(1, len(a)):
        j = i
        while j > 0:
            yield (j - 1, j), ()
            if a[j - 1] > a[j]:
                a[j - 1], a[j] = a[j], a[j - 1]
                yield (), (j - 1, j)
                j -= 1
            else:
                break


def merge_sort(a: List[int]) -> Iterator[Step]:
    yield from _merge_sort(a, 0, len(a) - 1)


def _merge_sort(a: List[int], lo: int, hi: int) -> Iterator[Step]:
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    yield from _merge_sort(a, lo, mid)
    yield from _merge_sort(a, mid + 1, hi)

    left, right = a[lo:mid + 1], a[mid + 1:hi + 1]
    i = j = 0
    k = lo
    while i < len(left) and j < len(right):
        yield (lo + i, mid + 1 + j), ()
        if left[i] <= right[j]:
            a[k] = left[i]
            i += 1
        else:
            a[k] = right[j]
            j += 1
        yield (), (k,)
        k += 1
    while i < len(left):
        a[k] = left[i]
        i += 1
        yield (), (k,)
        k += 1
    while j < len(right):
        a[k] = right[j]
        j += 1
        yield (), (k,)
        k += 1


def quick_sort(a: List[int]) -> Iterator[Step]:
    # Iterative (explicit stack) so sorted input can't hit the recursion limit.
    stack = [(0, len(a) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            yield (j, hi), ()
            if a[j] < pivot:
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    yield (), (i, j)
                i += 1
        if i != hi:
            a[i], a[hi] = a[hi], a[i]
            yield (), (i, hi)
        stack.append((lo, i - 1))
        stack.append((i + 1, hi))


def heap_sort(a: List[int]) -> Iterator[Step]:
    n = len(a)

    def sift_down(root: int, end: int) -> Iterator[Step]:
        while True:
            child = 2 * root + 1
            if child >= end:
                return
            if child + 1 < end:
                yield (child, child + 1), ()
                if a[child] < a[child + 1]:
                    child += 1
            yield (root, child), ()
            if a[root] < a[child]:
                a[root], a[child] = a[child], a[root]
                yield (), (root, child)
                root = child
            else:
                return

    for start in range(n // 2 - 1, -1, -1):
        yield from sift_down(start, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        yield (), (0, end)
        yield from sift_down(0, end)


# name -> generator function (order = order shown in the UI)
ALGORITHMS: Dict[str, Algorithm] = {
    "Bubble Sort": bubble_sort,
    "Selection Sort": selection_sort,
    "Insertion Sort": insertion_sort,
    "Merge Sort": merge_sort,
    "Quick Sort": quick_sort,
    "Heap Sort": heap_sort,
}

# name -> (best, average, worst, extra space)
COMPLEXITY: Dict[str, Tuple[str, str, str, str]] = {
    "Bubble Sort": ("O(n)", "O(n²)", "O(n²)", "O(1)"),
    "Selection Sort": ("O(n²)", "O(n²)", "O(n²)", "O(1)"),
    "Insertion Sort": ("O(n)", "O(n²)", "O(n²)", "O(1)"),
    "Merge Sort": ("O(n log n)", "O(n log n)", "O(n log n)", "O(n)"),
    "Quick Sort": ("O(n log n)", "O(n log n)", "O(n²)", "O(log n)"),
    "Heap Sort": ("O(n log n)", "O(n log n)", "O(n log n)", "O(1)"),
}


def find_algorithm(query: str) -> Optional[str]:
    """Resolve 'quick', 'Quick Sort', 'quick_sort' ... to a key of ALGORITHMS."""
    q = query.strip().lower().replace("_", " ").replace("-", " ")
    for name in ALGORITHMS:
        if q in (name.lower(), name.split()[0].lower()):
            return name
    return None
