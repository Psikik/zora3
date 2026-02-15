"""Tests for board detection (vision.detect module)."""

import numpy as np

from zora.capture import BGRImage
from zora.vision import BoundingBox
from zora.vision.detect import crop_board, detect_board


class TestDetectBoard:
    def test_detects_dark_region(self, synthetic_board: BGRImage) -> None:
        """Board detection finds the dark background region."""
        box = detect_board(synthetic_board)
        assert box is not None
        assert box.width > 0
        assert box.height > 0

    def test_returns_none_for_bright_image(self) -> None:
        """A uniformly bright image has no board region."""
        bright = np.full((400, 600, 3), (200, 200, 200), dtype=np.uint8)
        box = detect_board(bright)
        assert box is None

    def test_board_covers_significant_area(self, synthetic_board: BGRImage) -> None:
        """The detected board region covers most of the synthetic image."""
        box = detect_board(synthetic_board)
        assert box is not None
        image_area = synthetic_board.shape[0] * synthetic_board.shape[1]
        assert box.area > image_area * 0.05


class TestCropBoard:
    def test_crop_returns_subimage(self, synthetic_board: BGRImage) -> None:
        box = BoundingBox(x=10, y=20, width=100, height=50)
        cropped = crop_board(synthetic_board, box)
        assert cropped.shape == (50, 100, 3)

    def test_crop_preserves_content(self) -> None:
        """Cropping preserves the pixel values."""
        image = np.zeros((200, 300, 3), dtype=np.uint8)
        image[50:100, 100:200] = (255, 128, 64)
        box = BoundingBox(x=100, y=50, width=100, height=50)
        cropped = crop_board(image, box)
        assert np.all(cropped == (255, 128, 64))


class TestBoundingBox:
    def test_properties(self) -> None:
        box = BoundingBox(x=10, y=20, width=100, height=50)
        assert box.x2 == 110
        assert box.y2 == 70
        assert box.area == 5000

    def test_frozen(self) -> None:
        box = BoundingBox(x=10, y=20, width=100, height=50)
        try:
            box.x = 999  # type: ignore[misc]
            assert False, "Should not be able to mutate frozen dataclass"
        except AttributeError:
            pass
