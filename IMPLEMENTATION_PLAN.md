# Implementation Plan

## Current State

**Milestone 1 is complete. All P1 and P2 items resolved.** Core pipeline architecture is in place and functional — capture, board detection, card region detection, OCR extraction, and JSON output all work end-to-end. Error reporting surfaces extraction failures to users via stderr warnings and an `errors` field in JSON output.

### What Works

- `pyproject.toml` — Python 3.12+, hatchling build, `zora` CLI entry point, deps: numpy, opencv-python-headless, pytesseract; dev: ruff, pytest; optional: `mss` for live capture
- `src/zora/cli.py` — argparse CLI with `--image`, `--verbose`, `--version` flags; outputs JSON; attempts live capture via `ScreenshotCapture` when no `--image` provided; version read from `importlib.metadata`; stderr warning when card extraction fails
- `src/zora/pipeline.py` — orchestration: capture → detect board → find cards → extract assignments → BoardState; collects extraction errors into BoardState.errors
- `src/zora/models/` — `Ship`, `Assignment`, `Campaign`, `BoardState` dataclasses with `to_dict()`; BoardState includes optional `errors` field
- `src/zora/capture/` — `CaptureSource` protocol, `FileCapture`, `ScreenshotCapture` (mss, lazy import)
- `src/zora/vision/detect.py` — HSV-based board region detection with morphological cleanup; magic numbers extracted to named constants
- `src/zora/vision/regions.py` — HSV-based card region detection within board, sorted by position; magic numbers extracted to named constants
- `src/zora/vision/extract.py` — Tesseract OCR with preprocessing (GaussianBlur + OTSU), text parsing for stats/duration/rarity/event_rewards; magic numbers extracted to named constants
- `src/zora/vision/__init__.py` — `BoundingBox` frozen dataclass
- 74 tests (70 pass, 4 skipped for Tesseract); full coverage including ScreenshotCapture mock tests, CLI, models, pipeline, and all vision modules

### Key Decisions

- **Python 3.13.7** runtime (3.12+ in pyproject.toml), **hatchling** build backend
- **Tesseract 5.5.0** for OCR via pytesseract; `--oem 3 --psm 6` for block text, `--psm 7` for digits
- **GaussianBlur + OTSU** threshold instead of adaptiveThreshold (crashes on ARM/aarch64 with opencv-python-headless)
- **CaptureSource** is a `Protocol` — any callable returning `BGRImage` (NDArray[np.uint8]) satisfies it
- **mss** lazy-imported in ScreenshotCapture to avoid failures in headless environments
- **HSV color ranges**: board bg [0,0,10]–[180,120,60], card bg [0,0,80]–[180,100,200]
- **Errors field** in BoardState is conditional — only included in JSON when errors are present, keeping clean output for successful runs

## Remaining Work — Priority 3 (Future/Enhancement)

- [ ] **P3-1: Real screenshot calibration** — All vision tests use synthetic images. Capture actual STO admiralty board screenshots, add to `tests/fixtures/`, validate and tune HSV ranges and OCR config against real game UI. Files: `tests/fixtures/`, vision modules.

- [ ] **P3-2: Campaign model is minimal** — Spec defines Campaign as having "progress tracking and associated rewards" but the model only has `name: str`. Add progress, reward, and tour-of-duty fields when campaign functionality is needed (milestone 2+). Files: `src/zora/models/campaign.py`, `tests/test_models.py`.

- [ ] **P3-3: Ship roster reading (Milestone 2)** — Spec notes assignment view and ship roster are separate screens. Current implementation handles assignment view only. `Ship` model already exists. Files: new vision modules, pipeline updates, CLI updates.

- [ ] **P3-4: Critical Success computation** — Spec defines this as "ship stats exceed assignment requirements." Pure model logic, no vision work needed. Files: `src/zora/models/assignment.py` or new module.

- [ ] **P3-5: Alternative OCR engines** — Evaluate EasyOCR or PaddleOCR if Tesseract accuracy is poor on real STO fonts. These are pip-installable and may handle game UI text better. Files: `src/zora/vision/extract.py`, `pyproject.toml`.

## Known Limitations

- **OCR accuracy with synthetic text** is approximate — OpenCV's `putText` renders differently from STO's game font. Real screenshots may need HSV range tuning and OCR config adjustments.
- **No real STO screenshots** yet. The synthetic fixtures validate the pipeline architecture but calibration against real game UI is pending.
- **Science stat extraction** is inconsistent with synthetic images — the OCR sometimes misses "Sci:" text. Works well with the text parser when OCR output is clean.

## Notes

- **adaptiveThreshold crashes** on aarch64 with opencv-python-headless 4.13 — use GaussianBlur + OTSU as workaround
- **Tesseract must be system-installed** (`apt-get install tesseract-ocr`) — pytesseract is just a wrapper
- **Vision architecture**: detection (detect.py/regions.py) and extraction (extract.py) are strictly separated per AGENTS.md
