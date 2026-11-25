"""Gestão de sessões — uma pasta por gravação.

Nomenclatura: <base>/YYYYMMDD_HHMM-NN/
    - YYYYMMDD_HHMM: data e hora do início da sessão
    - NN: número sequencial da sessão no dia (01, 02, 03, ...)

Dentro da pasta, as capturas são sequenciais: 01.png, 02.png, ...
"""

from __future__ import annotations

import datetime
import re
from pathlib import Path


def _count_sessions_today(base: Path, date_prefix: str) -> int:
    """Conta as pastas de sessão que já existem para a data de hoje."""
    if not base.exists():
        return 0
    pattern = re.compile(rf"^{re.escape(date_prefix)}-(\d{{2}})$")
    max_n = 0
    for d in base.iterdir():
        if not d.is_dir():
            continue
        m = pattern.match(d.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return max_n


def next_session_dir(
    base: Path | str = Path("capturas"),
    *,
    now: datetime.datetime | None = None,
) -> Path:
    """Retorna o Path da próxima pasta de sessão (sem criar).

    Formato: <base>/YYYYMMDD_HHMM-NN/

    Se a base não existir, cria. A própria pasta de sessão é criada
    pelo chamador (CLI/GUI) quando a gravação inicia.
    """
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)

    if now is None:
        now = datetime.datetime.now()

    date_prefix = now.strftime("%Y%m%d_%H%M")
    existing = _count_sessions_today(base, date_prefix)
    nn = existing + 1

    return base / f"{date_prefix}-{nn:02d}"
