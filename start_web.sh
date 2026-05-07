#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true

# Auto-start Ollama if not running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo "⚠️  Ollama not running — attempting to start..."
  ollama serve &>/dev/null &
  sleep 2
fi

echo ""
echo "🤖  MEGAN Web UI  →  http://localhost:5001"
echo "    Press Ctrl+C to stop"
echo ""
python server.py
