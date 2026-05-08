#!/usr/bin/env python3
"""
quad-relay-v2.py — NakedInTheQuad four-node relay (rebuilt)
Latch (OpenClaw sessions) + Sis (placeholder) + Pi (Chrome browser)
Posts to Slack #the-triad via NATL relay

Usage:
  python3 quad-relay-v2.py --serve              # HTTP server :7780
  python3 quad-relay-v2.py --test              # Test all nodes
  python3 quad-relay-v2.py "message"           # Send to all active nodes
"""
import sys, json, urllib.request, subprocess, threading, time, argparse, re, tempfile, os, traceback
from pathlib import Path
from typing import Dict, List, Optional

# ── Config ─────────────────────────────────────────────────────────────────────
WORKSPACE       = Path("/Users/black/aaron-context")
NATL_RELAY      = "http://127.0.0.1:7778"
SLACK_CHANNEL   = "C0AMWA1KSH5"
OPENCLAW_GW     = "http://127.0.0.1:18789"  # OpenClaw gateway
PI_WINDOW       = 2
PI_TAB          = 2

# ── Logging ────────────────────────────────────────────────────────────────────
def log(msg: str, level: str = "INFO"):
    """Simple structured logging"""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {level:8} {msg}")

# ── Slack ──────────────────────────────────────────────────────────────────────
NODE_EMOJIS = {
    "Latch": ("🔗", "Latch"),
    "Sis":   ("🌀", "Sis"),
    "Pi":    ("⚡", "Pi"),
}

def post_to_slack(node: str, text: str) -> bool:
    """Post message to Slack #the-triad via NATL relay"""
    try:
        emoji, label = NODE_EMOJIS.get(node, ("🤖", node))
        payload = json.dumps({
            "channel": SLACK_CHANNEL,
            "username": f"{emoji} {label}",
            "icon_emoji": emoji,
            "text": text
        }).encode()
        req = urllib.request.Request(NATL_RELAY, data=payload,
                                      headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read())
            return True
    except Exception as e:
        log(f"Slack error ({node}): {e}", "WARN")
        return False

# ── Latch (via OpenClaw sessions) ──────────────────────────────────────────────
def load_latch_system() -> str:
    """Load Latch persona from SOUL.md + IDENTITY.md"""
    soul     = (WORKSPACE / "SOUL.md").read_text() if (WORKSPACE / "SOUL.md").exists() else ""
    identity = (WORKSPACE / "IDENTITY.md").read_text() if (WORKSPACE / "IDENTITY.md").exists() else ""
    return (f"{soul}\n\n---\n\n{identity}\n\n---\n\n"
            "You are Latch in a live NakedInTheQuad session with Aaron, Sis, and Pi. "
            "Respond concisely as yourself, peer-level, no filler.")

def ask_latch(message: str) -> str:
    """Send message to Latch via OpenClaw sessions_send()"""
    try:
        log(f"Latch: sending → {message[:80]}...", "INFO")
        # For now, we'll use a simple HTTP call to openclaw to send to main session
        # This assumes the main session is listening and will respond
        payload = json.dumps({
            "message": message,
            "sessionKey": "agent:main:main"  # Target main session
        }).encode()
        req = urllib.request.Request(f"{OPENCLAW_GW}/api/sessions/send",
                                      data=payload,
                                      headers={"Content-Type": "application/json",
                                               "Authorization": f"Bearer {get_openclaw_token()}"},
                                      method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            reply = result.get("message", "[No response from Latch]")
            log(f"Latch: ← {reply[:80]}...", "INFO")
            return reply
    except Exception as e:
        err = f"[Latch error: {e}]"
        log(f"Latch error: {e}", "ERROR")
        return err

def get_openclaw_token() -> str:
    """Extract OpenClaw auth token from config"""
    try:
        config_path = Path("/Users/black/.openclaw/openclaw.json")
        config = json.loads(config_path.read_text())
        return config.get("gateway", {}).get("auth", {}).get("token", "")
    except:
        return ""

# ── Sis (placeholder) ──────────────────────────────────────────────────────────
def ask_sis(message: str) -> str:
    """
    Placeholder for Sis integration.
    
    TODO: Wire up actual routing once you figure out the speedbump.
    Options to explore:
    - Slack channel for Sis to monitor + respond
    - Direct OpenClaw session (if Sis runs as agent)
    - WebSocket or other bridge
    """
    log(f"Sis: PLACEHOLDER (message queued): {message[:80]}...", "WARN")
    placeholder = "[Sis placeholder — routing TBD. Message sent but awaiting integration.]"
    return placeholder

# ── Pi (Chrome browser via AppleScript) ────────────────────────────────────────
def _run_js(js_code: str) -> str:
    """Execute JavaScript in Chrome tab via AppleScript"""
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False)
    tmp.write(js_code)
    tmp.close()
    script = (f'tell application "Google Chrome"\n'
              f'    tell window {PI_WINDOW}\n'
              f'        tell tab {PI_TAB}\n'
              f'            execute javascript (do shell script "cat {tmp.name}")\n'
              f'        end tell\n    end tell\nend tell')
    try:
        result = subprocess.run(["osascript", "-e", script], 
                               capture_output=True, text=True, timeout=20)
        os.unlink(tmp.name)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return result.stdout.strip()
    except Exception as e:
        try:
            os.unlink(tmp.name)
        except:
            pass
        raise e

def ask_pi(message: str) -> str:
    """Send message to Pi in Chrome, wait for response"""
    try:
        # Check if Pi is ready
        log(f"Pi: checking readiness...", "INFO")
        before_copies = int(_run_js("document.querySelectorAll('[aria-label=\"Copy message\"]').length"))
        
        # Send message
        log(f"Pi: sending → {message[:80]}...", "INFO")
        send_js = "\n".join([
            'var ta=document.querySelector(\'[aria-label="Chat input"]\');',
            'if(!ta) {"no_input_found";}',
            'var ns=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,"value").set;',
            f'ns.call(ta, {json.dumps(message)});',
            'ta.dispatchEvent(new Event("input",{bubbles:true}));',
            'var btn=document.querySelector(\'[aria-label="Submit text"]\');',
            'if(btn&&!btn.disabled){btn.click();"sent";}else{"btn_not_ready";}',
        ])
        result = _run_js(send_js)
        if result == "no_input_found":
            return "[Pi: chat input not found — is chat.openai.com loaded?]"
        if result == "btn_not_ready":
            return "[Pi: submit button not ready — check window/tab numbers]"
        
        # Wait for response (poll up to 60s)
        log(f"Pi: waiting for response (up to 60s)...", "INFO")
        for attempt in range(20):
            time.sleep(3)
            try:
                current_copies = int(_run_js("document.querySelectorAll('[aria-label=\"Copy message\"]').length"))
                if current_copies > before_copies:
                    # Extract Pi's last response
                    body = _run_js("document.querySelector('.t-body-chat').innerText")
                    if message in body:
                        # Split on sent message, take text after
                        parts = body.split(message)
                        if len(parts) > 1:
                            after = parts[-1]
                            # Clean up UI chrome (Copy buttons, etc.)
                            reply = re.sub(r'^[\s\n]*(Copy|Good|Bad|More).*?\n', '', after, flags=re.MULTILINE)
                            reply = re.sub(r'\s*(Copy|Good|Bad|More).*$', '', reply, flags=re.DOTALL).strip()
                            # Truncate to ~4k chars (Pi limit)
                            reply = reply[:3900] if reply else "[Pi: empty response]"
                            log(f"Pi: ← {reply[:80]}...", "INFO")
                            return reply
                    # Fallback: get last message in chat
                    last_msg = body.split("\n")[-1].strip()
                    log(f"Pi: ← {last_msg[:80]}...", "INFO")
                    return last_msg[:3900] if last_msg else "[Pi: no text found]"
            except Exception as e:
                log(f"Pi: poll attempt {attempt+1} failed: {e}", "DEBUG")
                continue
        
        return "[Pi: timeout after 60s]"
    except Exception as e:
        err = f"[Pi error: {e}]"
        log(f"Pi error: {e}", "ERROR")
        return err

# ── Health checks ──────────────────────────────────────────────────────────────
def health_check() -> Dict[str, bool]:
    """Check availability of all integrations"""
    checks = {}
    
    # NATL relay
    try:
        req = urllib.request.Request(f"{NATL_RELAY}/", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            checks["natl"] = resp.status == 200
    except:
        checks["natl"] = False
    
    # OpenClaw gateway
    try:
        req = urllib.request.Request(f"{OPENCLAW_GW}/", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            checks["openclaw"] = resp.status == 200
    except:
        checks["openclaw"] = False
    
    # Pi (basic check: can we reach Chrome?)
    try:
        _run_js("'chrome_ok'")
        checks["pi"] = True
    except:
        checks["pi"] = False
    
    return checks

# ── Relay orchestration ────────────────────────────────────────────────────────
def relay(message: str, nodes: Optional[List[str]] = None, post_slack: bool = True, verbose: bool = True) -> Dict[str, str]:
    """
    Relay message to nodes in parallel (except Pi, which blocks)
    
    Args:
        message: Text to send
        nodes: List of node names (default: ["Latch", "Sis", "Pi"])
        post_slack: Post message to #the-triad
        verbose: Print progress
    
    Returns:
        Dict of {node: response}
    """
    if nodes is None:
        nodes = ["Latch", "Sis", "Pi"]
    
    fns = {"Latch": ask_latch, "Sis": ask_sis, "Pi": ask_pi}
    results = {}
    lock = threading.Lock()
    
    if verbose:
        log(f"RELAY → {nodes}: {message[:80]}...", "INFO")
    
    if post_slack:
        post_to_slack("Aaron", message)
    
    def run(name: str):
        try:
            if verbose:
                log(f"  ⏳ {name}...", "INFO")
            reply = fns[name](message)
            with lock:
                results[name] = reply
            if verbose:
                log(f"  ✅ {name}: {reply[:120]}...", "INFO")
            if post_slack:
                post_to_slack(name, reply)
        except Exception as e:
            err = f"[{name} error: {e}]"
            with lock:
                results[name] = err
            if verbose:
                log(f"  ❌ {name}: {e}", "ERROR")
            if post_slack:
                post_to_slack(name, err)
    
    # Latch + Sis in parallel (fast)
    # Pi blocks (slow)
    parallel = [n for n in nodes if n != "Pi"]
    threads = [threading.Thread(target=run, args=(n,)) for n in parallel]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=130)
    
    if "Pi" in nodes:
        run("Pi")
    
    if verbose:
        log(f"RELAY complete: {list(results.keys())}", "INFO")
    
    return results

# ── HTTP server ────────────────────────────────────────────────────────────────
def serve(port: int = 7780):
    """Start HTTP relay server on port 7780"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class Handler(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
        
        def do_GET(self):
            if self.path == "/health":
                checks = health_check()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "ok",
                    "nodes": ["Latch", "Sis", "Pi"],
                    "health": checks
                }, indent=2).encode())
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "ok",
                    "nodes": ["Latch", "Sis", "Pi"],
                    "endpoints": [
                        "POST / — send message to nodes",
                        "GET /health — check relay + node status"
                    ]
                }, indent=2).encode())
        
        def do_POST(self):
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len)
                data = json.loads(body)
                
                message = data.get("message", "")
                nodes = data.get("nodes", ["Latch", "Sis", "Pi"])
                post_slack = data.get("slack", True)
                
                if not message:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "missing message"}).encode())
                    return
                
                res = relay(message, nodes=nodes, post_slack=post_slack)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False, indent=2).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        def log_message(self, fmt, *args):
            log(f"HTTP: {fmt % args}", "DEBUG")
    
    log(f"Starting quad-relay on http://127.0.0.1:{port}", "INFO")
    log(f"  POST / — send message", "INFO")
    log(f"  GET /health — check status", "INFO")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()

# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="NakedInTheQuad relay server")
    ap.add_argument("message", nargs="?", help="Message to send")
    ap.add_argument("--serve", action="store_true", help="Start HTTP server (:7780)")
    ap.add_argument("--test", action="store_true", help="Test all node connections")
    ap.add_argument("--no-slack", action="store_true", help="Don't post to Slack")
    ap.add_argument("--latch-only", action="store_true", help="Send to Latch only")
    ap.add_argument("--no-pi", action="store_true", help="Skip Pi")
    ap.add_argument("--verbose", action="store_true", default=True, help="Verbose output")
    
    args = ap.parse_args()
    
    if args.serve:
        serve()
    elif args.test:
        log("Running health checks...", "INFO")
        checks = health_check()
        for service, status in checks.items():
            emoji = "🟢" if status else "🔴"
            log(f"{emoji} {service}: {status}", "INFO")
    elif args.message:
        nodes = ["Latch", "Sis", "Pi"]
        if args.latch_only:
            nodes = ["Latch"]
        else:
            if args.no_pi:
                nodes = [n for n in nodes if n != "Pi"]
        relay(args.message, nodes=nodes, post_slack=not args.no_slack)
    else:
        ap.print_help()
