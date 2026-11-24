"""Testes do ClickCapture (listener sem pynput — eventos sintéticos)."""

from __future__ import annotations

from pathlib import Path

import pytest

from screen_click_capture.listener import ClickCapture


class FakeKey:
    def __init__(self, name: str):
        self.name = name


@pytest.fixture
def out_dir(tmp_path):
    d = tmp_path / "capturas"
    d.mkdir()
    return d


def test_starts_stopped(out_dir):
    cc = ClickCapture(out_dir=out_dir)
    assert cc.is_recording is False


def test_hotkey_toggles_recording(out_dir):
    cc = ClickCapture(out_dir=out_dir, hotkey="f9")
    assert cc.is_recording is False
    cc.on_key_press(FakeKey("f9"))
    assert cc.is_recording is True
    cc.on_key_press(FakeKey("f9"))
    assert cc.is_recording is False


def test_non_hotkey_does_not_toggle(out_dir):
    cc = ClickCapture(out_dir=out_dir, hotkey="f9")
    cc.on_key_press(FakeKey("a"))
    assert cc.is_recording is False
    cc.on_key_press(FakeKey("f10"))
    assert cc.is_recording is False


def test_click_not_recorded_when_stopped(out_dir, monkeypatch):
    cc = ClickCapture(out_dir=out_dir)
    captured = []
    monkeypatch.setattr(
        "screen_click_capture.capture.capture_screen",
        lambda x, y, out_path: captured.append(out_path),
    )
    cc.on_mouse_click(100, 200, "left")
    assert captured == []


def test_click_captures_when_recording(out_dir, monkeypatch):
    cc = ClickCapture(out_dir=out_dir)
    cc.is_recording = True
    captured = []
    monkeypatch.setattr(
        "screen_click_capture.capture.capture_screen",
        lambda x, y, out_path: captured.append(str(out_path)),
    )
    cc.on_mouse_click(100, 200, "left")
    assert len(captured) == 1
    assert captured[0].endswith("01.png")


def test_sequential_numbering(out_dir, monkeypatch):
    cc = ClickCapture(out_dir=out_dir)
    cc.is_recording = True
    captured = []
    monkeypatch.setattr(
        "screen_click_capture.capture.capture_screen",
        lambda x, y, out_path: captured.append(Path(out_path).name),
    )
    cc.on_mouse_click(10, 10, "left")
    cc.on_mouse_click(20, 20, "left")
    cc.on_mouse_click(30, 30, "right")
    assert captured == ["01.png", "02.png", "03.png"]


def test_numbering_resets_after_restart(out_dir, monkeypatch):
    cc = ClickCapture(out_dir=out_dir)
    captured = []
    monkeypatch.setattr(
        "screen_click_capture.capture.capture_screen",
        lambda x, y, out_path: captured.append(Path(out_path).name),
    )
    # 1ª sessão
    cc.is_recording = True
    cc.on_mouse_click(10, 10, "left")
    cc.is_recording = False
    # 2ª sessão (novo counter? não — continua sequencial)
    cc.is_recording = True
    cc.on_mouse_click(20, 20, "left")
    assert captured == ["01.png", "02.png"]


def test_on_state_change_callback(out_dir):
    states = []
    cc = ClickCapture(out_dir=out_dir, on_state_change=states.append)
    cc.on_key_press(FakeKey("f9"))
    assert states == [True]
    cc.on_key_press(FakeKey("f9"))
    assert states == [True, False]


def test_custom_hotkey(out_dir):
    cc = ClickCapture(out_dir=out_dir, hotkey="f10")
    cc.on_key_press(FakeKey("f10"))
    assert cc.is_recording is True
    cc.on_key_press(FakeKey("f9"))  # não é o hotkey custom
    assert cc.is_recording is True  # continua gravando


def test_capture_failure_does_not_crash(out_dir, monkeypatch, capsys):
    cc = ClickCapture(out_dir=out_dir)
    cc.is_recording = True

    def fail(x, y, out_path):
        raise RuntimeError("no display")

    monkeypatch.setattr(
        "screen_click_capture.capture.capture_screen",
        fail,
    )
    # não deve lançar
    cc.on_mouse_click(100, 200, "left")
    out = capsys.readouterr().out
    assert "ERRO" in out
