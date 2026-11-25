# screen-click-capture

Captura a tela a cada clique do mouse e salva PNGs sequenciais numa
pasta por sessão, com uma janelinha de status.

## Uso

```bash
# Instale (modo dev)
pip install -e ".[dev]"

# Inicie (F9 liga/desliga, GUI minimalista aparece)
scc

# Pasta de saída customizada
scc --out ./minhas-capturas

# Hotkey diferente
scc --hotkey f10

# Sem janela (só terminal)
scc --no-gui
```

Pressione **F9** para começar a gravar. A cada clique do mouse, o
programa captura a tela inteira do monitor que contém o cursor e salva
um PNG sequencial na pasta da sessão:

```
capturas/
└── 20261125_0913-01/
    ├── 01.png
    ├── 02.png
    ├── 03.png
    └── ...
```

Pressione **F9** de novo para parar. Cada execução do `scc` cria uma
pasta nova de sessão (`YYYYMMDD_HHMM-NN`), onde `NN` é o número da
sessão no dia (01, 02, 03, ...).

## GUI

Por padrão o `scc` abre uma janela pequena de status:

- **⏸ MONITORANDO** (cinza) — aguardando F9
- **● GRAVANDO** (vermelho pulsante) — capturando telas
- Pasta da sessão e contador de capturas

Para rodar sem a janela: `scc --no-gui`.

## Opções

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--out` | `./capturas` | Pasta base de saída |
| `--hotkey` | `f9` | Tecla que liga/desliga a gravação |
| `--no-gui` | off | Roda sem a janela de status (só terminal) |

## Requisitos

- Windows 10/11 (ou qualquer SO suportado pelo pynput + mss)
- Python ≥ 3.10
- tkinter (já vem com o Python no Windows)

## Estrutura

```
src/screen_click_capture/
├── capture.py    # captura de tela (mss) — multi-monitor
├── listener.py   # pynput — hotkey + cliques + callbacks
├── session.py    # pasta por sessão (YYYYMMDD_HHMM-NN)
├── gui.py        # GUI minimalista (tkinter)
└── cli.py        # entry point `scc`
```

