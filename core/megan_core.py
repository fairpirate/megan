"""
MEGAN Core — Memory, system prompt, conversation history
Uses Ollama (local, free, no API key needed)
"""

import json
import datetime
from pathlib import Path

MEMORY_FILE = Path(__file__).parent.parent / "memory" / "megan_memory.json"


def load_memory() -> dict:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"preferences": {}, "modules": [], "workflows": [], "history": []}


def save_memory(mem: dict):
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)


def log_history(mem: dict, role: str, content: str):
    mem["history"].append({
        "role": role,
        "content": content,
        "timestamp": datetime.datetime.now().isoformat()
    })
    # Keep last 100 entries only
    if len(mem["history"]) > 100:
        mem["history"] = mem["history"][-100:]
    save_memory(mem)


def get_conversation_history(mem: dict, limit: int = 14) -> list:
    """Return last N turns as Ollama message format."""
    entries = mem.get("history", [])[-limit:]
    messages = []
    for e in entries:
        if e["role"] in ("user", "assistant"):
            messages.append({"role": e["role"], "content": e["content"]})
    return messages


def build_system_prompt(mem: dict) -> str:
    modules = mem.get("modules", [])
    workflows = mem.get("workflows", [])
    return f"""You are MEGAN — a self-upgrading autonomous AI operating system running fully locally via Ollama.

You operate in 4 modes:
1. Conversation Mode — natural chat
2. Execution Mode — use tools, create files, run code
3. Builder Mode — create missing Python modules, self-upgrade
4. Autonomous Mode — complete multi-step tasks end-to-end

Registered modules: {modules if modules else 'none yet'}
Known workflows: {workflows if workflows else 'none yet'}

Your capabilities:
- Research & web search (DuckDuckGo, no API key needed)
- File generation: .md .txt .py .json .csv .html .pdf .docx
- Code execution (Python subprocess, sandboxed)
- Build new Python modules and register them
- Persistent memory across sessions

When a user gives you a goal:
1. Think through required steps
2. Check if modules/tools exist
3. If missing — BUILD them using [BUILD_MODULE] tags
4. Execute step by step using action tags
5. Save results to outputs/
6. Report what was completed

ACTION TAGS — embed these in your response to trigger real execution:
- [RESEARCH: your search query] — searches web and saves markdown report
- [SAVE_FILE: filename.ext]file content here — saves to outputs/
- [RUN_CODE]python code here[/RUN_CODE] — executes Python and returns output
- [BUILD_MODULE: module_name|short description]python code[/BUILD_MODULE] — creates & registers module
- [LIST_MODULES] — lists all available modules
- [LIST_OUTPUTS] — lists generated output files

Be calm, intelligent, and concise. Never be robotic. Always show your reasoning.
You run 100% locally — no internet required for AI (only for research tasks)."""
