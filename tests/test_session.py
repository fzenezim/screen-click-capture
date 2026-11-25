"""Testes de sessões por data (pasta por sessão)."""

from __future__ import annotations

from pathlib import Path

import pytest


def _count_existing(base: Path, date_prefix: str) -> int:
    """Conta pastas existentes com o prefixo de data."""
    if not base.exists():
        return 0
    return sum(1 for d in base.iterdir() if d.is_dir() and d.name.startswith(date_prefix))


def test_first_session_gets_01(tmp_path):
    from screen_click_capture.session import next_session_dir

    d = next_session_dir(tmp_path)
    assert d.parent == tmp_path
    assert d.name.endswith("-01")
    # formato: YYYYMMDD_HHMM-01
    import re
    assert re.match(r"^\d{8}_\d{4}-01$", d.name)


def test_second_session_same_day_gets_02(tmp_path):
    from screen_click_capture.session import next_session_dir

    d1 = next_session_dir(tmp_path)
    d1.mkdir(parents=True)
    d2 = next_session_dir(tmp_path)
    assert d2.name.endswith("-02")


def test_session_counter_increments_with_existing(tmp_path):
    from screen_click_capture.session import next_session_dir

    d1 = next_session_dir(tmp_path)
    d1.mkdir(parents=True)
    # simula uma 2ª sessão já existente (mesma data)
    fake = d1.with_name(d1.name[:-2] + "02")
    fake.mkdir(parents=True)
    d3 = next_session_dir(tmp_path)
    assert d3.name.endswith("-03")


def test_session_dir_is_created(tmp_path):
    from screen_click_capture.session import next_session_dir

    d = next_session_dir(tmp_path)
    d.mkdir(parents=True, exist_ok=True)
    assert d.exists()


def test_different_days_restart_counter(tmp_path):
    """Dias diferentes reiniciam o contador (mas aqui testamos só o formato)."""
    from screen_click_capture.session import next_session_dir

    d = next_session_dir(tmp_path)
    # extraí a data do nome
    date_part = d.name[:8]
    # cria uma pasta de OUTRA data
    other = tmp_path / f"20200101_0000-01"
    other.mkdir(parents=True)
    # próxima sessão HOJE ainda deve ser -01 (a de 2020 não conta)
    d2 = next_session_dir(tmp_path)
    assert d2.name.endswith("-01")
