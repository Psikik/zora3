# Implementation Plan

## Current State

**Milestone 1 is functionally complete.** All six priorities are implemented with 56 tests passing and all validation green. The system can:
1. Capture a screenshot (from file or live screen)
2. Detect the admiralty board region via color-based segmentation
3. Find individual assignment card sub-regions within the board
4. Extract assignment details via Tesseract OCR (name, stats, slots, duration, rarity)
5. Output structured JSON to stdout

### Implemented

- `pyproject.toml` — Python 3.12+, hatchling build, `zora` CLI entry point, deps: numpy, opencv-python-headless, pytesseract; dev: ruff, pytest
- `src/zora/cli.py` — argparse CLI with `--image`, `--verbose`, `--version` flags; outputs JSON
- `src/zora/pipeline.py` — orchestration: capture → detect board → find cards → extract assignments → BoardState
- `src/zora/models/` — `Ship`, `Assignment`, `Campaign`, `BoardState` dataclasses with `to_dict()`
- `src/zora/capture/` — `CaptureSource` protocol, `FileCapture`, `ScreenshotCapture` (mss, lazy)
- `src/zora/vision/detect.py` — HSV-based board region detection with morphological cleanup
- `src/zora/vision/regions.py` — HSV-based card region detection within board, sorted by position
- `src/zora/vision/extract.py` — Tesseract OCR with preprocessing (GaussianBlur + OTSU), text parsing for stats/duration/rarity
- `src/zora/vision/__init__.py` — `BoundingBox` frozen dataclass
- 56 tests across 6 test files; synthetic fixtures in `tests/fixtures/`

### Key Decisions

- **Python 3.13.7** runtime (3.12+ in pyproject.toml), **hatchling** build backend
- **Tesseract 5.5.0** for OCR via pytesseract; `--oem 3 --psm 6` for block text, `--psm 7` for digits
- **GaussianBlur + OTSU** threshold instead of adaptiveThreshold (crashes on ARM/aarch64 with opencv-python-headless)
- **CaptureSource** is a `Protocol` — any callable returning `BGRImage` (NDArray[np.uint8]) satisfies it
- **mss** lazy-imported in ScreenshotCapture to avoid failures in headless environments
- **HSV color ranges**: board bg [0,0,10]–[180,120,60], card bg [0,0,80]–[180,100,200]

## Known Limitations

- **OCR accuracy with synthetic text** is approximate — OpenCV's `putText` renders differently from STO's game font. Real screenshots may need HSV range tuning and OCR config adjustments.
- **No real STO screenshots** yet. The synthetic fixtures validate the pipeline architecture but calibration against real game UI is pending.
- **Science stat extraction** is inconsistent with synthetic images — the OCR sometimes misses "Sci:" text. Works well with the text parser when OCR output is clean.

## Future Work

- [ ] **Real screenshot calibration**: capture actual STO admiralty board screenshots, adjust HSV ranges and OCR config
- [ ] **Ship roster reading**: milestone 2 per spec — separate screen from assignments
- [ ] **Critical Success computation**: derive from ship stats vs assignment requirements (pure model logic)
- [ ] **mss dependency**: add as optional dependency for live capture environments
- [ ] **OCR alternatives**: evaluate EasyOCR or PaddleOCR if Tesseract accuracy is poor on real STO fonts

## Notes

- **adaptiveThreshold crashes** on aarch64 with opencv-python-headless 4.13 — use GaussianBlur + OTSU as workaround
- **Tesseract must be system-installed** (`apt-get install tesseract-ocr`) — pytesseract is just a wrapper
- **Vision architecture**: detection (detect.py/regions.py) and extraction (extract.py) are strictly separated per AGENTS.md
