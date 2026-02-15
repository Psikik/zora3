"""Board detection — locate the admiralty board within a screenshot.

The admiralty board is a rectangular UI panel with a dark background
containing assignment cards. This module finds that panel region.
"""

import logging

import cv2
import numpy as np

from zora.capture import BGRImage
from zora.vision import BoundingBox

logger = logging.getLogger(__name__)

# HSV range for the dark admiralty board background.
# STO's UI uses a very dark blue/gray background for the board area.
BOARD_BG_LOWER = np.array([0, 0, 10], dtype=np.uint8)
BOARD_BG_UPPER = np.array([180, 120, 60], dtype=np.uint8)

# Minimum fraction of image area the board must occupy to be valid
MIN_BOARD_AREA_FRACTION = 0.05
# Morphological kernel size for noise cleanup in board detection
BOARD_MORPH_KERNEL_SIZE = (15, 15)


def detect_board(image: BGRImage) -> BoundingBox | None:
    """Locate the admiralty board region within a full screenshot.

    Uses color-based segmentation to find the dark UI panel, then
    returns the bounding box of the largest qualifying region.

    Returns None if no board-like region is found.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, BOARD_BG_LOWER, BOARD_BG_UPPER)

    # Clean up noise with morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, BOARD_MORPH_KERNEL_SIZE)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        logger.debug("No contours found in board detection")
        return None

    image_area = image.shape[0] * image.shape[1]
    min_area = int(image_area * MIN_BOARD_AREA_FRACTION)

    # Find the largest contour that meets the minimum area threshold
    best = None
    best_area = 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area >= min_area and area > best_area:
            best = BoundingBox(x=x, y=y, width=w, height=h)
            best_area = area

    if best is None:
        logger.debug("No contour met minimum area threshold (%d px)", min_area)
    else:
        logger.debug("Detected board at %s (area=%d)", best, best_area)

    return best


def crop_board(image: BGRImage, box: BoundingBox) -> BGRImage:
    """Crop the image to the board bounding box."""
    return image[box.y : box.y2, box.x : box.x2]
