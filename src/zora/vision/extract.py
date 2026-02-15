"""Data extraction — read text and numbers from detected card regions.

Uses Tesseract OCR (via pytesseract) to read assignment details from
card images. Preprocessing improves OCR accuracy on game UI text.
"""

import logging
import re

import cv2
import pytesseract

from zora.capture import BGRImage
from zora.models.assignment import Assignment

logger = logging.getLogger(__name__)

# Tesseract config for reading game UI text
# PSM 6 = assume a single uniform block of text
# OEM 3 = default engine mode
TESSERACT_CONFIG = "--oem 3 --psm 6"

# For reading individual numbers/stats
TESSERACT_DIGITS_CONFIG = "--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789"


def preprocess_for_ocr(image: BGRImage) -> BGRImage:
    """Preprocess a card image for better OCR accuracy.

    Converts to grayscale, applies Gaussian blur + OTSU thresholding,
    and scales up small text to improve Tesseract recognition.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Scale up if the image is small — Tesseract works better on larger text
    h, w = gray.shape
    if h < 100 or w < 200:
        scale = max(200 / w, 100 / h, 2.0)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Blur to reduce noise, then apply OTSU threshold for clean binary output
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary


def ocr_text(image: BGRImage, config: str = TESSERACT_CONFIG) -> str:
    """Run Tesseract OCR on an image and return the recognized text.

    The image is preprocessed before OCR to improve accuracy.
    """
    processed = preprocess_for_ocr(image)
    text = pytesseract.image_to_string(processed, config=config)
    return text.strip()


def ocr_number(image: BGRImage) -> int | None:
    """Extract a single integer from an image region.

    Returns None if no valid number is found.
    """
    processed = preprocess_for_ocr(image)
    text = pytesseract.image_to_string(processed, config=TESSERACT_DIGITS_CONFIG)
    text = text.strip()
    if text.isdigit():
        return int(text)
    # Try to find a number in noisy output
    match = re.search(r"\d+", text)
    if match:
        return int(match.group())
    return None


def parse_assignment_text(raw_text: str) -> dict:
    """Parse raw OCR text from an assignment card into structured fields.

    This is a best-effort parser that extracts what it can from OCR output.
    The STO assignment card layout typically shows:
    - Title on the first line
    - Stats as "Engineering: N", "Science: N", "Tactical: N" or similar
    - Duration as a time string
    - Rarity indicator
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    result: dict = {
        "name": "",
        "engineering": 0,
        "science": 0,
        "tactical": 0,
        "ship_slots": 0,
        "duration": "",
        "rarity": "",
        "event_rewards": [],
    }

    if not lines:
        return result

    # First non-empty line is usually the assignment name
    result["name"] = lines[0]

    full_text = raw_text.lower()

    # Extract stats with pattern matching
    eng_match = re.search(r"(?:eng(?:ineering)?)\s*[:\-]?\s*(\d+)", full_text)
    if eng_match:
        result["engineering"] = int(eng_match.group(1))

    sci_match = re.search(r"(?:sci(?:ence)?)\s*[:\-]?\s*(\d+)", full_text)
    if sci_match:
        result["science"] = int(sci_match.group(1))

    tac_match = re.search(r"(?:tac(?:tical)?)\s*[:\-]?\s*(\d+)", full_text)
    if tac_match:
        result["tactical"] = int(tac_match.group(1))

    # Ship slots
    slots_match = re.search(r"(?:slots?|ships?)\s*[:\-]?\s*(\d+)", full_text)
    if slots_match:
        result["ship_slots"] = int(slots_match.group(1))

    # Duration (e.g., "4h", "30m", "1h 30m", "4 hours")
    dur_pat = r"(\d+\s*h(?:ours?)?(?:\s*\d+\s*m(?:in)?)?|\d+\s*m(?:in)?)"
    dur_match = re.search(dur_pat, full_text)
    if dur_match:
        result["duration"] = dur_match.group(1).strip()

    # Rarity
    for rarity in ["epic", "very rare", "rare", "uncommon", "common"]:
        if rarity in full_text:
            result["rarity"] = rarity.title()
            break

    # Event rewards — look for lines containing reward-related keywords
    # STO event rewards appear as "Event: <reward name>" or "Reward: <name>"
    # or lines mentioning specific reward types like dilithium, marks, XP, etc.
    rewards: list[str] = []
    reward_line_pat = re.compile(
        r"(?:event\s*rewards?|rewards?)\s*[:\-]\s*(.+)", re.IGNORECASE
    )
    reward_item_pat = re.compile(
        r"(\d+[x×]?\s*(?:dilithium|dil|marks?|xp|experience|ec|energy credits"
        r"|fleet credits|admiralty xp|campaign xp|tour of duty|"
        r"r&d materials?|reputation marks?))",
        re.IGNORECASE,
    )
    for line in lines:
        line_match = reward_line_pat.search(line)
        if line_match:
            # Split comma-separated rewards on a single reward line
            reward_text = line_match.group(1).strip()
            for part in re.split(r"[,;]", reward_text):
                part = part.strip()
                if part:
                    rewards.append(part)
        else:
            # Also check for standalone reward item patterns
            for item_match in reward_item_pat.finditer(line):
                rewards.append(item_match.group(1).strip())
    result["event_rewards"] = rewards

    return result


def extract_assignment(card_image: BGRImage) -> Assignment:
    """Extract an Assignment from a card image using OCR.

    Takes a cropped image of a single assignment card, runs OCR,
    parses the text, and returns an Assignment domain object.
    """
    raw_text = ocr_text(card_image)
    logger.debug("OCR raw text: %r", raw_text)

    fields = parse_assignment_text(raw_text)
    logger.debug("Parsed fields: %s", fields)

    return Assignment(
        name=fields["name"],
        engineering=fields["engineering"],
        science=fields["science"],
        tactical=fields["tactical"],
        ship_slots=fields["ship_slots"],
        duration=fields["duration"],
        rarity=fields["rarity"],
        event_rewards=fields["event_rewards"],
    )
