"""GUI minimalista — janela de status do screen-click-capture.

Uma janela pequena (tkinter) que mostra:
    - Estado: "MONITORANDO" (cinza) ou "GRAVANDO" (vermelho pulsante)
    - Pasta de sessão atual
    - Contador de capturas
    - Dica: F9 liga/desliga

A janela fica visível o tempo todo (não minimiza — é pequena).
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from typing import Optional

# Estados de status
STATUS_MONITORING = "monitoring"
STATUS_RECORDING = "recording"

# Cores
_COLOR_MONITORING = "#607d8b"  # cinza-azulado
_COLOR_RECORDING = "#e53935"  # vermelho
_COLOR_BG = "#fafafa"
_COLOR_FG = "#212121"


class GUIApp:
    """Janela de status tkinter.

    Uso:
        gui = GUIApp(out_base=Path("capturas"))
        gui.start()          # abre a janela e entra no mainloop
        # ou (com o Recorder):
        gui = GUIApp(...)
        rec = Recorder(..., on_state_change=gui.on_state_change)
        gui.set_session(Path("capturas/20261124_1530-01"))
        gui.start()
    """

    def __init__(
        self,
        *,
        out_base: Path | str = Path("capturas"),
        hotkey: str = "f9",
    ):
        self._out_base = Path(out_base)
        self._hotkey = hotkey.upper()
        self._session_dir: Optional[Path] = None
        self._count = 0
        self._state = STATUS_MONITORING
        self._root: Optional[tk.Tk] = None

    # ── API pública ────────────────────────────────────────────────────────
    def set_session(self, session_dir: Path) -> None:
        """Define a pasta da sessão atual (chamado ao iniciar gravação)."""
        self._session_dir = Path(session_dir)
        self._count = 0
        self._update()

    def on_state_change(self, recording: bool) -> None:
        """Callback do Recorder: muda o estado visual.

        threading: o pynput chama de outra thread — usa .after().
        """
        state = STATUS_RECORDING if recording else STATUS_MONITORING
        if self._root is None:
            self._state = state
            return
        self._root.after(0, self._set_state, state)

    def on_capture(self, n: int, path: Path) -> None:
        """Callback: uma captura foi salva (n = número, path = onde)."""
        if self._root is None:
            self._count = n
            return
        self._root.after(0, self._bump_count, n)

    def start(self) -> None:
        """Abre a janela e entra no mainloop do tkinter."""
        self._root = tk.Tk()
        root = self._root
        root.title("Screen Click Capture")
        root.resizable(False, False)
        root.configure(bg=_COLOR_BG)

        # não centraliza — fica onde o Windows quiser (pequena)

        # label de status (grande)
        self._status_var = tk.StringVar(value="⏸ MONITORANDO")
        self._status_color = _COLOR_MONITORING
        lbl_status = tk.Label(
            root,
            textvariable=self._status_var,
            font=("Segoe UI", 16, "bold"),
            fg=self._status_color,
            bg=_COLOR_BG,
            padx=20,
            pady=(12, 4),
        )
        lbl_status.pack()

        # label de sessão/pasta
        self._session_var = tk.StringVar(value=f"Base: {self._out_base}")
        lbl_session = tk.Label(
            root,
            textvariable=self._session_var,
            font=("Consolas", 9),
            fg="#616161",
            bg=_COLOR_BG,
        )
        lbl_session.pack(pady=(0, 2))

        # label de contador
        self._count_var = tk.StringVar(value="0 capturas")
        lbl_count = tk.Label(
            root,
            textvariable=self._count_var,
            font=("Segoe UI", 11),
            fg=_COLOR_FG,
            bg=_COLOR_BG,
            pady=(0, 8),
        )
        lbl_count.pack()

        # dica de hotkey
        lbl_hint = tk.Label(
            root,
            text=f"Pressione {self._hotkey} para gravar/parar",
            font=("Segoe UI", 9),
            fg="#9e9e9e",
            bg=_COLOR_BG,
            pady=(0, 10),
        )
        lbl_hint.pack()

        # aplica o estado atual (pode já ser recording)
        self._apply_state(self._state)

        # blink loop
        self._blink_active = False
        self._blink_on = False

        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.mainloop()

    # ── interno ────────────────────────────────────────────────────────────
    def _set_state(self, state: str) -> None:
        self._state = state
        self._apply_state(state)

    def _apply_state(self, state: str) -> None:
        if self._root is None:
            return
        if state == STATUS_RECORDING:
            self._status_var.set("● GRAVANDO")
            self._status_color = _COLOR_RECORDING
            self._blink_active = True
            self._blink_on = True
        else:
            self._status_var.set("⏸ MONITORANDO")
            self._status_color = _COLOR_MONITORING
            self._blink_active = False
        # atualiza cor do label (procura pelo label de status)
        for w in self._root.winfo_children():
            if isinstance(w, tk.Label) and w.cget("font", "").find("bold") >= 0:
                w.configure(fg=self._status_color)
                break
        # reinicia o blink
        if self._blink_active:
            self._root.after(600, self._blink_tick)

    def _blink_tick(self) -> None:
        """Pulsa o texto GRAVANDO."""
        if not self._blink_active:
            return
        self._blink_on = not self._blink_on
        if self._root:
            for w in self._root.winfo_children():
                if isinstance(w, tk.Label) and w.cget("font", "").find("bold") >= 0:
                    w.configure(fg=_COLOR_RECORDING if self._blink_on else "#ffffff")
                    break
            self._root.after(600, self._blink_tick)

    def _bump_count(self, n: int) -> None:
        self._count = n
        self._count_var.set(f"{n} captura{'s' if n != 1 else ''}")
        if self._session_dir:
            self._session_var.set(str(self._session_dir))

    def _on_close(self) -> None:
        if self._root:
            self._root.destroy()
            self._root = None
