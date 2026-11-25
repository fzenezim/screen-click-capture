"""Testes do GUI minimalista (só lógica, sem abrir janela real)."""

from __future__ import annotations

import pytest


def test_gui_module_imports():
    """O módulo gui importa sem erro (não abre janela no import)."""
    import screen_click_capture.gui  # noqa: F401


def test_gui_has_status_constants():
    from screen_click_capture.gui import STATUS_MONITORING, STATUS_RECORDING

    assert STATUS_MONITORING is not None
    assert STATUS_RECORDING is not None
    assert STATUS_MONITORING != STATUS_RECORDING


def test_gui_app_has_on_state_change():
    """GUIApp tem o método on_state_change."""
    from screen_click_capture.gui import GUIApp

    assert hasattr(GUIApp, "on_state_change")
    assert callable(GUIApp.on_state_change)
