"""Captura de tela por clique — só o essencial.

Responsabilidades:
    - get_monitors(): lista de monitores via mss.
    - monitor_for_point(x, y): índice do monitor que contém o ponto.
    - capture_screen(x, y, out_path): captura o monitor que contém (x, y)
      e salva em out_path.
"""

from __future__ import annotations

from pathlib import Path


def get_monitors() -> list[dict]:
    """Retorna lista de monitores (exclui o virtual 'all' do mss)."""
    import mss

    with mss.mss() as sct:
        # sct.monitors[0] é o virtual box de todos; ignora
        return [m for m in sct.monitors[1:]]


def monitor_for_point(x: int, y: int) -> int:
    """Índice (0-based) do monitor que contém o ponto (x, y).

    Coordenadas virtuais multimonitor podem ser negativas (monitor à
    esquerda do primário). Se nenhum contém o ponto, retorna 0.
    """
    monitors = get_monitors()
    for i, m in enumerate(monitors):
        if (
            m["left"] <= x < m["left"] + m["width"]
            and m["top"] <= y < m["top"] + m["height"]
        ):
            return i
    return 0


def capture_screen(
    x: int,
    y: int,
    *,
    out_path: Path | str,
    monitor_index: int | None = None,
) -> Path:
    """Captura o monitor que contém (x, y) e salva em out_path.

    Se monitor_index for None, detecta automaticamente via
    monitor_for_point. Retorna o Path salvo.
    """
    import mss
    from mss.tools import to_png

    if monitor_index is None:
        monitor_index = monitor_for_point(x, y)

    monitors = get_monitors()
    if not monitors:
        raise RuntimeError("nenhum monitor detectado")

    idx = min(monitor_index, len(monitors) - 1)

    with mss.mss() as sct:
        mon_data = sct.monitors[1 + idx]  # mss: 0=virtual, 1=primeiro monitor
        img = sct.grab(mon_data)
        png_bytes = to_png(img.rgb, img.size)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(png_bytes)
    return out_path
