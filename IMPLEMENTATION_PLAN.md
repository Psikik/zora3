# Implementation Plan

## Current State

**Milestone 1 is partially complete.** Core pipeline architecture is in place and functional — capture, board detection, card region detection, OCR extraction, and JSON output all work end-to-end. However, several spec requirements remain unimplemented and test gaps exist.

### What Works

- `pyproject.toml` — Python 3.12+, hatchling build, `zora` CLI entry point, deps: numpy, opencv-python-headless, pytesseract; dev: ruff, pytest
- `src/zora/cli.py` — argparse CLI with `--image`, `--verbose`, `--version` flags; outputs JSON
- `src/zora/pipeline.py` — orchestration: capture → detect board → find cards → extract assignments → BoardState
- `src/zora/models/` — `Ship`, `Assignment`, `Campaign`, `BoardState` dataclasses with `to_dict()`
- `src/zora/capture/` — `CaptureSource` protocol, `FileCapture`, `ScreenshotCapture` (mss, lazy import)
- `src/zora/vision/detect.py` — HSV-based board region detection with morphological cleanup
- `src/zora/vision/regions.py` — HSV-based card region detection within board, sorted by position
- `src/zora/vision/extract.py` — Tesseract OCR with preprocessing (GaussianBlur + OTSU), text parsing for stats/duration/rarity
- `src/zora/vision/__init__.py` — `BoundingBox` frozen dataclass
- 52 tests pass (across 8 test files); 4 tests fail when tesseract binary not installed; synthetic fixtures in `tests/fixtures/`

### Key Decisions

- **Python 3.13.7** runtime (3.12+ in pyproject.toml), **hatchling** build backend
- **Tesseract 5.5.0** for OCR via pytesseract; `--oem 3 --psm 6` for block text, `--psm 7` for digits
- **GaussianBlur + OTSU** threshold instead of adaptiveThreshold (crashes on ARM/aarch64 with opencv-python-headless)
- **CaptureSource** is a `Protocol` — any callable returning `BGRImage` (NDArray[np.uint8]) satisfies it
- **mss** lazy-imported in ScreenshotCapture to avoid failures in headless environments
- **HSV color ranges**: board bg [0,0,10]–[180,120,60], card bg [0,0,80]–[180,100,200]

## Remaining Work — Priority 1 (Blocking/Correctness)

- [ ] **P1-1: Declare `mss` as optional dependency** — `ScreenshotCapture` imports `mss` at runtime but it is not listed in `pyproject.toml`. Add as optional dependency (e.g., `[project.optional-dependencies] capture = ["mss"]`). Files: `pyproject.toml`.

- [ ] **P1-2: CLI must attempt live capture when no `--image` provided** — Spec requirement 1 says "Capture a screenshot of the STO game window." Currently `cli.py` returns a hardcoded empty `BoardState` in the no-argument path (lines 43-45) instead of using `ScreenshotCapture`. Should use `ScreenshotCapture` as default source, with graceful error if `mss` is not installed. Depends on P1-1. Files: `src/zora/cli.py`.

- [ ] **P1-3: `event_rewards` extraction is unimplemented** — Spec requirement 3 explicitly lists "Event rewards" as a required extracted field. The `Assignment` model has the `event_rewards: list[str]` field, but `parse_assignment_text()` never populates it and `extract_assignment()` never passes it through. Every extracted assignment has `event_rewards: []`. Add regex pattern matching for event reward text and wire through extraction. Files: `src/zora/vision/extract.py`, `tests/test_vision_extract.py`.

- [ ] **P1-4: OCR tests fail without tesseract binary** — 4 tests in `test_vision_extract.py` (`TestOcrText.test_reads_clear_text`, `TestOcrText.test_reads_numbers`, `TestOcrNumber.test_extracts_number`, `TestExtractAssignment.test_returns_assignment_object`) call Tesseract directly and fail with `TesseractNotFoundError` when the binary is absent. Add `pytest.mark.skipif(shutil.which("tesseract") is None, ...)` guard. Files: `tests/test_vision_extract.py` or `tests/conftest.py`.

## Remaining Work — Priority 2 (Quality/Robustness)

- [ ] **P2-1: Add CLI test coverage** — `main()` in `cli.py` has zero test coverage. Need tests for: `--image` with valid fixture producing JSON, `--image` with missing file, no arguments, `--version` output, `--verbose` logging level. Files: new `tests/test_cli.py`.

- [ ] **P2-2: Add ScreenshotCapture mock tests** — `screenshot.py` is completely untested. Add mock-based tests for BGRA→BGR conversion, monitor parameter passthrough, and `CaptureSource` protocol conformance. Files: `tests/test_capture.py`.

- [ ] **P2-3: Read version from package metadata instead of hardcoding** — `cli.py` line 22 hardcodes `version="%(prog)s 0.1.0"`. Use `importlib.metadata.version("zora")` to read from pyproject.toml at runtime so versions stay in sync. Files: `src/zora/cli.py`.

- [ ] **P2-4: Extract magic numbers to named constants** — `vision/extract.py` has inline thresholds (h < 100, w < 200, scale 2.0, blur kernel (5,5)). `vision/detect.py` has morph kernel (15,15). `vision/regions.py` has morph kernel (5,5). Extract to descriptive module-level constants. Files: `src/zora/vision/extract.py`, `src/zora/vision/detect.py`, `src/zora/vision/regions.py`.

- [ ] **P2-5: Surface extraction failures to user** — Pipeline catches all exceptions during card extraction (`except Exception` at `pipeline.py:63`) and logs them, but failures are invisible without `--verbose`. Consider adding stderr warning or errors field to output when cards fail extraction. Files: `src/zora/pipeline.py`, potentially `src/zora/cli.py`.

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
