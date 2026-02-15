"""Image processing, region detection, and OCR.

Architecture: detection finds regions, extraction reads them.
- detect.py: locates the admiralty board within a full screenshot
- regions.py: identifies sub-regions (individual assignment cards) within the board
- extract.py: reads text/numbers from identified regions using OCR
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BoundingBox:
    """An axis-aligned rectangle within an image.

    Coordinates are in pixels, origin at top-left.
    """

    x: int
    y: int
    width: int
    height: int

    @property
    def x2(self) -> int:
        return self.x + self.width

    @property
    def y2(self) -> int:
        return self.y + self.height

    @property
    def area(self) -> int:
        return self.width * self.height


__all__ = ["BoundingBox"]
