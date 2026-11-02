"""Drives the real GUI object on matplotlib's non-interactive Agg backend."""
import os
import sys

import matplotlib

matplotlib.use("Agg")

import pytest  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from visualizer.algorithms import ALGORITHMS  # noqa: E402
from visualizer.app import SortVisualizer  # noqa: E402


def run_to_end(viz, limit=100000):
    for _ in range(limit):
        viz._tick()
        if viz.state == "done":
            return
    raise AssertionError("visualizer never finished")


@pytest.mark.parametrize("name", list(ALGORITHMS))
def test_gui_sorts_every_algorithm(name):
    viz = SortVisualizer(name, size=30, steps_per_frame=10, seed=3)
    viz.toggle()
    run_to_end(viz)
    assert viz.data == sorted(viz.data)
    assert viz.writes > 0 or name == "Insertion Sort" or viz.comparisons > 0
    viz.fig.canvas.draw()


def test_pause_reset_shuffle_and_resize():
    viz = SortVisualizer("Quick Sort", size=20, steps_per_frame=2, seed=1)
    before = list(viz.original)

    viz.toggle()
    viz._tick()
    assert viz.state == "running"
    viz.toggle()
    assert viz.state == "paused"
    viz.toggle()
    assert viz.state == "running"

    viz.reset()
    assert viz.state == "idle" and viz.data == before

    viz.shuffle()
    assert sorted(viz.data) == list(range(1, 21))

    viz.slider_size.set_val(45)
    assert len(viz.data) == 45 and len(viz.bars) == 45

    viz.radio.set_active(3)  # Merge Sort
    assert viz.algorithm == "Merge Sort" and viz.state == "idle"


def test_restart_after_finish():
    viz = SortVisualizer("Bubble Sort", size=10, steps_per_frame=50, seed=5)
    viz.toggle()
    run_to_end(viz)
    viz.toggle()  # starts a fresh run on the same data
    assert viz.state == "running"
    run_to_end(viz)
    assert viz.data == sorted(viz.data)
