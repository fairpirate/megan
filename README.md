# MEGAN — Autonomous AI Operating System
### Powered by Ollama + Gemma4 · 100% Free · Runs Fully Offline

---

## Why Ollama?

| | Anthropic API | MEGAN + Ollama |
|---|---|---|
| Cost | Pay per token | **FREE** |
| Internet | Required | **Not needed** |
| API Key | Required | **Not needed** |
| Privacy | Data sent to cloud | **100% local** |

---

## Prerequisites

| Tool | Install |
|------|---------|
| Python 3.9+ | https://python.org |
| Ollama | https://ollama.com |

---

## Setup (one time)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh   # Mac/Linux
# Windows: https://ollama.com/download

# 2. Pull Gemma4 (~3GB, one-time)
ollama pull gemma4:e4b

# 3. Clone / unzip MEGAN, then:
cd megan
bash setup.sh
```

---

## Run MEGAN

```bash
# Terminal 1 — start Ollama (if not already running)
ollama serve

# Terminal 2 — Web UI
bash start_web.sh
# → Open http://localhost:5001

# OR — CLI
bash start_cli.sh
```

---

## Other Free Models (drop-in replacements)

```bash
ollama pull llama3.2:3b      # Meta Llama 3.2 — very fast
ollama pull phi4-mini        # Microsoft Phi-4 — great for code
ollama pull mistral:7b       # Mistral 7B — strong reasoning
ollama pull gemma4:12b       # Gemma4 12B — more powerful (needs 8GB RAM)
```

MEGAN auto-selects the best available model. To force a specific one,
edit `DEFAULT_MODEL` in `core/ollama_client.py`.

---

## Project Structure

```
megan/
├── core/
│   ├── megan_core.py       # Memory, system prompt, history
│   ├── ollama_client.py    # Ollama API client (replaces Anthropic)
│   ├── modules_engine.py   # Research, file gen, code exec, builder
│   └── orchestrator.py     # Intent detection + action dispatch
├── modules/                # Auto-generated custom modules live here
├── memory/                 # Persistent JSON memory
├── outputs/                # All generated files
├── web/index.html          # Web UI
├── megan_cli.py            # CLI
├── server.py               # Flask server
├── setup.sh
├── start_web.sh
└── start_cli.sh
```

---

## MEGAN Action Tags

Embed these in conversation to trigger real actions:

| Tag | Effect |
|-----|--------|
| `[RESEARCH: topic]` | DuckDuckGo search → saves `.md` report |
| `[SAVE_FILE: name.ext]content` | Saves file to `outputs/` |
| `[RUN_CODE]...code...[/RUN_CODE]` | Executes Python |
| `[BUILD_MODULE: name\|desc]...code...[/BUILD_MODULE]` | Creates module |
| `[LIST_MODULES]` | Lists all modules |
| `[LIST_OUTPUTS]` | Lists output files |

---

## CLI Commands

| Command | Effect |
|---------|--------|
| `memory` | View memory state |
| `modules` | List custom modules |
| `outputs` | List generated files |
| `models` | Show Ollama models |
| `clear` | Clear history |
| `exit` | Quit |

---

## RAM Requirements

| Model | RAM needed |
|-------|-----------|
| gemma4:e4b | ~4 GB |
| llama3.2:3b | ~3 GB |
| phi4-mini | ~3 GB |
| mistral:7b | ~6 GB |
| gemma4:12b | ~10 GB |
