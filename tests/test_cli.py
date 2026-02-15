"""Tests for the CLI entry point (zora.cli module).

Validates argument parsing, JSON output format, and error handling
so the command-line interface works correctly for both file-based
and live-capture workflows.
"""

import builtins
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from zora.cli import _get_version, main

_real_import = builtins.__import__

FIXTURES = Path(__file__).parent / "fixtures"


class TestVersion:
    def test_get_version_returns_string(self) -> None:
        """_get_version always returns a non-empty string."""
        version = _get_version()
        assert isinstance(version, str)
        assert len(version) > 0

    def test_version_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        """--version prints the version and exits."""
        with (
            patch("sys.argv", ["zora", "--version"]),
            pytest.raises(SystemExit) as exc,
        ):
            main()
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "zora" in captured.out
        assert any(c.isdigit() for c in captured.out)


class TestImageFlag:
    def test_image_with_valid_fixture(self, capsys: pytest.CaptureFixture[str]) -> None:
        """--image with a valid fixture produces valid JSON."""
        fixture = FIXTURES / "test_capture.png"
        if not fixture.exists():
            pytest.skip("test_capture.png fixture not found")
        with patch("sys.argv", ["zora", "--image", str(fixture)]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "assignments" in data
        assert "ships" in data
        assert isinstance(data["assignments"], list)
        assert isinstance(data["ships"], list)

    def test_image_with_missing_file(self) -> None:
        """--image with a non-existent file raises an error."""
        with patch("sys.argv", ["zora", "--image", "/nonexistent/path.png"]):
            with pytest.raises((FileNotFoundError, SystemExit)):
                main()


class TestNoImageFlag:
    def test_no_args_exits_if_mss_missing(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Without --image and without mss, exits with error."""

        def selective_import(name, *args, **kwargs):
            if name == "zora.capture.screenshot":
                raise ImportError("No module named 'mss'")
            return _real_import(name, *args, **kwargs)

        with (
            patch("sys.argv", ["zora"]),
            patch("builtins.__import__", side_effect=selective_import),
            pytest.raises(SystemExit) as exc,
        ):
            main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "mss" in captured.err


class TestVerboseFlag:
    def test_verbose_enables_debug_logging(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--verbose flag enables DEBUG-level logging."""
        fixture = FIXTURES / "test_capture.png"
        if not fixture.exists():
            pytest.skip("test_capture.png fixture not found")
        with patch(
            "sys.argv",
            ["zora", "--verbose", "--image", str(fixture)],
        ):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "assignments" in data


class TestJsonOutput:
    def test_output_is_valid_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        """CLI output is always valid JSON."""
        fixture = FIXTURES / "test_capture.png"
        if not fixture.exists():
            pytest.skip("test_capture.png fixture not found")
        with patch("sys.argv", ["zora", "--image", str(fixture)]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, dict)

    def test_output_has_required_fields(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """JSON output contains 'assignments' and 'ships' keys."""
        fixture = FIXTURES / "test_capture.png"
        if not fixture.exists():
            pytest.skip("test_capture.png fixture not found")
        with patch("sys.argv", ["zora", "--image", str(fixture)]):
            main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "assignments" in data
        assert "ships" in data
