"""Testes da capture.py (com mocks de mss)."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_monitor_for_point_primary(monkeypatch):
    """Ponto dentro do monitor primário → índice 0."""
    import screen_click_capture.capture as cap

    monkeypatch.setattr(
        cap,
        "get_monitors",
        lambda: [
            {"left": 0, "top": 0, "width": 1920, "height": 1080, "is_primary": True},
        ],
    )
    assert cap.monitor_for_point(100, 200) == 0


def test_monitor_for_point_secondary(monkeypatch):
    """Ponto no monitor secundário (à direita) → índice 1."""
    import screen_click_capture.capture as cap

    monkeypatch.setattr(
        cap,
        "get_monitors",
        lambda: [
            {"left": 0, "top": 0, "width": 1920, "height": 1080, "is_primary": True},
            {"left": 1920, "top": 0, "width": 1920, "height": 1080, "is_primary": False},
        ],
    )
    assert cap.monitor_for_point(2000, 500) == 1


def test_monitor_for_point_left_monitor(monkeypatch):
    """Ponto no monitor à esquerda (coordenada negativa) → índice 1."""
    import screen_click_capture.capture as cap

    monkeypatch.setattr(
        cap,
        "get_monitors",
        lambda: [
            {"left": 0, "top": 0, "width": 1920, "height": 1080, "is_primary": True},
            {"left": -1920, "top": 0, "width": 1920, "height": 1080, "is_primary": False},
        ],
    )
    assert cap.monitor_for_point(-100, 500) == 1


def test_monitor_for_point_out_of_bounds(monkeypatch):
    """Ponto fora de qualquer monitor → 0 (primário)."""
    import screen_click_capture.capture as cap

    monkeypatch.setattr(
        cap,
        "get_monitors",
        lambda: [
            {"left": 0, "top": 0, "width": 1920, "height": 1080, "is_primary": True},
        ],
    )
    assert cap.monitor_for_point(5000, 5000) == 0


def test_capture_screen_saves_png(tmp_path, monkeypatch):
    """capture_screen grava um arquivo PNG válido."""
    import struct
    import zlib

    import screen_click_capture.capture as cap

    # mock get_monitors
    monkeypatch.setattr(
        cap,
        "get_monitors",
        lambda: [
            {"left": 0, "top": 0, "width": 100, "height": 100, "is_primary": True},
        ],
    )

    # mock mss
    class FakeImg:
        rgb = b"\x00\x00\x00" * 100 * 100 * 3
        size = (100, 100)

    class FakeSct:
        monitors = [
            {"left": -1, "top": -1, "width": 101, "height": 101},  # virtual
            {"left": 0, "top": 0, "width": 100, "height": 100},  # real
        ]

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def grab(self, mon):
            return FakeImg()

    class FakeMss:
        def __enter__(self):
            return FakeSct()

        def __exit__(self, *a):
            pass

    import mss
    monkeypatch.setattr(mss, "mss", FakeMss)

    out = tmp_path / "test.png"
    cap.capture_screen(50, 50, out_path=out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_capture_screen_creates_parent_dirs(tmp_path, monkeypatch):
    """capture_screen cria a pasta de saída se não existir."""
    import screen_click_capture.capture as cap

    monkeypatch.setattr(
        cap,
        "get_monitors",
        lambda: [
            {"left": 0, "top": 0, "width": 100, "height": 100, "is_primary": True},
        ],
    )

    class FakeImg:
        rgb = b"\x00" * 300
        size = (10, 10)

    class FakeSct:
        monitors = [
            {"left": -1, "top": -1, "width": 11, "height": 11},
            {"left": 0, "top": 0, "width": 10, "height": 10},
        ]

        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def grab(self, mon):
            return FakeImg()

    class FakeMss:
        def __enter__(self):
            return FakeSct()

        def __exit__(self, *a):
            pass

    import mss
    monkeypatch.setattr(mss, "mss", FakeMss)

    out = tmp_path / "a" / "b" / "c.png"
    cap.capture_screen(5, 5, out_path=out)
    assert out.exists()
