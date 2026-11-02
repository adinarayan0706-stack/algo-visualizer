#!/usr/bin/env python3
"""Sorting Algorithm Visualizer - command line entry point."""
import argparse
import sys

from visualizer.algorithms import ALGORITHMS, find_algorithm


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize sorting algorithms with matplotlib.")
    parser.add_argument("-a", "--algo", default="bubble",
                        help="bubble, selection, insertion, merge, quick or heap "
                             "(default: bubble)")
    parser.add_argument("-n", "--size", type=int, default=40,
                        help="number of bars, 5-150 (default: 40)")
    parser.add_argument("-s", "--speed", type=int, default=3,
                        help="steps per frame, 1-40 (default: 3)")
    parser.add_argument("--seed", type=int, default=None,
                        help="random seed for a reproducible shuffle")
    parser.add_argument("--save", metavar="FILE.gif",
                        help="render an animated GIF instead of opening a window")
    parser.add_argument("--list", action="store_true",
                        help="list available algorithms and exit")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    if args.list:
        print("\n".join(ALGORITHMS))
        return 0

    algorithm = find_algorithm(args.algo)
    if algorithm is None:
        print(f"Unknown algorithm {args.algo!r}. Try --list.", file=sys.stderr)
        return 2
    if not 5 <= args.size <= 150:
        print("--size must be between 5 and 150.", file=sys.stderr)
        return 2
    if not 1 <= args.speed <= 40:
        print("--speed must be between 1 and 40.", file=sys.stderr)
        return 2

    if args.save:
        import matplotlib
        matplotlib.use("Agg")  # no window needed
        from visualizer.export import export_gif
        frames = export_gif(algorithm, args.size, args.save, seed=args.seed)
        print(f"Saved {args.save} ({frames} frames)")
        return 0

    from visualizer.app import SortVisualizer
    SortVisualizer(algorithm, args.size, args.speed, args.seed).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
