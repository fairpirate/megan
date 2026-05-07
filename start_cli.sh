#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true

if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "⚠️  Ollama not running — attempting to start..."
  ollama serve &>/dev/null &
  sleep 2
fi

python megan_cli.py
