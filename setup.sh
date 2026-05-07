#!/bin/bash
# MEGAN Setup Script — Ollama + Gemma3 edition
set -e
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   MEGAN Setup  (Ollama / Gemma3 — 100% Free)    ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Python check
if ! command -v python3 &>/dev/null; then
  echo "❌  Python 3 not found. Install from https://python.org"; exit 1
fi
PYTHON=$(command -v python3)
echo "✅  Python: $($PYTHON --version)"

# Virtualenv
if [ ! -d "venv" ]; then
  echo "▸   Creating virtual environment..."
  $PYTHON -m venv venv
fi
source venv/bin/activate
echo "✅  Virtual environment active"

# Dependencies
echo "▸   Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅  Dependencies installed"

# Directories
mkdir -p outputs modules memory web/static core
touch core/__init__.py

# Ollama check
echo ""
if command -v ollama &>/dev/null; then
  echo "✅  Ollama found: $(ollama --version 2>/dev/null || echo 'installed')"
  echo ""
  echo "▸   Checking if gemma3:4b is available..."
  if ollama list 2>/dev/null | grep -q "gemma3:4b"; then
    echo "✅  gemma3:4b already installed"
  else
    echo "▸   Pulling gemma3:4b (≈3GB, one-time download)..."
    ollama pull gemma3:4b
    echo "✅  gemma3:4b ready"
  fi
else
  echo "⚠️   Ollama not installed."
  echo ""
  echo "    Install it now:"
  echo "    → macOS/Linux : curl -fsSL https://ollama.com/install.sh | sh"
  echo "    → Windows     : https://ollama.com/download"
  echo ""
  echo "    Then run:"
  echo "    → ollama pull gemma3:4b"
  echo ""
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   MEGAN is ready!                               ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║   1. Start Ollama  :  ollama serve              ║"
echo "║   2. Web UI        :  bash start_web.sh         ║"
echo "║      → http://localhost:5000                    ║"
echo "║   3. CLI           :  bash start_cli.sh         ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
