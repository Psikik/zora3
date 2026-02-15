"""Region identification — find individual assignment cards within the board.

Once the board region is located, this module identifies the sub-regions
corresponding to individual assignment cards. Each card is a lighter
rectangle within the dark board background.
"""

import logging

import cv2
import numpy as np

from zora.capture import BGRImage
from zora.vision import BoundingBox

logger = logging.getLogger(__name__)

# Assignment cards are lighter rectangles against the dark board background.
# In HSV, they have moderate-to-high value (brightness).
CARD_BG_LOWER = np.array([0, 0, 80], dtype=np.uint8)
CARD_BG_UPPER = np.array([180, 100, 200], dtype=np.uint8)

# Minimum card dimensions as fraction of board dimensions
MIN_CARD_WIDTH_FRACTION = 0.15
MIN_CARD_HEIGHT_FRACTION = 0.05


def find_assignment_cards(
    board_image: BGRImage,
    min_width_frac: float = MIN_CARD_WIDTH_FRACTION,
    min_height_frac: float = MIN_CARD_HEIGHT_FRACTION,
) -> list[BoundingBox]:
    """Find assignment card regions within the cropped board image.

    Returns bounding boxes for each detected card, sorted top-to-bottom
    then left-to-right (reading order).
    """
    h, w = board_image.shape[:2]
    min_width = int(w * min_width_frac)
    min_height = int(h * min_height_frac)

    hsv = cv2.cvtColor(board_image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, CARD_BG_LOWER, CARD_BG_UPPER)

    # Clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cards: list[BoundingBox] = []
    for contour in contours:
        x, y, cw, ch = cv2.boundingRect(contour)
        if cw >= min_width and ch >= min_height:
            cards.append(BoundingBox(x=x, y=y, width=cw, height=ch))

    # Sort by y first (top to bottom), then x (left to right)
    cards.sort(key=lambda b: (b.y, b.x))

    logger.debug("Found %d assignment card regions", len(cards))
    return cards


def crop_region(image: BGRImage, box: BoundingBox) -> BGRImage:
    """Crop a sub-region from an image using a bounding box."""
    return image[box.y : box.y2, box.x : box.x2]
