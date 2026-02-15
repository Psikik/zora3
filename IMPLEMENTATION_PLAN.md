# Implementation Plan

## Current State

The project has Ralph automation infrastructure, a core spec (`specs/core.md`), and
architectural guidelines (`AGENTS.md`) but **zero application code**. No Python files,
no tests, no `pyproject.toml`, no test fixtures exist yet.

## Priority 1 — Project Skeleton

These items establish the foundation everything else depends on.

- [ ] Create `pyproject.toml` with project metadata, Python 3.12+ requirement, `[project.scripts]` entry point for `zora` CLI, dev dependencies (ruff, pytest), and runtime dependencies (numpy, opencv-python-headless, pytesseract or other OCR library)
- [ ] Create package structure: `src/zora/__init__.py`, `src/zora/capture/__init__.py`, `src/zora/vision/__init__.py`, `src/zora/models/__init__.py`
- [ ] Create `src/zora/__main__.py` so `python -m zora` works
- [ ] Create minimal `src/zora/cli.py` entry point wired to `[project.scripts]`
- [ ] Create `tests/__init__.py` and `tests/fixtures/.gitkeep`
- [ ] Verify `uv sync`, `uv run ruff check`, `uv run ruff format --check`, and `uv run pytest` all pass on the empty skeleton

## Priority 2 — Domain Models

Dataclasses in `src/zora/models/` matching the spec's domain concepts.

- [ ] `src/zora/models/ship.py` — `Ship` dataclass with fields: `name: str`, `engineering: int`, `science: int`, `tactical: int`, `maintenance: bool` (True = on cooldown), `special_abilities: list[str]` (default empty)
- [ ] `src/zora/models/assignment.py` — `Assignment` dataclass with fields: `name: str`, `engineering: int`, `science: int`, `tactical: int`, `ship_slots: int`, `campaign: str`
- [ ] `src/zora/models/campaign.py` — `Campaign` dataclass with fields: `name: str` (and potentially progress/rewards later, but spec only requires name for milestone 1)
- [ ] `src/zora/models/board.py` — `BoardState` dataclass aggregating assignments and ships read from the board (the structured output the spec requires)
- [ ] Re-export models from `src/zora/models/__init__.py`
- [ ] Unit tests for model construction and field defaults in `tests/test_models.py`

## Priority 3 — Screen Capture

`src/zora/capture/` — isolated behind a simple interface so tests can inject fixture images.

- [ ] Define a capture interface/protocol: a callable or protocol class that returns a numpy array (BGR image)
- [ ] Implement `src/zora/capture/screenshot.py` — concrete implementation using a screenshot library (e.g., mss, pyautogui, or platform-specific) to capture the STO game window
- [ ] Implement `src/zora/capture/file.py` — a file-based implementation that loads an image from disk (for testing and development without a live game)
- [ ] Tests for the file-based capture using a small fixture image in `tests/fixtures/`

## Priority 4 — Vision: Board Detection

`src/zora/vision/` — locate the admiralty board UI within a screenshot.

- [ ] `src/zora/vision/detect.py` — function(s) to locate the admiralty board region within a full screenshot, returning bounding box coordinates or a cropped image
- [ ] `src/zora/vision/regions.py` — functions to identify sub-regions within the board: assignment cards, ship card slots, campaign indicator, stat areas
- [ ] Golden screenshot fixtures in `tests/fixtures/` for board detection tests
- [ ] Tests for board detection using fixture screenshots

## Priority 5 — Vision: Data Extraction (OCR)

Reading text and numbers from detected regions.

- [ ] `src/zora/vision/extract.py` — functions to extract assignment data from detected assignment regions (name, eng/sci/tac stats, ship slots, campaign)
- [ ] `src/zora/vision/extract.py` — functions to extract ship card data from detected ship regions (name, eng/sci/tac stats, maintenance status)
- [ ] OCR configuration tuned for STO's UI font/colors
- [ ] Tests for extraction accuracy against golden fixtures with known expected values

## Priority 6 — End-to-End Pipeline & CLI

Wire everything together.

- [ ] `src/zora/cli.py` — full CLI that captures → detects → extracts → outputs structured data (JSON or similar)
- [ ] `src/zora/pipeline.py` (or similar) — orchestration function: capture image → detect board → extract assignments → extract ships → return `BoardState`
- [ ] End-to-end test using fixture image → expected `BoardState`
- [ ] Structured output format (JSON to stdout, matching spec requirement 5)

## Notes

- **OCR library choice**: pytesseract (Tesseract wrapper) is the most common Python OCR option. EasyOCR or PaddleOCR are alternatives if Tesseract accuracy is poor on STO's UI. Decision should be made during Priority 5 based on testing with actual screenshots.
- **opencv-python-headless** preferred over opencv-python to avoid unnecessary GUI dependencies in the container.
- **Vision architecture**: per AGENTS.md, detection (finding regions) and extraction (reading data) must be kept separate. `detect.py`/`regions.py` handle detection; `extract.py` handles reading.
- **Test fixtures**: golden screenshots of the STO admiralty board are needed. These should be committed to `tests/fixtures/` and paired with expected output files or inline expected values in tests.
- **Critical Success**: mentioned in the spec's domain concepts but not in the milestone 1 requirements. It may be computed from Ship stats vs Assignment requirements — this is a derived value, not something to extract from the screen. Can be deferred or implemented as a simple utility function on the models.
