#!/usr/bin/env python3
"""
MEGAN Flask Server — Ollama backend, streaming support
"""

import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from pathlib import Path

from core.megan_core    import load_memory, save_memory, log_history, get_conversation_history, build_system_prompt
from core.ollama_client import call_ollama, stream_ollama, is_ollama_running, get_available_models, pick_model
from core.orchestrator  import detect_intent, execute_actions, format_action_results
from core.modules_engine import list_modules, list_outputs

app = Flask(__name__, static_folder="web/static")
CORS(app)

OUTPUTS_DIR = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


@app.route("/")
def index():
    return send_from_directory("web", "index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data         = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "No message"}), 400

    mem           = load_memory()
    system_prompt = build_system_prompt(mem)
    history       = get_conversation_history(mem, limit=14)

    response = call_ollama(system_prompt, history, user_message)

    actions        = detect_intent(response)
    action_results = execute_actions(actions, mem) if actions else []

    log_history(mem, "user",      user_message)
    log_history(mem, "assistant", response)

    return jsonify({
        "response": response,
        "actions":  action_results,
        "summary":  format_action_results(action_results)
    })


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    """Server-sent events streaming endpoint."""
    data         = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "No message"}), 400

    mem           = load_memory()
    system_prompt = build_system_prompt(mem)
    history       = get_conversation_history(mem, limit=14)

    def generate():
        tokens = []

        def on_token(t):
            tokens.append(t)
            yield f"data: {json.dumps({'token': t})}\n\n"

        # We can't yield from callback directly, so buffer then stream
        full_response = []

        def collect(t):
            full_response.append(t)
            pass

        # Non-streaming call, then send full response as chunks for simplicity
        resp = call_ollama(system_prompt, history, user_message)

        # Send in ~20 char chunks to simulate streaming
        for i in range(0, len(resp), 20):
            chunk = resp[i:i+20]
            yield f"data: {json.dumps({'token': chunk})}\n\n"

        # Execute actions
        actions = detect_intent(resp)
        action_results = execute_actions(actions, mem) if actions else []
        summary = format_action_results(action_results)

        log_history(mem, "user", user_message)
        log_history(mem, "assistant", resp)

        yield f"data: {json.dumps({'done': True, 'summary': summary, 'actions': action_results})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/status", methods=["GET"])
def status():
    running = is_ollama_running()
    models  = get_available_models() if running else []
    active  = pick_model() if running else "not available"
    mem     = load_memory()
    return jsonify({
        "ollama_running": running,
        "active_model":   active,
        "available_models": models,
        "modules":        list_modules(),
        "output_count":   len(list_outputs())
    })


@app.route("/api/models", methods=["GET"])
def models():
    return jsonify({"models": get_available_models(), "active": pick_model()})


@app.route("/api/modules", methods=["GET"])
def get_modules():
    return jsonify({"modules": list_modules()})


@app.route("/api/outputs", methods=["GET"])
def get_outputs():
    return jsonify({"files": list_outputs()})


@app.route("/api/outputs/<filename>")
def download_output(filename):
    return send_from_directory(str(OUTPUTS_DIR), filename)


@app.route("/api/memory", methods=["GET"])
def get_memory():
    mem = load_memory()
    return jsonify({
        "modules":       mem.get("modules", []),
        "workflows":     mem.get("workflows", []),
        "history_count": len(mem.get("history", []))
    })


@app.route("/api/clear", methods=["POST"])
def clear_history():
    mem = load_memory()
    mem["history"] = []
    save_memory(mem)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("MEGAN_PORT", 5001))
    print(f"\n🤖  MEGAN Web Server → http://localhost:{port}")
    running = is_ollama_running()
    if running:
        print(f"✅  Ollama running  →  model: {pick_model()}")
    else:
        print("⚠️  Ollama not running — start with: ollama serve")
    print()
    app.run(host="0.0.0.0", port=port, debug=False)
