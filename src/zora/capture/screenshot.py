"""Live screenshot capture source.

Captures the entire screen (or a specific window) and returns it as a BGR
numpy array. Uses mss for cross-platform screenshot capture.

This module is only usable when a display is available. In headless
environments (CI, containers), use FileCapture instead.
"""

import numpy as np

from zora.capture import BGRImage


class ScreenshotCapture:
    """Capture a screenshot of the screen.

    Uses the mss library for fast, cross-platform screen capture.
    The captured image is converted from BGRA to BGR format.

    Usage::

        capture = ScreenshotCapture()
        image = capture()  # full screen
    """

    def __init__(self, monitor: int = 0) -> None:
        """Initialize with a monitor index (0 = all monitors combined)."""
        self.monitor = monitor

    def __call__(self) -> BGRImage:
        """Capture and return a BGR screenshot."""
        import mss

        with mss.mss() as sct:
            shot = sct.grab(sct.monitors[self.monitor])
            # mss returns BGRA; drop alpha channel to get BGR
            bgra = np.array(shot, dtype=np.uint8)
            bgr: BGRImage = bgra[:, :, :3]
            return bgr
