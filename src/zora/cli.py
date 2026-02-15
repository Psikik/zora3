"""Command-line entry point for Zora."""

import json
import sys

from zora.models import BoardState


def main() -> None:
    """Run the Zora admiralty board reader."""
    # The full pipeline (capture → detect → extract) will be wired in Priority 6.
    board = BoardState(assignments=[], ships=[])
    json.dump(board.to_dict(), sys.stdout, indent=2)
    sys.stdout.write("\n")
