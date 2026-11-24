"""Listener pynput — captura cliques e dispara screenshot sequencial.

Só o essencial: cada clique do mouse → captura a tela inteira do monitor
que contém o cursor → salva como NN.png na pasta de saída.

Sem gravação de texto, sem crops de âncora, sem replay.
"""

from __future__ import annotations

import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


@dataclass
class _MouseEvent:
    """Adapter: pynput passa (x, y, button, pressed) — normaliza."""
    x: int
    y: int
    button: str = "left"


class ClickCapture:
    """Coleciona cliques e dispara capturas de tela sequenciais.

    Argumentos:
        out_dir: pasta onde os PNGs serão salvos (01.png, 02.png, ...)
        hotkey: tecla de toggle (default "f9")
        on_state_change: callback opcional (is_recording: bool)
    """

    def __init__(
        self,
        *,
        out_dir: Path | str = Path("capturas"),
        hotkey: Optional[str] = "f9",
        on_state_change: Optional[Callable[[bool], None]] = None,
    ):
        self._out_dir = Path(out_dir)
        self._hotkey = (hotkey or "f9").lower()
        self._on_state_change = on_state_change
        self.is_recording = False
        self._counter = 0

    # ── hotkey ─────────────────────────────────────────────────────────────
    def _is_hotkey(self, key) -> bool:
        """True se a tecla é a do hotkey."""
        name = getattr(key, "name", None)
        if isinstance(name, str):
            return name == self._hotkey
        return False

    def _notify_state(self) -> None:
        if self._on_state_change is None:
            return
        try:
            self._on_state_change(self.is_recording)
        except Exception:
            pass

    # ── callbacks ──────────────────────────────────────────────────────────
    def on_key_press(self, key) -> None:
        """Chamado a cada tecla pressionada (pynput)."""
        if self._is_hotkey(key):
            self.is_recording = not self.is_recording
            self._notify_state()
            return

    def on_mouse_click(self, x: int, y: int, button: str = "left") -> None:
        """Chamado a cada clique do mouse (apenas 'pressed').

        Se estiver gravando, captura a tela e salva como NN.png.
        """
        if not self.is_recording:
            return

        self._counter += 1
        nn = f"{self._counter:02d}"
        out_path = self._out_dir / f"{nn}.png"

        try:
            from screen_click_capture.capture import capture_screen
            capture_screen(x, y, out_path=out_path)
            print(f"  [{nn}] {out_path}", flush=True)
        except Exception as e:
            print(f"  [{nn}] ERRO na captura: {e!r}", flush=True)


# ═════════════════════════════════════════════════════════════════════════
# Recorder — wrapper com pynput (runtime real)
# ═════════════════════════════════════════════════════════════════════════
class Recorder:
    """Gravador com listeners globais pynput.

    Uso:
        rec = Recorder(out_dir=Path("./capturas"))
        rec.run()   # bloqueia até o 2º F9 (ou Ctrl+C para cancelar)

    Fluxo:
        1. run() → "aguardando F9 ..."
        2. F9 → "GRAVANDO..."
        3. cliques → screenshots salvos
        4. F9 → "PARADO"
    """

    def __init__(
        self,
        *,
        out_dir: Path | str = Path("capturas"),
        hotkey: Optional[str] = "f9",
        on_state_change: Optional[Callable[[bool], None]] = None,
    ):
        from pynput import keyboard, mouse  # noqa: F401 — checa disponibilidade

        self._collector = ClickCapture(
            out_dir=out_dir,
            hotkey=hotkey,
            on_state_change=on_state_change,
        )
        self._toggle_event: threading.Event = threading.Event()
        self._ready: threading.Event = threading.Event()
        self._was_started = False
        self._running = False

    def wait_ready(self, timeout: float = 6.0) -> bool:
        """Espera o listener pynput estar ativo."""
        return self._ready.wait(timeout)

    def toggle(self) -> bool:
        """Aciona o toggle do hotkey (thread-safe)."""
        self._toggle_event.set()
        return self._collector.is_recording

    # ── callbacks pynput ───────────────────────────────────────────────────
    def _notify(self) -> None:
        if self._collector._on_state_change:
            try:
                self._collector._on_state_change(self._collector.is_recording)
            except Exception:
                pass

    def _on_key_press(self, key, *a):
        if self._collector._is_hotkey(key):
            self._collector.on_key_press(key)
            hk = self._collector._hotkey.upper()
            if self._collector.is_recording:
                self._was_started = True
                print(
                    f"\n[scc] >>> GRAVANDO...  (2ª {hk} para PARAR | Ctrl+C cancela)",
                    flush=True,
                )
            else:
                print("\n[scc] <<< PARADO.", flush=True)
            return

    def _on_mouse_move(self, x, y):
        pass  # não usamos move

    def _on_mouse_click(self, x, y, button, pressed):
        if not pressed:
            return
        # normaliza o botão pynput (Button.left → "left")
        try:
            from pynput.mouse import Button
            for name in ("left", "middle", "right"):
                if button == getattr(Button, name, None):
                    button = name
                    break
        except Exception:
            pass

        self._collector.on_mouse_click(int(x), int(y), str(button))

    def _programmatic_toggle(self) -> None:
        """Toggle programático (GUI/teste) — mesmo efeito do hotkey."""
        hk = self._collector._hotkey
        before = self._collector.is_recording
        self._collector.is_recording = not before
        self._collector._notify_state()
        if not before and self._collector.is_recording:
            self._was_started = True
            print(
                f"\n[scc] >>> GRAVANDO...  (2ª {hk.upper()} para PARAR | Ctrl+C cancela)",
                flush=True,
            )
        elif before and not self._collector.is_recording:
            print("\n[scc] <<< PARADO.", flush=True)

    def run(self) -> int:
        """Executa o loop de gravação. Retorna 0 (sucesso) ou 1 (cancelado)."""
        from pynput import keyboard, mouse
        import time as _t

        hk = self._collector._hotkey.upper()
        print(
            f"[scc] Pressione {hk} para LIGAR a gravação; 2ª {hk} para PARAR.",
            flush=True,
        )
        print(
            f"[scc] Pasta de saída: {self._collector._out_dir}",
            flush=True,
        )

        self._running = True
        self._ready.clear()
        self._collector.is_recording = False
        self._was_started = False

        try:
            with keyboard.Listener(on_press=self._on_key_press) as kl, \
                 mouse.Listener(
                     on_move=self._on_mouse_move,
                     on_click=self._on_mouse_click,
                 ) as ml:
                self._ready.set()
                while True:
                    _t.sleep(0.1)
                    if self._toggle_event.is_set():
                        self._toggle_event.clear()
                        self._programmatic_toggle()
                    if self._was_started and not self._collector.is_recording:
                        break
        except KeyboardInterrupt:
            print("\n\n[scc] Cancelado (Ctrl+C).", flush=True)
            return 1

        self._running = False

        total = self._collector._counter
        print(
            f"\n[scc] ✅ {total} captura(s) salvas em {self._collector._out_dir}/",
            flush=True,
        )
        return 0
