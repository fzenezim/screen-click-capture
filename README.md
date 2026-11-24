# screen-click-capture

Captura a tela a cada clique do mouse e salva PNGs sequenciais.

## Uso

```bash
# Instale (modo dev)
pip install -e ".[dev]"

# Inicie a gravação (F9 liga/desliga)
scc
# Ou com pasta de saída customizada:
scc --out ./minhas-capturas
# Ou com hotkey diferente:
scc --hotkey f10
```

Pressione **F9** para começar a gravar. A cada clique do mouse, o programa
captura a tela inteira do monitor que contém o cursor e salva um PNG
sequencial na pasta de saída:

```
capturas/
├── 01.png
├── 02.png
├── 03.png
└── ...
```

Pressione **F9** de novo para parar.

## Opções

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--out` | `./capturas` | Pasta de saída dos PNGs |
| `--hotkey` | `f9` | Tecla que liga/desliga a gravação |

## Requisitos

- Windows 10/11 (ou qualquer SO suportado pelo pynput + mss)
- Python ≥ 3.10
