"""Tests for the capture module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from zora.capture import BGRImage, CaptureSource, FileCapture
from zora.capture.screenshot import ScreenshotCapture

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


class TestScreenshotCapture:
    def test_bgra_to_bgr_conversion(self) -> None:
        """ScreenshotCapture converts BGRA (4 channel) to BGR (3 channel)."""
        # Create a fake BGRA image (100x200 with 4 channels)
        fake_bgra = np.zeros((100, 200, 4), dtype=np.uint8)
        fake_bgra[:, :, 0] = 255  # Blue
        fake_bgra[:, :, 1] = 128  # Green
        fake_bgra[:, :, 2] = 64  # Red
        fake_bgra[:, :, 3] = 255  # Alpha

        # Mock mss module and its context manager
        mock_sct = MagicMock()
        mock_sct.monitors = [
            {},  # Monitor 0 (all monitors)
            {},  # Monitor 1
        ]
        mock_sct.grab.return_value = fake_bgra

        # Patch mss at the location where it's imported (inside screenshot module)
        mock_mss_module = MagicMock()
        mock_mss_module.mss.return_value.__enter__.return_value = mock_sct
        mock_mss_module.mss.return_value.__exit__.return_value = None

        with patch.dict("sys.modules", {"mss": mock_mss_module}):
            capture = ScreenshotCapture()
            result = capture()

        # Verify BGRA was converted to BGR (3 channels)
        assert result.shape == (100, 200, 3)
        assert result.dtype == np.uint8
        # Verify color channels are correct (alpha dropped)
        assert result[0, 0, 0] == 255  # Blue
        assert result[0, 0, 1] == 128  # Green
        assert result[0, 0, 2] == 64  # Red

    def test_monitor_parameter_passthrough(self) -> None:
        """ScreenshotCapture passes monitor index to sct.monitors."""
        fake_bgra = np.zeros((50, 50, 4), dtype=np.uint8)

        mock_sct = MagicMock()
        mock_sct.monitors = [
            {},  # Monitor 0
            {},  # Monitor 1
            {},  # Monitor 2
        ]
        mock_sct.grab.return_value = fake_bgra

        mock_mss_module = MagicMock()
        mock_mss_module.mss.return_value.__enter__.return_value = mock_sct
        mock_mss_module.mss.return_value.__exit__.return_value = None

        with patch.dict("sys.modules", {"mss": mock_mss_module}):
            capture = ScreenshotCapture(monitor=2)
            result = capture()

        # Verify grab was called with the correct monitor
        mock_sct.grab.assert_called_once_with(mock_sct.monitors[2])
        assert result.shape == (50, 50, 3)

    def test_default_monitor_is_zero(self) -> None:
        """ScreenshotCapture defaults to monitor 0 (all monitors)."""
        fake_bgra = np.zeros((30, 40, 4), dtype=np.uint8)

        mock_sct = MagicMock()
        mock_sct.monitors = [{}]
        mock_sct.grab.return_value = fake_bgra

        mock_mss_module = MagicMock()
        mock_mss_module.mss.return_value.__enter__.return_value = mock_sct
        mock_mss_module.mss.return_value.__exit__.return_value = None

        with patch.dict("sys.modules", {"mss": mock_mss_module}):
            capture = ScreenshotCapture()
            result = capture()

        # Verify default monitor is 0
        assert capture.monitor == 0
        mock_sct.grab.assert_called_once_with(mock_sct.monitors[0])
        assert result.shape == (30, 40, 3)

    def test_satisfies_capture_source_protocol(self) -> None:
        """ScreenshotCapture satisfies the CaptureSource protocol."""
        fake_bgra = np.zeros((10, 10, 4), dtype=np.uint8)

        mock_sct = MagicMock()
        mock_sct.monitors = [{}]
        mock_sct.grab.return_value = fake_bgra

        mock_mss_module = MagicMock()
        mock_mss_module.mss.return_value.__enter__.return_value = mock_sct
        mock_mss_module.mss.return_value.__exit__.return_value = None

        with patch.dict("sys.modules", {"mss": mock_mss_module}):
            # Type annotation ensures protocol conformance
            source: CaptureSource = ScreenshotCapture()
            result = source()

        # Verify it returns a valid BGRImage
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.uint8
        assert result.ndim == 3
        assert result.shape[2] == 3  # BGR has 3 channels
