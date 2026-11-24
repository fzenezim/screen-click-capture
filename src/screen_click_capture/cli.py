"""CLI do screen-click-capture — entry point `scc`.

Uso:
    scc [--out PASTA] [--hotkey TECLA]
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser
from pathlib import Path

from screen_click_capture import __version__


def _build_parser() -> ArgumentParser:
    p = ArgumentParser(
        prog="scc",
        description=(
            "Captura a tela a cada clique do mouse — salva PNGs "
            "sequenciais (01.png, 02.png, ...)."
        ),
    )
    p.add_argument(
        "--version",
        action="version",
        version=f"scc {__version__}",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("capturas"),
        help="Pasta de saída dos PNGs (default: ./capturas)",
    )
    p.add_argument(
        "--hotkey",
        default="f9",
        help="Tecla que liga/desliga a gravação (default: f9)",
    )
    return p


def main(argv: list | None = None) -> int:
    args = _build_parser().parse_args(argv)

    # garante que a pasta existe
    args.out.mkdir(parents=True, exist_ok=True)

    from screen_click_capture.listener import Recorder

    rec = Recorder(out_dir=args.out, hotkey=args.hotkey)
    return rec.run()


if __name__ == "__main__":
    sys.exit(main())
