"""Command-line entry point for Zora."""

import argparse
import json
import logging
import sys

from zora.capture.file import FileCapture
from zora.models import BoardState
from zora.pipeline import read_board


def main() -> None:
    """Run the Zora admiralty board reader."""
    parser = argparse.ArgumentParser(
        prog="zora",
        description="Read the Star Trek Online Admiralty assignment board",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    parser.add_argument(
        "--image",
        type=str,
        help="Path to a screenshot image file (instead of live capture)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(message)s")

    if args.image:
        source = FileCapture(args.image)
        board = read_board(source)
    else:
        # No image provided — output empty board
        board = BoardState(assignments=[], ships=[])

    json.dump(board.to_dict(), sys.stdout, indent=2)
    sys.stdout.write("\n")
