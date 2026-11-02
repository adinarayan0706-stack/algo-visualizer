"""Render a sorting run to an animated GIF (no window needed)."""
from __future__ import annotations

import math
import random
from typing import Iterator, List, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from .algorithms import ALGORITHMS, COMPLEXITY
from .app import BASE, BG, MUTED, TEXT, paint, style_axes

Frame = Tuple[List[int], tuple, tuple, int, int, int]


def _frames(data: List[int], algorithm: str, steps_per_frame: int) -> Iterator[Frame]:
    arr = list(data)
    gen = ALGORITHMS[algorithm](arr)
    compare: tuple = ()
    write: tuple = ()
    comparisons = writes = 0
    done = False
    while not done:
        for _ in range(steps_per_frame):
            try:
                compare, write = next(gen)
            except StopIteration:
                done = True
                break
            if compare:
                comparisons += 1
            writes += len(write)
        yield list(arr), compare, write, 0, comparisons, writes
    n = len(arr)
    sweep = 0
    while sweep < n:  # green sweep
        sweep = min(n, sweep + max(1, n // 20))
        yield list(arr), (), (), sweep, comparisons, writes
    for _ in range(15):  # hold the finished picture
        yield list(arr), (), (), n, comparisons, writes


def export_gif(algorithm: str, size: int, path: str, fps: int = 25,
               max_frames: int = 250, seed: Optional[int] = None) -> int:
    """Write an animated GIF to ``path`` and return the number of frames."""
    rng = random.Random(seed)
    data = list(range(1, size + 1))
    rng.shuffle(data)

    total_steps = sum(1 for _ in ALGORITHMS[algorithm](list(data)))
    steps_per_frame = max(1, math.ceil(total_steps / max_frames))
    frames = list(_frames(data, algorithm, steps_per_frame))

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=80, facecolor=BG)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.82, bottom=0.12)
    style_axes(ax, size)
    bars = ax.bar(range(size), data, width=0.85, color=BASE)
    best, avg, worst, space = COMPLEXITY[algorithm]
    ax.set_title(f"{algorithm}\nBest {best}  ·  Average {avg}  ·  "
                 f"Worst {worst}  ·  Space {space}",
                 color=TEXT, fontsize=11, loc="left")
    stats = fig.text(0.03, 0.04, "", color=MUTED, fontsize=10)

    def update(frame: Frame):
        arr, compare, write, sweep, comparisons, writes = frame
        paint(bars, arr, compare, write, sweep)
        stats.set_text(f"Comparisons: {comparisons}    Writes: {writes}")
        return list(bars)

    anim = FuncAnimation(fig, update, frames=frames, blit=False,
                         cache_frame_data=False)
    anim.save(path, writer=PillowWriter(fps=fps))
    plt.close(fig)
    return len(frames)
