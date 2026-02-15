"""Shared test fixtures for vision tests.

Generates synthetic images that simulate the STO admiralty board layout.
These are deliberately simplified versions — real screenshots will differ,
but these validate that the detection → extraction pipeline works.
"""

from pathlib import Path

import cv2
import numpy as np
import pytest

from zora.capture import BGRImage

FIXTURES = Path(__file__).parent / "fixtures"


def make_board_image(
    width: int = 800,
    height: int = 600,
    bg_color: tuple[int, int, int] = (30, 25, 20),
    num_cards: int = 3,
) -> BGRImage:
    """Create a synthetic board image with assignment cards.

    The board is a dark rectangle with lighter card rectangles inside.
    Each card contains text that simulates assignment details.
    """
    image = np.full((height, width, 3), bg_color, dtype=np.uint8)
    return image


def draw_assignment_card(
    image: BGRImage,
    x: int,
    y: int,
    w: int,
    h: int,
    name: str = "Patrol Sector 42",
    eng: int = 30,
    sci: int = 20,
    tac: int = 15,
    slots: int = 2,
    duration: str = "4h",
    rarity: str = "Common",
) -> BGRImage:
    """Draw a synthetic assignment card onto an image.

    The card has a lighter background with text content laid out
    similar to the actual STO assignment card format.
    """
    # Card background — lighter gray/blue
    card_color = (120, 110, 100)
    cv2.rectangle(image, (x, y), (x + w, y + h), card_color, -1)
    cv2.rectangle(image, (x, y), (x + w, y + h), (180, 170, 160), 2)

    # Text settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_color = (255, 255, 255)
    small = 0.5
    line_h = 25

    # Title
    cv2.putText(image, name, (x + 10, y + 25), font, 0.6, text_color, 1)

    # Stats
    cy = y + 55
    cv2.putText(image, f"Eng: {eng}", (x + 10, cy), font, small, text_color, 1)
    cy += line_h
    cv2.putText(image, f"Sci: {sci}", (x + 10, cy), font, small, text_color, 1)
    cy += line_h
    cv2.putText(image, f"Tac: {tac}", (x + 10, cy), font, small, text_color, 1)
    cy += line_h
    cv2.putText(image, f"Slots: {slots}", (x + 10, cy), font, small, text_color, 1)
    cy += line_h
    dur_text = f"Duration: {duration}"
    cv2.putText(image, dur_text, (x + 10, cy), font, small, text_color, 1)
    cy += line_h
    cv2.putText(image, rarity, (x + 10, cy), font, small, text_color, 1)

    return image


@pytest.fixture
def synthetic_board() -> BGRImage:
    """A synthetic board image with 3 assignment cards."""
    image = make_board_image(800, 600)

    draw_assignment_card(
        image,
        50,
        30,
        300,
        200,
        name="Patrol Sector 42",
        eng=30,
        sci=20,
        tac=15,
        slots=2,
        duration="4h",
        rarity="Common",
    )
    draw_assignment_card(
        image,
        50,
        250,
        300,
        200,
        name="Rescue Mission",
        eng=50,
        sci=40,
        tac=30,
        slots=3,
        duration="8h",
        rarity="Rare",
    )
    draw_assignment_card(
        image,
        400,
        30,
        300,
        200,
        name="Supply Run",
        eng=15,
        sci=5,
        tac=25,
        slots=1,
        duration="2h",
        rarity="Uncommon",
    )

    return image


@pytest.fixture
def single_card_image() -> BGRImage:
    """A single assignment card image (already cropped)."""
    image = np.full((200, 300, 3), (120, 110, 100), dtype=np.uint8)
    draw_assignment_card(
        image,
        0,
        0,
        300,
        200,
        name="Patrol Sector 42",
        eng=30,
        sci=20,
        tac=15,
        slots=2,
        duration="4h",
        rarity="Common",
    )
    return image
