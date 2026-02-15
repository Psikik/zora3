"""End-to-end pipeline: capture → detect → extract → structured output.

Orchestrates the full flow from screen capture to structured BoardState.
"""

import logging

from zora.capture import BGRImage, CaptureSource
from zora.models.assignment import Assignment
from zora.models.board import BoardState
from zora.vision.detect import crop_board, detect_board
from zora.vision.extract import extract_assignment
from zora.vision.regions import crop_region, find_assignment_cards

logger = logging.getLogger(__name__)


def read_board(source: CaptureSource) -> BoardState:
    """Run the full pipeline: capture → detect → extract.

    Takes a CaptureSource (any callable returning a BGR image) and
    returns a BoardState with all detected assignments.
    """
    image = source()
    return read_board_from_image(image)


def read_board_from_image(image: BGRImage) -> BoardState:
    """Run the pipeline on an already-captured image.

    Useful for testing and when the image is already loaded.
    """
    # Step 1: Detect the board region
    board_box = detect_board(image)
    if board_box is None:
        logger.warning("No admiralty board detected in image")
        return BoardState(assignments=[], ships=[])

    board_image = crop_board(image, board_box)
    logger.info(
        "Board detected at (%d, %d) size %dx%d",
        board_box.x,
        board_box.y,
        board_box.width,
        board_box.height,
    )

    # Step 2: Find assignment card regions within the board
    card_boxes = find_assignment_cards(board_image)
    logger.info("Found %d assignment cards", len(card_boxes))

    if not card_boxes:
        return BoardState(assignments=[], ships=[])

    # Step 3: Extract assignment data from each card
    assignments: list[Assignment] = []
    errors: list[str] = []
    for i, box in enumerate(card_boxes):
        card_image = crop_region(board_image, box)
        try:
            assignment = extract_assignment(card_image)
            assignments.append(assignment)
            logger.debug("Card %d: %s", i, assignment.name)
        except Exception:
            msg = f"Failed to extract assignment from card {i}"
            logger.exception(msg)
            errors.append(msg)

    return BoardState(assignments=assignments, ships=[], errors=errors)
