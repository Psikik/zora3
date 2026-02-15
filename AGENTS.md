# Zora — Star Trek Online Automation

## Project Structure

```
zora/
├── src/zora/           # Application source
│   ├── capture/        # Screen capture and window detection
│   ├── vision/         # Image processing, region detection, OCR
│   ├── models/         # Domain data models (ships, assignments, campaigns)
│   └── cli.py          # Command-line entry point
├── tests/              # pytest tests
│   └── fixtures/       # Golden screenshots and expected outputs
├── specs/              # Requirement specs
└── pyproject.toml
```

## Build & Run

```bash
uv sync                          # Install dependencies
uv run zora                      # Run the tool
uv run python -m zora             # Alternative entry point
```

## Validation

Run all before committing:

```bash
uv run ruff check src/ tests/    # Lint
uv run ruff format --check src/ tests/  # Format check
uv run pytest                    # Tests
```

Fix formatting: `uv run ruff format src/ tests/`

## Codebase Patterns

- Python 3.12+, type hints on all public functions
- Domain models are dataclasses in `src/zora/models/`
- Screen capture is isolated behind a simple interface so tests can inject fixture images
- Vision code takes images as input (numpy arrays), never captures directly
- Tests use golden screenshots in `tests/fixtures/` as ground truth
- Keep OCR and image processing separate — detection finds regions, extraction reads them
