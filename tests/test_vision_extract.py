"""Tests for data extraction (vision.extract module)."""

import cv2
import numpy as np

from zora.capture import BGRImage
from zora.vision.extract import (
    extract_assignment,
    ocr_number,
    ocr_text,
    parse_assignment_text,
    preprocess_for_ocr,
)


class TestPreprocessForOcr:
    def test_returns_binary_image(self) -> None:
        """Preprocessing produces a binary (black/white) image."""
        image = np.full((100, 200, 3), 128, dtype=np.uint8)
        result = preprocess_for_ocr(image)
        assert result.ndim == 2  # grayscale
        unique_vals = set(np.unique(result))
        assert unique_vals.issubset({0, 255})

    def test_upscales_small_images(self) -> None:
        """Small images are scaled up for better OCR."""
        small = np.full((30, 50, 3), 128, dtype=np.uint8)
        result = preprocess_for_ocr(small)
        assert result.shape[0] > 30
        assert result.shape[1] > 50


class TestParseAssignmentText:
    def test_parses_complete_text(self) -> None:
        text = """Patrol Sector 42
Eng: 30
Sci: 20
Tac: 15
Slots: 2
Duration: 4h
Common"""
        result = parse_assignment_text(text)
        assert result["name"] == "Patrol Sector 42"
        assert result["engineering"] == 30
        assert result["science"] == 20
        assert result["tactical"] == 15
        assert result["ship_slots"] == 2
        assert result["duration"] == "4h"
        assert result["rarity"] == "Common"

    def test_parses_partial_text(self) -> None:
        """Handles OCR output where some fields are missing."""
        text = "Rescue Mission\nEng: 50\nSci: 40"
        result = parse_assignment_text(text)
        assert result["name"] == "Rescue Mission"
        assert result["engineering"] == 50
        assert result["science"] == 40
        assert result["tactical"] == 0  # default
        assert result["ship_slots"] == 0  # default

    def test_parses_full_stat_names(self) -> None:
        text = "Mission\nEngineering: 30\nScience: 20\nTactical: 15"
        result = parse_assignment_text(text)
        assert result["engineering"] == 30
        assert result["science"] == 20
        assert result["tactical"] == 15

    def test_parses_rarity_levels(self) -> None:
        for rarity in ["Common", "Uncommon", "Rare", "Very Rare", "Epic"]:
            text = f"Test Mission\n{rarity}"
            result = parse_assignment_text(text)
            assert result["rarity"] == rarity

    def test_empty_text(self) -> None:
        result = parse_assignment_text("")
        assert result["name"] == ""
        assert result["engineering"] == 0

    def test_parses_duration_formats(self) -> None:
        """Handles various duration formats."""
        for text, expected in [
            ("Mission\nDuration: 4h", "4h"),
            ("Mission\n30m", "30m"),
            ("Mission\n1h 30m", "1h 30m"),
        ]:
            result = parse_assignment_text(text)
            assert result["duration"] == expected, f"Failed for input {text!r}"


class TestOcrText:
    def test_reads_clear_text(self) -> None:
        """OCR reads clear white text on black background."""
        image = np.zeros((60, 300, 3), dtype=np.uint8)
        cv2.putText(
            image,
            "Hello World",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
        )
        text = ocr_text(image)
        assert "Hello" in text or "hello" in text.lower()

    def test_reads_numbers(self) -> None:
        """OCR reads numbers from an image."""
        image = np.zeros((60, 200, 3), dtype=np.uint8)
        cv2.putText(
            image,
            "12345",
            (10, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255, 255, 255),
            2,
        )
        text = ocr_text(image)
        # OCR should recognize at least some digits
        assert any(c.isdigit() for c in text)


class TestOcrNumber:
    def test_extracts_number(self) -> None:
        """Extracts a single number from an image."""
        image = np.zeros((60, 120, 3), dtype=np.uint8)
        cv2.putText(
            image,
            "42",
            (10, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255, 255, 255),
            2,
        )
        result = ocr_number(image)
        assert result is not None
        assert isinstance(result, int)


class TestExtractAssignment:
    def test_returns_assignment_object(self, single_card_image: BGRImage) -> None:
        """Extracting from a card image returns an Assignment."""
        assignment = extract_assignment(single_card_image)
        assert assignment is not None
        assert isinstance(assignment.name, str)
        assert isinstance(assignment.engineering, int)
        assert isinstance(assignment.science, int)
        assert isinstance(assignment.tactical, int)
