"""File-based capture source for testing and development.

Loads an image from disk using OpenCV, returning it as a BGR numpy array.
This avoids needing a live game window during testing.
"""

from pathlib import Path

import cv2

from zora.capture import BGRImage


class FileCapture:
    """Load a screenshot from a file on disk.

    Usage::

        capture = FileCapture("tests/fixtures/board.png")
        image = capture()
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Capture file not found: {self.path}")

    def __call__(self) -> BGRImage:
        """Read and return the image as a BGR numpy array."""
        image = cv2.imread(str(self.path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"Failed to read image: {self.path}")
        return image
