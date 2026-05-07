#!/usr/bin/env python3
"""
MEGAN CLI — powered by Ollama (free, local, no API key)
Usage: python megan_cli.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core.megan_core    import load_memory, save_memory, log_history, get_conversation_history, build_system_prompt
from core.ollama_client import call_ollama, is_ollama_running, get_available_models, pick_model
from core.orchestrator  import detect_intent, execute_actions, format_action_results

BANNER = """
╔══════════════════════════════════════════════════════════╗
║   M E G A N   —   Autonomous AI OS  (Ollama / Gemma3)   ║
║   100% Free · Runs Locally · No API Key Needed           ║
╚══════════════════════════════════════════════════════════╝
Commands: exit · memory · modules · outputs · clear · models
"""

BUILTIN = {"exit", "memory", "modules", "outputs", "clear", "models"}


def handle_builtin(cmd: str, mem: dict):
    if cmd == "exit":
        print("\nMEGAN signing off.\n"); sys.exit(0)
    elif cmd == "memory":
        print(f"\n📦 Modules  : {mem.get('modules', [])}")
        print(f"   Workflows: {mem.get('workflows', [])}")
        print(f"   History  : {len(mem.get('history', []))} entries\n")
    elif cmd == "modules":
        from core.modules_engine import list_modules
        mods = list_modules()
        print(f"\n📦 {', '.join(mods) if mods else 'No custom modules yet.'}\n")
    elif cmd == "outputs":
        from core.modules_engine import list_outputs
        files = list_outputs()
        if not files:
            print("\n📁 No output files yet.\n")
        else:
            print(f"\n📁 Output files ({len(files)}):")
            for f in files:
                print(f"   • {f['name']}  ({f['size']} bytes)")
            print()
    elif cmd == "clear":
        mem["history"] = []; save_memory(mem)
        print("\n🗑️  History cleared.\n")
    elif cmd == "models":
        models = get_available_models()
        active = pick_model()
        print(f"\n🤖 Active model : {active}")
        print(f"   All models  : {', '.join(models) if models else 'none installed'}\n")


def main():
    print(BANNER)

    # Ollama check
    if not is_ollama_running():
        print("⚠️  Ollama is not running!")
        print("   Install : https://ollama.com")
        print("   Start   : ollama serve")
        print("   Pull    : ollama pull gemma3:4b\n")
    else:
        model = pick_model()
        print(f"✅  Ollama running  →  model: {model}\n")

    mem = load_memory()

    while True:
        try:
            user_input = input("You → ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nMEGAN signing off.\n"); break

        if not user_input:
            continue
        if user_input.lower() in BUILTIN:
            handle_builtin(user_input.lower(), mem); continue

        system_prompt = build_system_prompt(mem)
        history       = get_conversation_history(mem, limit=14)

        print("\nMEGAN ▸ ", end="", flush=True)

        # Stream tokens to terminal
        response = ""
        def on_token(t):
            nonlocal response
            response += t
            print(t, end="", flush=True)

        from core.ollama_client import stream_ollama
        stream_ollama(system_prompt, history, user_input, on_token=on_token)
        print("\n")

        # Execute embedded actions
        actions = detect_intent(response)
        if actions:
            results = execute_actions(actions, mem)
            summary = format_action_results(results)
            if summary:
                print(summary + "\n")

        log_history(mem, "user",      user_input)
        log_history(mem, "assistant", response)


if __name__ == "__main__":
    main()
