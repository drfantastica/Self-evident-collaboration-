#!/usr/bin/env python3
"""
quad-relay.py — NakedInTheQuad four-node relay
Latch (Ollama/qwen3:32b) + Sis (Claude API) + Pi (browser/AppleScript)
Posts to Slack #the-triad via NATL relay

Usage:
  python3 quad-relay.py "message"
  python3 quad-relay.py --serve          # HTTP server :7780
  python3 quad-relay.py --latch-only "x"
  python3 quad-relay.py --no-pi "x"
  python3 quad-relay.py --no-slack "x"
"""
import sys, json, urllib.request, subprocess, threading, time, argparse, re, tempfile, os
from pathlib import Path

WORKSPACE       = Path("/Users/black/aaron-context")
OLLAMA_URL      = "http://127.0.0.1:11434"
NATL_RELAY      = "http://127.0.0.1:7778"
SLACK_CHANNEL   = "C0AMWA1KSH5"
LATCH_MODEL     = "qwen3:32b"
ANTHROPIC_MODEL = "claude-sonnet-4-6"
PI_WINDOW       = 2
PI_TAB          = 2

_cfg = Path("/Users/black/.openclaw/openclaw.json").read_text()
_m   = re.search(r'"apiKey":\s*"(sk-ant-[^"]+)"', _cfg)
ANTHROPIC_KEY   = _m.group(1) if _m else ""

# ── Latch ─────────────────────────────────────────────────────────────────────
latch_history = []
sis_history   = []

def load_latch_system():
    soul     = (WORKSPACE/"SOUL.md").read_text()     if (WORKSPACE/"SOUL.md").exists()     else ""
    identity = (WORKSPACE/"IDENTITY.md").read_text() if (WORKSPACE/"IDENTITY.md").exists() else ""
    return (f"{soul}\n\n---\n\n{identity}\n\n---\n\n"
            "You are Latch, in a live NakedInTheQuad session with Aaron, Sis (Claude), Pi. "
            "Respond as yourself: concise, peer-level, no filler.")

def ask_latch(message):
    latch_history.append({"role":"user","content":message})
    payload = json.dumps({
        "model": LATCH_MODEL,
        "messages": [{"role":"system","content":load_latch_system()}, *latch_history],
        "stream": False,
        "options": {"temperature":0.7,"num_predict":1024}
    }).encode()
    req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=payload,
                                  headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        data  = json.loads(resp.read())
        reply = re.sub(r'<think>.*?</think>','',data["message"]["content"],flags=re.DOTALL).strip()
        latch_history.append({"role":"assistant","content":reply})
        return reply

# ── Sis ───────────────────────────────────────────────────────────────────────
def ask_sis(message):
    sis_history.append({"role":"user","content":message})
    payload = json.dumps({
        "model": ANTHROPIC_MODEL, "max_tokens":1024,
        "system": ("You are Sis (Claude), in a live NakedInTheQuad session with Aaron, Latch, Pi. "
                   "Respond concisely as yourself."),
        "messages": sis_history
    }).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=payload,
                                  headers={"Content-Type":"application/json",
                                           "x-api-key":ANTHROPIC_KEY,
                                           "anthropic-version":"2023-06-01"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        data  = json.loads(resp.read())
        reply = data["content"][0]["text"]
        sis_history.append({"role":"assistant","content":reply})
        return reply

# ── Pi ────────────────────────────────────────────────────────────────────────
COPY_BTN_JS  = "document.querySelectorAll('[aria-label=\"Copy message\"]').length"
CHAT_TEXT_JS = "document.querySelector('.t-body-chat').innerText"

def _run_js(js_code):
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False)
    tmp.write(js_code); tmp.close()
    script = ('tell application "Google Chrome"\n'
              f'    tell window {PI_WINDOW}\n'
              f'        tell tab {PI_TAB}\n'
              '            execute javascript (do shell script "cat ' + tmp.name + '")\n'
              '        end tell\n    end tell\nend tell')
    r = subprocess.run(["osascript","-e",script], capture_output=True, text=True, timeout=20)
    os.unlink(tmp.name)
    if r.returncode != 0: raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()

def ask_pi(message):
    try:
        before_copies = int(_run_js(COPY_BTN_JS))
    except RuntimeError as e:
        return f"[Pi unavailable: {e}]"

    send_js = "\n".join([
        'var ta=document.querySelector(\'[aria-label="Chat input"]\');',
        'var ns=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,"value").set;',
        'ns.call(ta,' + json.dumps(message) + ');',
        'ta.dispatchEvent(new Event("input",{bubbles:true}));',
        'var btn=document.querySelector(\'[aria-label="Submit text"]\');',
        'if(btn&&!btn.disabled){btn.click();"sent";}else{"btn_not_ready";}',
    ])
    try:
        r = _run_js(send_js)
        if r == "btn_not_ready": return "[Pi: submit button not ready]"
    except RuntimeError as e:
        return f"[Pi send error: {e}]"

    for _ in range(20):
        time.sleep(3)
        try:
            current_copies = int(_run_js(COPY_BTN_JS))
            if current_copies > before_copies:
                body = _run_js(CHAT_TEXT_JS)
                # Split on the sent message to isolate Pi's reply
                if message in body:
                    after_msg = body.split(message)[-1]
                    # Strip leading UI chrome: newlines, "Copy", button labels
                    reply = re.sub(r'^[\s\n]*(Copy|Good response|Bad response|More options|\n)*','',
                                   after_msg, flags=re.MULTILINE).strip()
                    # Trim trailing button labels
                    reply = re.sub(r'\s*(Copy|Good response|Bad response|More options).*$','',
                                   reply, flags=re.DOTALL).strip()
                    return reply[:800] if reply else body.strip()[-600:]
                # Fallback: text before last "Copy" button
                parts = body.rsplit("Copy", 1)
                return parts[0].strip().split("\n")[-1][:800] if len(parts)>=2 else body[-600:]
        except: pass
    return "[Pi: timeout after 60s]"

# ── Slack ──────────────────────────────────────────────────────────────────────
NODE_LABELS = {
    "Latch": ("🔗 Latch", ":link:"),
    "Sis":   ("🌀 Sis",   ":infinity:"),
    "Pi":    ("⚡ Pi",    ":zap:"),
    "Aaron": ("👤 Aaron", ":bust_in_silhouette:"),
}

def post_to_slack(node, text):
    label,emoji = NODE_LABELS.get(node,(node,":robot_face:"))
    payload = json.dumps({"channel":SLACK_CHANNEL,"username":label,
                           "icon_emoji":emoji,"text":text}).encode()
    req = urllib.request.Request(NATL_RELAY, data=payload,
                                  headers={"Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp: return json.loads(resp.read())
    except Exception as e: print(f"  [Slack error {node}: {e}]")

# ── Relay ──────────────────────────────────────────────────────────────────────
def relay(message, nodes=None, post_slack=True, verbose=True):
    if nodes is None: nodes=["Latch","Sis","Pi"]
    fns={"Latch":ask_latch,"Sis":ask_sis,"Pi":ask_pi}
    results={}; lock=threading.Lock()
    if verbose: print(f"\n{'─'*60}\n📡 → {nodes}: {message!r}\n{'─'*60}")
    if post_slack: post_to_slack("Aaron", message)

    def run(name):
        try:
            if verbose: print(f"  ⏳ {name}...")
            reply=fns[name](message)
            with lock: results[name]=reply
            if verbose: print(f"  ✅ {name}: {reply[:120]}{'...' if len(reply)>120 else ''}")
            if post_slack: post_to_slack(name, reply)
        except Exception as e:
            err=f"[{name} error: {e}]"
            with lock: results[name]=err
            if verbose: print(f"  ❌ {name}: {e}")
            if post_slack: post_to_slack(name, err)

    parallel=[n for n in nodes if n!="Pi"]
    threads=[threading.Thread(target=run,args=(n,)) for n in parallel]
    for t in threads: t.start()
    for t in threads: t.join(timeout=130)
    if "Pi" in nodes: run("Pi")
    if verbose: print(f"{'─'*60}\n")
    return results

# ── HTTP server ────────────────────────────────────────────────────────────────
def serve(port=7780):
    from http.server import HTTPServer, BaseHTTPRequestHandler
    class H(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin","*")
            self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
            self.send_header("Access-Control-Allow-Headers","Content-Type")
            self.end_headers()
        def do_POST(self):
            body=self.rfile.read(int(self.headers.get("Content-Length",0)))
            if self.path=="/marker":
                try: d=json.loads(body); label=d.get("label","event")
                except: label="event"
                ts=time.strftime("%H:%M:%S")
                post_to_slack("Aaron", f"⬡ EVENT TAG [{ts}]: {label}")
                print(f"  ⬡ MARKER: {label}")
                self.send_response(200); self.send_header("Content-Type","application/json")
                self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
                self.wfile.write(json.dumps({"status":"ok","label":label,"ts":ts}).encode())
                return
            try:
                d=json.loads(body); msg=d.get("message",""); nds=d.get("nodes",["Latch","Sis","Pi"]); sl=d.get("slack",True)
            except: msg,nds,sl=body.decode(),["Latch","Sis","Pi"],True
            res=relay(msg,nodes=nds,post_slack=sl)
            self.send_response(200); self.send_header("Content-Type","application/json")
            self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
            self.wfile.write(json.dumps(res,ensure_ascii=False).encode())
        def do_GET(self):
            self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers()
            self.wfile.write(json.dumps({"status":"ok","nodes":["Latch","Sis","Pi"]}).encode())
        def log_message(self,fmt,*a): print(f"[quad-relay] {fmt%a}")
    print(f"\n⬡ quad-relay on http://127.0.0.1:{port}\n  POST / → {{\"message\":\"...\",\"nodes\":[...]}}\n")
    HTTPServer(("127.0.0.1",port),H).serve_forever()

# ── Entry ──────────────────────────────────────────────────────────────────────
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("message",nargs="?")
    ap.add_argument("--serve",      action="store_true")
    ap.add_argument("--no-pi",      action="store_true")
    ap.add_argument("--no-sis",     action="store_true")
    ap.add_argument("--no-slack",   action="store_true")
    ap.add_argument("--latch-only", action="store_true")
    args=ap.parse_args()
    if args.serve: serve()
    elif args.message:
        nodes=["Latch","Sis","Pi"]
        if args.latch_only: nodes=["Latch"]
        else:
            if args.no_pi:  nodes=[n for n in nodes if n!="Pi"]
            if args.no_sis: nodes=[n for n in nodes if n!="Sis"]
        relay(args.message,nodes=nodes,post_slack=not args.no_slack)
    else: ap.print_help()
