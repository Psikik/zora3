"""Command-line entry point for Zora."""

import argparse
import importlib.metadata
import json
import logging
import sys

from zora.capture.file import FileCapture
from zora.pipeline import read_board


def _get_version() -> str:
    """Read the package version from installed metadata."""
    try:
        return importlib.metadata.version("zora")
    except importlib.metadata.PackageNotFoundError:
        return "0.1.0"


def main() -> None:
    """Run the Zora admiralty board reader."""
    parser = argparse.ArgumentParser(
        prog="zora",
        description="Read the Star Trek Online Admiralty assignment board",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
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
    else:
        try:
            from zora.capture.screenshot import ScreenshotCapture

            source = ScreenshotCapture()
        except ImportError:
            print(
                "Error: Live capture requires the 'mss' package. "
                "Install it with: pip install zora[capture]",
                file=sys.stderr,
            )
            sys.exit(1)

    board = read_board(source)
    json.dump(board.to_dict(), sys.stdout, indent=2)
    sys.stdout.write("\n")
