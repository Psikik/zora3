# Implementation Plan

## Current State

Priority 1 (Project Skeleton) and Priority 2 (Domain Models) are **complete**. The project
has a working `pyproject.toml`, package structure, CLI entry points (`zora` and `python -m zora`),
domain models with full test coverage (18 tests passing), and all validation passes.

### Implemented

- `pyproject.toml` — Python 3.12+, hatchling build, `zora` CLI entry point, deps: numpy, opencv-python-headless; dev: ruff, pytest
- `src/zora/` — package with `__init__.py`, `__main__.py`, `cli.py`
- `src/zora/models/` — `Ship`, `Assignment`, `Campaign`, `BoardState` dataclasses with `to_dict()` serialization
- `src/zora/capture/__init__.py`, `src/zora/vision/__init__.py` — empty subpackage stubs
- `tests/test_models.py` — 18 unit tests covering construction, defaults, serialization, mutable default isolation
- Assignment model includes spec milestone 1 fields: `duration`, `rarity`, `event_rewards` (beyond original plan)

### Key Decisions

- **No argparse yet** in CLI — will be added when the pipeline is wired (Priority 6)
- **Python 3.13.7** is the runtime (3.12+ in pyproject.toml)
- **hatchling** build backend with `src/` layout

## Priority 3 — Screen Capture

`src/zora/capture/` — isolated behind a simple interface so tests can inject fixture images.

- [ ] Define a capture interface/protocol: a callable or protocol class that returns a numpy array (BGR image)
- [ ] Implement `src/zora/capture/screenshot.py` — concrete implementation using a screenshot library (e.g., mss) to capture the STO game window
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

- [ ] `src/zora/cli.py` — full CLI with argparse (--image flag) that captures → detects → extracts → outputs structured data
- [ ] `src/zora/pipeline.py` — orchestration function: capture image → detect board → extract assignments → return `BoardState`
- [ ] End-to-end test using fixture image → expected `BoardState`
- [ ] Structured output format (JSON to stdout, matching spec requirement 4)

## Notes

- **OCR library choice**: pytesseract (Tesseract wrapper) is the most common Python OCR option. EasyOCR or PaddleOCR are alternatives if Tesseract accuracy is poor on STO's UI. Decision should be made during Priority 5 based on testing with actual screenshots.
- **opencv-python-headless** preferred over opencv-python to avoid unnecessary GUI dependencies in the container.
- **Vision architecture**: per AGENTS.md, detection (finding regions) and extraction (reading data) must be kept separate. `detect.py`/`regions.py` handle detection; `extract.py` handles reading.
- **Test fixtures**: golden screenshots of the STO admiralty board are needed. These should be committed to `tests/fixtures/` and paired with expected output files or inline expected values in tests.
- **Critical Success**: mentioned in the spec's domain concepts but not in the milestone 1 requirements. It may be computed from Ship stats vs Assignment requirements — this is a derived value, not something to extract from the screen. Can be deferred or implemented as a simple utility function on the models.
