"""Screen capture and window detection.

The capture interface is a simple callable protocol: any function or object
that returns a BGR numpy array (H x W x 3, dtype uint8) qualifies. This
lets tests inject fixture images via FileCapture while production uses
ScreenshotCapture.
"""

from typing import Protocol

import numpy as np
from numpy.typing import NDArray

# BGR image: height x width x 3 channels, uint8
BGRImage = NDArray[np.uint8]


class CaptureSource(Protocol):
    """Protocol for screen capture sources.

    Any callable that returns a BGR numpy array satisfies this protocol.
    """

    def __call__(self) -> BGRImage: ...


from zora.capture.file import FileCapture  # noqa: E402

__all__ = ["BGRImage", "CaptureSource", "FileCapture"]
