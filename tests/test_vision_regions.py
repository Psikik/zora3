"""Tests for region identification (vision.regions module)."""

import numpy as np

from zora.capture import BGRImage
from zora.vision import BoundingBox
from zora.vision.regions import crop_region, find_assignment_cards


class TestFindAssignmentCards:
    def test_finds_cards_in_synthetic_board(self, synthetic_board: BGRImage) -> None:
        """Detects the card regions within the synthetic board."""
        cards = find_assignment_cards(synthetic_board)
        # Our synthetic board has 3 cards drawn as lighter rectangles
        assert len(cards) >= 1  # At least some cards detected

    def test_cards_have_valid_dimensions(self, synthetic_board: BGRImage) -> None:
        """Each detected card has positive width and height."""
        cards = find_assignment_cards(synthetic_board)
        for card in cards:
            assert card.width > 0
            assert card.height > 0

    def test_cards_sorted_by_position(self, synthetic_board: BGRImage) -> None:
        """Cards are sorted top-to-bottom, left-to-right."""
        cards = find_assignment_cards(synthetic_board)
        if len(cards) > 1:
            for i in range(len(cards) - 1):
                # Either y increases, or same y row and x increases
                assert (cards[i].y, cards[i].x) <= (cards[i + 1].y, cards[i + 1].x)

    def test_no_cards_in_empty_dark_image(self) -> None:
        """A uniformly dark image has no card regions."""
        dark = np.full((400, 600, 3), (30, 25, 20), dtype=np.uint8)
        cards = find_assignment_cards(dark)
        assert len(cards) == 0

    def test_no_cards_in_very_bright_image(self) -> None:
        """A very bright image (V>200) has no card-like regions."""
        bright = np.full((400, 600, 3), (250, 250, 250), dtype=np.uint8)
        cards = find_assignment_cards(bright)
        assert len(cards) == 0


class TestCropRegion:
    def test_crop_returns_subimage(self) -> None:
        image = np.zeros((200, 300, 3), dtype=np.uint8)
        image[10:50, 20:80] = 128
        box = BoundingBox(x=20, y=10, width=60, height=40)
        cropped = crop_region(image, box)
        assert cropped.shape == (40, 60, 3)
        assert np.all(cropped == 128)
