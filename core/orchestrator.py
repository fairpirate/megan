"""
MEGAN Orchestrator
Detects action tags in AI responses and dispatches them.
"""

import re
from pathlib import Path
from core.modules_engine import (
    research_agent, format_research_report,
    generate_file, execute_code,
    build_module, list_modules, list_outputs
)


def detect_intent(response: str) -> list:
    actions = []

    # [RESEARCH: query]
    for m in re.finditer(r'\[RESEARCH:\s*(.+?)\]', response, re.IGNORECASE):
        actions.append({"type": "research", "query": m.group(1).strip()})

    # [SAVE_FILE: name.ext]content
    for m in re.finditer(r'\[SAVE_FILE:\s*(.+?)\](.*?)(?=\[SAVE_FILE:|$)', response, re.IGNORECASE | re.DOTALL):
        fname   = m.group(1).strip()
        content = m.group(2).strip()
        ext     = Path(fname).suffix.lstrip(".") or "md"
        actions.append({"type": "save_file", "filename": fname, "content": content, "format": ext})

    # [RUN_CODE]...[/RUN_CODE]
    for m in re.finditer(r'\[RUN_CODE\](.*?)\[/RUN_CODE\]', response, re.IGNORECASE | re.DOTALL):
        actions.append({"type": "run_code", "code": m.group(1).strip()})

    # [BUILD_MODULE: name|description]code[/BUILD_MODULE]
    for m in re.finditer(r'\[BUILD_MODULE:\s*(.+?)\|(.*?)\](.*?)\[/BUILD_MODULE\]', response, re.IGNORECASE | re.DOTALL):
        actions.append({
            "type": "build_module",
            "name": m.group(1).strip(),
            "description": m.group(2).strip(),
            "code": m.group(3).strip()
        })

    if "[LIST_MODULES]" in response.upper():
        actions.append({"type": "list_modules"})
    if "[LIST_OUTPUTS]" in response.upper():
        actions.append({"type": "list_outputs"})

    return actions


def execute_actions(actions: list, mem: dict) -> list:
    results = []
    for action in actions:
        t = action["type"]

        if t == "research":
            data   = research_agent(action["query"])
            report = format_research_report(action["query"], data["results"])
            saved  = generate_file(f"research_{action['query'][:30]}", report, "md")
            results.append({
                "action": "research",
                "query": action["query"],
                "result_count": len(data["results"]),
                "saved_to": saved.get("path", ""),
                "status": data["status"]
            })

        elif t == "save_file":
            res = generate_file(action["filename"], action["content"], action["format"])
            results.append({"action": "save_file", **res})

        elif t == "run_code":
            res = execute_code(action["code"])
            results.append({"action": "run_code", **res})

        elif t == "build_module":
            res = build_module(action["name"], action["description"], action["code"])
            if res["status"] == "ok":
                mem.setdefault("modules", [])
                if action["name"] not in mem["modules"]:
                    mem["modules"].append(action["name"])
            results.append({"action": "build_module", **res})

        elif t == "list_modules":
            results.append({"action": "list_modules", "modules": list_modules()})

        elif t == "list_outputs":
            results.append({"action": "list_outputs", "files": list_outputs()})

    return results


def format_action_results(results: list) -> str:
    if not results:
        return ""
    lines = ["\n⚙️  MEGAN Execution Report"]
    for r in results:
        a = r.get("action", "")
        if a == "research":
            lines.append(f"🔍  Research '{r['query']}' → {r['result_count']} results → {r['saved_to']}")
        elif a == "save_file":
            note = f" ({r['note']})" if r.get("note") else ""
            lines.append(f"💾  Saved: {r.get('filename','')} → {r.get('path','')}{note}")
        elif a == "run_code":
            ok = "✅" if r.get("status") == "ok" else "❌"
            out = r.get("stdout","")[:200]
            lines.append(f"{ok}  Code executed (rc={r.get('returncode')})" + (f": {out}" if out else ""))
            if r.get("stderr"):
                lines.append(f"    stderr: {r['stderr'][:200]}")
        elif a == "build_module":
            ok = "✅" if r.get("status") == "ok" else "❌"
            lines.append(f"{ok}  Module '{r.get('module','')}' → {r.get('path','')}")
        elif a == "list_modules":
            mods = r.get("modules", [])
            lines.append(f"📦  Modules: {', '.join(mods) if mods else 'none yet'}")
        elif a == "list_outputs":
            files = r.get("files", [])
            lines.append(f"📁  Outputs ({len(files)} files):")
            for f in files[:5]:
                lines.append(f"    • {f['name']} ({f['size']} bytes)")
    return "\n".join(lines)
