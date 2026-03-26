#!/usr/bin/env python3
"""
HA Diagnostic - Serveur web avec interface dans la barre latérale HA.
"""

import os
import threading
import time
from datetime import datetime
from flask import Flask, redirect
from diagnostic.addon_checker import AddonChecker
from diagnostic.log_parser import LogParser
from diagnostic.supervisor_api import SupervisorAPI

app = Flask(__name__)

# État global du diagnostic
state = {
    "status": "pending",   # pending | running | done | error
    "report": None,
    "error": None,
    "last_run": None,
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HA Diagnostic</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f0f2f5;
      color: #1a1a2e;
    }}
    header {{
      background: #03a9f4;
      color: white;
      padding: 16px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    header h1 {{ font-size: 1.3rem; font-weight: 600; }}
    header small {{ font-size: 0.75rem; opacity: 0.85; }}
    .btn {{
      background: white;
      color: #03a9f4;
      border: none;
      padding: 8px 18px;
      border-radius: 20px;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      font-size: 0.9rem;
    }}
    .btn:hover {{ background: #e3f2fd; }}
    .container {{ max-width: 960px; margin: 24px auto; padding: 0 16px; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }}
    .card {{
      background: white;
      border-radius: 12px;
      padding: 20px;
      text-align: center;
      box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }}
    .card .num {{ font-size: 2.2rem; font-weight: 700; margin-bottom: 4px; }}
    .card .label {{ font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }}
    .card.total .num {{ color: #03a9f4; }}
    .card.ok .num {{ color: #4caf50; }}
    .card.warn .num {{ color: #ff9800; }}
    .card.err .num {{ color: #f44336; }}
    .section {{ margin-bottom: 24px; }}
    .section h2 {{
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 12px;
      padding-left: 4px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .addon-item {{
      background: white;
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 10px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
      border-left: 4px solid #ccc;
    }}
    .addon-item.warn {{ border-left-color: #ff9800; }}
    .addon-item.err {{ border-left-color: #f44336; }}
    .addon-item .addon-name {{ font-weight: 600; margin-bottom: 4px; }}
    .addon-item .addon-meta {{ font-size: 0.8rem; color: #888; margin-bottom: 8px; }}
    .addon-item .log-errors {{ margin-top: 10px; }}
    .addon-item .log-errors h4 {{
      font-size: 0.78rem;
      text-transform: uppercase;
      color: #999;
      margin-bottom: 6px;
    }}
    .log-line {{
      background: #fff8f8;
      border: 1px solid #ffcdd2;
      border-radius: 6px;
      padding: 6px 10px;
      font-size: 0.78rem;
      font-family: monospace;
      color: #c62828;
      margin-bottom: 4px;
      word-break: break-all;
    }}
    .all-ok {{
      background: white;
      border-radius: 12px;
      padding: 32px;
      text-align: center;
      box-shadow: 0 1px 4px rgba(0,0,0,0.1);
      color: #4caf50;
    }}
    .all-ok .icon {{ font-size: 3rem; margin-bottom: 12px; }}
    .all-ok p {{ color: #555; margin-top: 8px; }}
    .loading {{
      text-align: center;
      padding: 60px 20px;
      color: #666;
    }}
    .spinner {{
      border: 4px solid #f3f3f3;
      border-top: 4px solid #03a9f4;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      animation: spin 1s linear infinite;
      margin: 0 auto 16px;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .error-box {{
      background: #ffebee;
      border: 1px solid #ffcdd2;
      border-radius: 10px;
      padding: 20px;
      color: #c62828;
      text-align: center;
    }}
  </style>
  {auto_refresh}
</head>
<body>
  <header>
    <div>
      <h1>🩺 HA Diagnostic</h1>
      {last_run}
    </div>
    <a href="/refresh" class="btn">↻ Relancer</a>
  </header>
  <div class="container">
    {content}
  </div>
</body>
</html>"""


def build_content(s):
    if s["status"] in ("pending", "running"):
        return (
            '<div class="loading">'
            '<div class="spinner"></div>'
            '<p>Diagnostic en cours...</p>'
            '</div>',
            '<meta http-equiv="refresh" content="3">',
            "",
        )

    if s["status"] == "error":
        return (
            f'<div class="error-box"><strong>Erreur :</strong> {s["error"]}</div>',
            "",
            "",
        )

    r = s["report"]
    total = r["total"]
    healthy = len(r["healthy"])
    stopped = len(r["stopped"])
    errors = len(r["errors"])

    cards = f"""
    <div class="cards">
      <div class="card total"><div class="num">{total}</div><div class="label">Total</div></div>
      <div class="card ok"><div class="num">{healthy}</div><div class="label">OK</div></div>
      <div class="card warn"><div class="num">{stopped}</div><div class="label">Arrêtés</div></div>
      <div class="card err"><div class="num">{errors}</div><div class="label">En erreur</div></div>
    </div>
    """

    if not r["stopped"] and not r["errors"]:
        body = cards + """
        <div class="all-ok">
          <div class="icon">✅</div>
          <strong>Tous les add-ons fonctionnent correctement.</strong>
          <p>Aucune erreur détectée.</p>
        </div>"""
        return body, "", s["last_run"]

    sections = cards

    if r["stopped"]:
        items = ""
        for a in r["stopped"]:
            logs_html = ""
            if a.get("log_errors"):
                lines = "".join(f'<div class="log-line">{l}</div>' for l in a["log_errors"])
                logs_html = f'<div class="log-errors"><h4>Erreurs dans les logs</h4>{lines}</div>'
            items += f"""
            <div class="addon-item warn">
              <div class="addon-name">⚠ {a['name']}</div>
              <div class="addon-meta">{a['slug']} — v{a['version']} — état : {a['state']}</div>
              {logs_html}
            </div>"""
        sections += f'<div class="section"><h2>⚠ Add-ons arrêtés ({stopped})</h2>{items}</div>'

    if r["errors"]:
        items = ""
        for a in r["errors"]:
            logs_html = ""
            if a.get("log_errors"):
                lines = "".join(f'<div class="log-line">{l}</div>' for l in a["log_errors"])
                logs_html = f'<div class="log-errors"><h4>Erreurs dans les logs</h4>{lines}</div>'
            items += f"""
            <div class="addon-item err">
              <div class="addon-name">✗ {a['name']}</div>
              <div class="addon-meta">{a['slug']} — v{a['version']} — état : {a['state']}</div>
              {logs_html}
            </div>"""
        sections += f'<div class="section"><h2>✗ Add-ons en erreur ({errors})</h2>{items}</div>'

    return sections, "", s["last_run"]


def run_diagnostic():
    state["status"] = "running"
    state["error"] = None
    try:
        api = SupervisorAPI()
        if not api.is_connected():
            state["status"] = "error"
            state["error"] = "Impossible de se connecter à l'API Supervisor."
            return

        checker = AddonChecker(api)
        parser = LogParser()
        addons = checker.get_all_addons()
        report = checker.check_addons(addons)

        for addon in report["stopped"] + report["errors"]:
            logs = api.get_addon_logs(addon["slug"])
            addon["log_errors"] = parser.extract_errors(logs)[-5:]

        state["report"] = report
        state["last_run"] = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
        state["status"] = "done"
    except Exception as e:
        state["status"] = "error"
        state["error"] = str(e)


@app.route("/")
def index():
    content, auto_refresh, last_run = build_content(state)
    last_run_html = f"<small>Dernier diagnostic : {last_run}</small>" if last_run else ""
    auto_refresh_html = auto_refresh
    return HTML_TEMPLATE.format(
        content=content,
        auto_refresh=auto_refresh_html,
        last_run=last_run_html,
    )


@app.route("/refresh")
def refresh():
    if state["status"] != "running":
        threading.Thread(target=run_diagnostic, daemon=True).start()
    return redirect("/")


if __name__ == "__main__":
    # Lancer le diagnostic au démarrage
    threading.Thread(target=run_diagnostic, daemon=True).start()

    port = int(os.environ.get("INGRESS_PORT", 8099))
    app.run(host="0.0.0.0", port=port)
