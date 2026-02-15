"""Tests for the capture module."""

from pathlib import Path

import numpy as np
import pytest

from zora.capture import BGRImage, CaptureSource, FileCapture

FIXTURES = Path(__file__).parent / "fixtures"


class TestFileCapture:
    def test_loads_image(self) -> None:
        capture = FileCapture(FIXTURES / "test_capture.png")
        image = capture()
        assert isinstance(image, np.ndarray)
        assert image.dtype == np.uint8
        assert image.ndim == 3
        assert image.shape == (100, 200, 3)

    def test_returns_bgr(self) -> None:
        """The fixture image has blue=255 everywhere, green rect in center."""
        capture = FileCapture(FIXTURES / "test_capture.png")
        image = capture()
        # Top-left corner should be pure blue (BGR: 255, 0, 0)
        assert image[0, 0, 0] == 255  # Blue
        assert image[0, 0, 1] == 0  # Green
        assert image[0, 0, 2] == 0  # Red

    def test_center_has_green(self) -> None:
        """Center region has green=128 overlay."""
        capture = FileCapture(FIXTURES / "test_capture.png")
        image = capture()
        assert image[50, 100, 1] == 128  # Green channel in center

    def test_callable_multiple_times(self) -> None:
        """FileCapture can be called repeatedly."""
        capture = FileCapture(FIXTURES / "test_capture.png")
        img1 = capture()
        img2 = capture()
        np.testing.assert_array_equal(img1, img2)

    def test_missing_file_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            FileCapture("/nonexistent/path.png")

    def test_accepts_string_path(self) -> None:
        capture = FileCapture(str(FIXTURES / "test_capture.png"))
        image = capture()
        assert image.shape == (100, 200, 3)

    def test_satisfies_protocol(self) -> None:
        """FileCapture satisfies the CaptureSource protocol."""
        capture = FileCapture(FIXTURES / "test_capture.png")
        # Protocol check: it's callable and returns BGRImage
        result = capture()
        assert isinstance(result, np.ndarray)


class TestCaptureSource:
    def test_lambda_satisfies_protocol(self) -> None:
        """A simple lambda returning a numpy array satisfies CaptureSource."""

        def fake_capture() -> BGRImage:
            return np.zeros((10, 10, 3), dtype=np.uint8)

        # This should work as a CaptureSource
        source: CaptureSource = fake_capture
        result = source()
        assert result.shape == (10, 10, 3)
