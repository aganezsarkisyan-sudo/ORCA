from __future__ import annotations

from pathlib import Path


def test_basic_structure() -> None:
    root = Path(__file__).resolve().parents[1]
    expected = [
        root / "main.py",
        root / "pyproject.toml",
        root / "app" / "ui" / "main_window.py",
    ]

    for p in expected:
        assert p.exists(), f"Expected {p} to exist"
