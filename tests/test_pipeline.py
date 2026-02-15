"""Tests for the end-to-end pipeline."""

import numpy as np

from zora.capture import BGRImage
from zora.models import BoardState
from zora.pipeline import read_board, read_board_from_image


class TestReadBoardFromImage:
    def test_returns_board_state(self, synthetic_board: BGRImage) -> None:
        """Pipeline returns a BoardState from a synthetic board image."""
        board = read_board_from_image(synthetic_board)
        assert isinstance(board, BoardState)

    def test_bright_image_returns_empty(self) -> None:
        """A bright image with no board returns empty BoardState."""
        bright = np.full((400, 600, 3), (200, 200, 200), dtype=np.uint8)
        board = read_board_from_image(bright)
        assert board.assignments == []
        assert board.ships == []

    def test_empty_dark_image_returns_empty(self) -> None:
        """A dark image with no cards returns empty assignments."""
        dark = np.full((400, 600, 3), (30, 25, 20), dtype=np.uint8)
        board = read_board_from_image(dark)
        assert board.assignments == []


class TestReadBoard:
    def test_with_callable_source(self, synthetic_board: BGRImage) -> None:
        """Pipeline works with any callable returning a BGR image."""

        def fake_source() -> BGRImage:
            return synthetic_board

        board = read_board(fake_source)
        assert isinstance(board, BoardState)

    def test_output_is_serializable(self, synthetic_board: BGRImage) -> None:
        """BoardState from pipeline can be serialized to dict/JSON."""
        board = read_board_from_image(synthetic_board)
        d = board.to_dict()
        assert "assignments" in d
        assert "ships" in d
        assert isinstance(d["assignments"], list)
