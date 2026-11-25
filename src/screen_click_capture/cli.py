"""CLI do screen-click-capture — entry point `scc`.

Uso:
    scc [--out PASTA] [--hotkey TECLA] [--no-gui]

Sessões: cada gravação cria uma pasta `capturas/YYYYMMDD_HHMM-NN/`.
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser
from pathlib import Path

from screen_click_capture import __version__
from screen_click_capture.session import next_session_dir


def _build_parser() -> ArgumentParser:
    p = ArgumentParser(
        prog="scc",
        description=(
            "Captura a tela a cada clique do mouse — salva PNGs "
            "sequenciais (01.png, 02.png, ...) numa pasta por sessão."
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
        help="Pasta base de saída (default: ./capturas)",
    )
    p.add_argument(
        "--hotkey",
        default="f9",
        help="Tecla que liga/desliga a gravação (default: f9)",
    )
    p.add_argument(
        "--no-gui",
        action="store_true",
        help="Roda sem a janela de status (só terminal)",
    )
    return p


def _run_gui(base: Path, hotkey: str) -> int:
    """Roda com GUI minimalista (tkinter) + pynput."""
    import threading
    import tkinter as tk
    from screen_click_capture.gui import (
        _COLOR_BG, _COLOR_FG, _COLOR_MONITORING, _COLOR_RECORDING,
    )
    from screen_click_capture.listener import Recorder

    session_dir = next_session_dir(base)
    session_dir.mkdir(parents=True, exist_ok=True)

    state = {"recording": False, "count": 0, "blink_on": True}
    _root: tk.Tk | None = None

    def on_state(recording: bool):
        state["recording"] = recording
        if _root is not None:
            _root.after(0, _update_status)

    def on_capture(n: int, path: Path):
        state["count"] = n
        if _root is not None:
            _root.after(0, _update_count, n)

    root = tk.Tk()
    root.title("Screen Click Capture")
    root.resizable(False, False)
    root.configure(bg=_COLOR_BG)

    status_var = tk.StringVar(value="⏸ MONITORANDO")
    session_var = tk.StringVar(value=str(session_dir))
    count_var = tk.StringVar(value="0 capturas")

    lbl_status = tk.Label(
        root, textvariable=status_var,
        font=("Segoe UI", 16, "bold"),
        fg=_COLOR_MONITORING, bg=_COLOR_BG, padx=20, pady=(12, 4),
    )
    lbl_status.pack()
    lbl_session = tk.Label(
        root, textvariable=session_var,
        font=("Consolas", 9), fg="#616161", bg=_COLOR_BG,
    )
    lbl_session.pack(pady=(0, 2))
    lbl_count = tk.Label(
        root, textvariable=count_var,
        font=("Segoe UI", 11), fg=_COLOR_FG, bg=_COLOR_BG, pady=(0, 8),
    )
    lbl_count.pack()
    lbl_hint = tk.Label(
        root, text=f"Pressione {hotkey.upper()} para gravar/parar",
        font=("Segoe UI", 9), fg="#9e9e9e", bg=_COLOR_BG, pady=(0, 10),
    )
    lbl_hint.pack()

    _root = root

    def _update_status():
        if state["recording"]:
            status_var.set("● GRAVANDO")
            fg = _COLOR_RECORDING if state["blink_on"] else "#ffffff"
            lbl_status.configure(fg=fg)
        else:
            status_var.set("⏸ MONITORANDO")
            lbl_status.configure(fg=_COLOR_MONITORING)

    def _update_count(n: int):
        count_var.set(f"{n} captura{'s' if n != 1 else ''}")

    def _blink():
        if state["recording"]:
            state["blink_on"] = not state["blink_on"]
            _update_status()
        if _root is not None:
            _root.after(600, _blink)

    def _on_close():
        if _root:
            _root.destroy()
            _root = None

    root.protocol("WM_DELETE_WINDOW", _on_close)
    _blink()

    rec = Recorder(
        out_dir=session_dir,
        hotkey=hotkey,
        on_state_change=on_state,
        on_capture=on_capture,
    )

    def run_rec():
        try:
            rec.run()
        except Exception as e:
            print(f"[scc] ERRO no recorder: {e!r}", flush=True)
        finally:
            if _root is not None:
                _root.after(0, _root.destroy)

    rec_thread = threading.Thread(target=run_rec, daemon=True)
    rec_thread.start()

    try:
        root.mainloop()
    except Exception:
        pass

    rec_thread.join(timeout=3)
    print(f"\n[scc] ✅ {state['count']} captura(s) em {session_dir}/", flush=True)
    return 0


def _run_cli(base: Path, hotkey: str) -> int:
    """Roda sem GUI (só terminal)."""
    from screen_click_capture.listener import Recorder

    session_dir = next_session_dir(base)
    session_dir.mkdir(parents=True, exist_ok=True)
    print(f"[scc] Sessão: {session_dir.name}", flush=True)

    rec = Recorder(out_dir=session_dir, hotkey=hotkey)
    return rec.run()


def main(argv: list | None = None) -> int:
    args = _build_parser().parse_args(argv)
    base = args.out
    hotkey = args.hotkey

    if args.no_gui:
        return _run_cli(base, hotkey)
    else:
        return _run_gui(base, hotkey)


if __name__ == "__main__":
    sys.exit(main())
