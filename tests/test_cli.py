"""Testes da CLI (só parse de args, sem pynput)."""

from __future__ import annotations

from pathlib import Path

from screen_click_capture.cli import _build_parser


def test_default_out():
    p = _build_parser()
    args = p.parse_args([])
    assert args.out == Path("capturas")


def test_default_hotkey():
    p = _build_parser()
    args = p.parse_args([])
    assert args.hotkey == "f9"


def test_custom_out():
    p = _build_parser()
    args = p.parse_args(["--out", "/tmp/meus-screenshots"])
    assert args.out == Path("/tmp/meus-screenshots")


def test_custom_hotkey():
    p = _build_parser()
    args = p.parse_args(["--hotkey", "f10"])
    assert args.hotkey == "f10"


def test_version():
    p = _build_parser()
    import pytest

    with pytest.raises(SystemExit) as exc:
        p.parse_args(["--version"])
    assert exc.value.code == 0
