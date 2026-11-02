"""Interactive matplotlib front-end for the sorting visualizer."""
from __future__ import annotations

import itertools
import random
from typing import Iterable, List, Optional

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons, Slider

from .algorithms import ALGORITHMS, COMPLEXITY

# Palette
BASE = "#4C78A8"
COMPARE = "#F2CF5B"
WRITE = "#E45756"
DONE = "#54A24B"
BG = "#14161a"
PANEL = "#1d2026"
TEXT = "#e6e6e6"
MUTED = "#9aa0a6"


def paint(bars, data: List[int], compare: Iterable[int] = (),
          write: Iterable[int] = (), sorted_upto: int = 0) -> None:
    """Set bar heights and colours for one frame (shared with the GIF exporter)."""
    cmp_set, write_set = set(compare), set(write)
    for i, (bar, value) in enumerate(zip(bars, data)):
        bar.set_height(value)
        if i in write_set:
            colour = WRITE
        elif i in cmp_set:
            colour = COMPARE
        elif i < sorted_upto:
            colour = DONE
        else:
            colour = BASE
        bar.set_facecolor(colour)


def style_axes(ax, n: int) -> None:
    ax.set_facecolor(BG)
    ax.set_xlim(-0.8, n - 0.2)
    ax.set_ylim(0, n * 1.05)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


class SortVisualizer:
    """Window with bars, an algorithm picker, buttons and sliders."""

    def __init__(self, algorithm: str = "Bubble Sort", size: int = 40,
                 steps_per_frame: int = 3, seed: Optional[int] = None) -> None:
        if algorithm not in ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algorithm!r}")
        self.algorithm = algorithm
        self.size = size
        self.steps = steps_per_frame
        self.rng = random.Random(seed)
        self.original = self._new_data()
        self._reset_run()
        self._build_ui()

    # ---------------------------------------------------------------- state
    def _new_data(self) -> List[int]:
        data = list(range(1, self.size + 1))
        self.rng.shuffle(data)
        return data

    def _reset_run(self) -> None:
        self.data = list(self.original)
        self.gen = None
        self.state = "idle"  # idle | running | paused | finishing | done
        self.comparisons = 0
        self.writes = 0
        self.sweep = 0
        self.compare: tuple = ()
        self.write: tuple = ()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        plt.rcParams["toolbar"] = "None"
        self.fig = plt.figure(figsize=(11, 6.5), facecolor=BG)
        try:
            self.fig.canvas.manager.set_window_title("Sorting Algorithm Visualizer")
        except Exception:
            pass

        self.ax = self.fig.add_axes([0.28, 0.12, 0.69, 0.74])
        self._draw_bars()

        # Algorithm picker
        radio_ax = self.fig.add_axes([0.03, 0.46, 0.20, 0.44], facecolor=PANEL)
        radio_ax.set_title("Algorithm", color=TEXT, fontsize=11, loc="left")
        names = list(ALGORITHMS)
        self.radio = RadioButtons(radio_ax, names, active=names.index(self.algorithm),
                                  activecolor=BASE)
        for label in self.radio.labels:
            label.set_color(TEXT)
            label.set_fontsize(10)
        try:  # make unselected circles visible on the dark panel
            self.radio.set_radio_props({"edgecolor": MUTED, "facecolor": PANEL})
        except Exception:
            pass
        self.radio.on_clicked(self._on_algorithm)

        # Buttons
        self.btn_start = self._button([0.03, 0.34, 0.20, 0.06], "Start / Pause", self.toggle)
        self.btn_reset = self._button([0.03, 0.26, 0.095, 0.06], "Reset", self.reset)
        self.btn_shuffle = self._button([0.135, 0.26, 0.095, 0.06], "Shuffle", self.shuffle)

        # Sliders
        size_ax = self.fig.add_axes([0.08, 0.17, 0.13, 0.03], facecolor=PANEL)
        self.slider_size = Slider(size_ax, "Size", 5, 150, valinit=self.size,
                                  valstep=5, color=BASE)
        speed_ax = self.fig.add_axes([0.08, 0.10, 0.13, 0.03], facecolor=PANEL)
        self.slider_speed = Slider(speed_ax, "Speed", 1, 40, valinit=self.steps,
                                   valstep=1, color=BASE)
        for slider in (self.slider_size, self.slider_speed):
            slider.label.set_color(TEXT)
            slider.valtext.set_color(MUTED)
        self.slider_size.on_changed(self._on_size)
        self.slider_speed.on_changed(self._on_speed)

        self.stats = self.fig.text(0.28, 0.05, "", color=MUTED, fontsize=11)
        self.fig.text(0.03, 0.03, "Keys: SPACE start/pause  R reset  N new shuffle",
                      color=MUTED, fontsize=8)

        # Replace matplotlib's default key bindings (S = save, R = home ...)
        manager = self.fig.canvas.manager
        handler = getattr(manager, "key_press_handler_id", None)
        if handler is not None:
            self.fig.canvas.mpl_disconnect(handler)
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)

        self._update_title()
        self.anim = FuncAnimation(self.fig, self._tick, frames=itertools.count(),
                                  interval=30, blit=False, cache_frame_data=False)

    def _button(self, rect, label, callback) -> Button:
        ax = self.fig.add_axes(rect)
        button = Button(ax, label, color=PANEL, hovercolor="#2a2f38")
        button.label.set_color(TEXT)
        button.on_clicked(callback)
        return button

    def _draw_bars(self) -> None:
        self.ax.clear()
        style_axes(self.ax, len(self.data))
        self.bars = self.ax.bar(range(len(self.data)), self.data, width=0.85, color=BASE)

    def _update_title(self) -> None:
        best, avg, worst, space = COMPLEXITY[self.algorithm]
        self.ax.set_title(
            f"{self.algorithm}\nBest {best}  ·  Average {avg}  ·  "
            f"Worst {worst}  ·  Space {space}",
            color=TEXT, fontsize=12, loc="left")

    # ------------------------------------------------------------- actions
    def toggle(self, _event=None) -> None:
        if self.state == "done":
            self.reset()
        if self.state == "idle":
            self.gen = ALGORITHMS[self.algorithm](self.data)
            self.state = "running"
        elif self.state == "running":
            self.state = "paused"
        elif self.state == "paused":
            self.state = "running"

    def reset(self, _event=None) -> None:
        """Restore the same unsorted data so algorithms can be compared fairly."""
        self._reset_run()
        self._draw_bars()
        self._update_title()

    def shuffle(self, _event=None) -> None:
        self.original = self._new_data()
        self.reset()

    def _on_algorithm(self, label: str) -> None:
        self.algorithm = label
        self.reset()

    def _on_size(self, value: float) -> None:
        if int(value) != self.size:
            self.size = int(value)
            self.shuffle()

    def _on_speed(self, value: float) -> None:
        self.steps = int(value)

    def _on_key(self, event) -> None:
        if event.key == " ":
            self.toggle()
        elif event.key == "r":
            self.reset()
        elif event.key == "n":
            self.shuffle()

    # ----------------------------------------------------------- animation
    def _tick(self, _frame=None):
        if self.state == "running":
            for _ in range(self.steps):
                try:
                    compare, write = next(self.gen)
                except StopIteration:
                    self.state = "finishing"
                    self.compare = self.write = ()
                    break
                self.compare, self.write = compare, write
                if compare:
                    self.comparisons += 1
                self.writes += len(write)
        elif self.state == "finishing":
            self.sweep = min(len(self.data), self.sweep + max(1, len(self.data) // 25))
            if self.sweep >= len(self.data):
                self.state = "done"

        sorted_upto = self.sweep if self.state in ("finishing", "done") else 0
        paint(self.bars, self.data, self.compare, self.write, sorted_upto)
        label = {"idle": "Ready", "running": "Sorting...", "paused": "Paused",
                 "finishing": "Sorted!", "done": "Sorted!"}[self.state]
        self.stats.set_text(f"{label}    Comparisons: {self.comparisons}    "
                            f"Writes: {self.writes}")
        return list(self.bars)

    def run(self) -> None:
        plt.show()
