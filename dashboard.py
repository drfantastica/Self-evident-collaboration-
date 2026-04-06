#!/usr/bin/env python3
"""
aaron-dashboard — Mission Control
Reads /Users/black/aaron-context/ and renders a live HTML briefing.
Usage: python3 /Users/black/aaron-context/dashboard.py
"""

import os, re, subprocess, tempfile
from datetime import datetime

BASE = "/Users/black/aaron-context"

def read(fname):
    try:
        with open(os.path.join(BASE, fname)) as f:
            return f.read()
    except:
        return ""

def section(content, header):
    """Extract content under a ## header"""
    pattern = rf"## {re.escape(header)}\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, content, re.DOTALL)
    return m.group(1).strip() if m else ""

def bullets(text):
    """Parse bullet lines into list"""
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("- ") or line.startswith("* "):
            lines.append(line[2:].strip())
        elif line.startswith("✅") or line.startswith("•"):
            lines.append(line)
    return lines

def table_rows(text):
    """Parse markdown table rows"""
    rows = []
    for line in text.split("\n"):
        if "|" in line and "---" not in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0]:
                rows.append(cells)
    return rows[1:] if len(rows) > 1 else rows  # skip header

# ── Parse files ──
active   = read("ACTIVE_STATE.md")
jwh      = read("JWH_STATE.md")
eeg      = read("EEG_BASELINE.md")
music    = read("MUSIC_STATE.md")
fw       = read("FRAMEWORK_CORE.md")
log      = read("SESSION_LOG.md")

# Active state
last_updated = ""
m = re.search(r"\*Last updated: (.+?)\*", active)
if m: last_updated = m.group(1)

open_threads_raw = section(active, "Open Threads")
open_threads = bullets(open_threads_raw)

# Project statuses
projects_raw = section(active, "Current Project Status")

# JWH
positions_raw = section(jwh, "Active Positions")
positions = table_rows(positions_raw)
jwh_signals_raw = section(jwh, "Signal Hierarchy")
jwh_signals = bullets(jwh_signals_raw)
open_signals_raw = section(jwh, "Open Signals")
open_signals = bullets(open_signals_raw)

# EEG
eeg_hardware = section(eeg, "Hardware")
eeg_channels = section(eeg, "Personal Channel Mapping")
eeg_protocol = section(eeg, "Personal Calibration Protocol")
eeg_notes_raw = section(eeg, "Session Notes")
eeg_notes = [l.strip() for l in eeg_notes_raw.split("\n") if l.strip() and not l.strip().startswith("*")]

# Music
music_source_raw = section(music, "Source Material")
music_arch_raw = section(music, "Architecture")

# Framework lenses
lenses_raw = section(fw, "Lens Palette (active lenses)")
lenses = []
for line in lenses_raw.split("\n"):
    m2 = re.match(r"- \*\*(.+?)\*\*[:\s]*(.*)", line.strip())
    if m2:
        lenses.append((m2.group(1), m2.group(2)[:80]))

# Session log - last entry
log_entries = re.split(r"\n---\n", log.strip())
last_session = log_entries[-1].strip() if log_entries else ""

now = datetime.now().strftime("%A, %B %d, %Y  %H:%M")

# ── Build HTML ──
def li(items, cls=""):
    return "".join(f'<li class="{cls}">{i}</li>' for i in items if i)

def thread_li(items):
    out = []
    for i in items:
        done = "✅" in i
        cls = "done" if done else "open"
        text = i.replace("✅", "").strip()
        marker = "✓" if done else "◆"
        out.append(f'<li class="thread {cls}"><span class="marker">{marker}</span>{text}</li>')
    return "".join(out)

def lens_cards(lenses):
    colors = ["#4ECDC4","#FFE66D","#FF6B9D","#A8E6CF","#C3B1E1","#F7C59F","#88D8B0"]
    out = []
    for i, (name, desc) in enumerate(lenses):
        c = colors[i % len(colors)]
        out.append(f'''<div class="lens-card" style="--accent:{c}">
            <div class="lens-name">{name}</div>
            <div class="lens-desc">{desc}</div>
        </div>''')
    return "".join(out)

def position_rows(positions):
    if not positions: return "<tr><td colspan='5' style='opacity:0.4;text-align:center'>No active positions logged</td></tr>"
    out = []
    for row in positions:
        while len(row) < 5: row.append("")
        out.append(f"<tr><td class='asset'>{row[0]}</td><td>{row[1][:50]}</td><td class='tier'>{row[2]}</td><td class='status'>{row[3]}</td><td class='notes'>{row[4][:60]}</td></tr>")
    return "".join(out)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AARON — Mission Control</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Cormorant+Garamond:ital,wght@0,300;0,600;1,300&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:        #080810;
  --bg2:       #0E0E1A;
  --bg3:       #14141F;
  --border:    rgba(255,255,255,0.06);
  --border2:   rgba(255,255,255,0.12);
  --text:      #E8E8F0;
  --muted:     rgba(232,232,240,0.45);
  --teal:      #4ECDC4;
  --gold:      #FFE66D;
  --coral:     #FF6B9D;
  --green:     #88D8B0;
  --mono:      'Space Mono', monospace;
  --serif:     'Cormorant Garamond', serif;
}}

* {{ box-sizing:border-box; margin:0; padding:0; }}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--mono);
  font-size: 12px;
  line-height: 1.6;
  min-height: 100vh;
  overflow-x: hidden;
}}

/* grain overlay */
body::before {{
  content:'';
  position:fixed; inset:0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events:none; z-index:0; opacity:0.4;
}}

.grid {{
  position:relative; z-index:1;
  display:grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: auto;
  gap: 1px;
  background: var(--border);
  min-height: 100vh;
}}

/* ── HEADER ── */
.header {{
  grid-column: 1 / -1;
  background: var(--bg2);
  padding: 28px 36px 20px;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  border-bottom: 1px solid var(--border2);
}}

.header-title {{
  font-family: var(--serif);
  font-size: 42px;
  font-weight: 300;
  letter-spacing: 0.08em;
  color: #fff;
}}

.header-title span {{
  font-style: italic;
  color: var(--teal);
}}

.header-meta {{
  text-align: right;
  color: var(--muted);
  font-size: 10px;
  line-height: 1.8;
}}

.pulse {{
  display: inline-block;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--green);
  margin-right: 6px;
  animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{
  0%,100% {{ opacity:1; transform:scale(1); }}
  50% {{ opacity:0.3; transform:scale(0.6); }}
}}

/* ── PANELS ── */
.panel {{
  background: var(--bg2);
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  animation: fadeUp 0.6s ease both;
}}

.panel:nth-child(2) {{ animation-delay: 0.05s; }}
.panel:nth-child(3) {{ animation-delay: 0.10s; }}
.panel:nth-child(4) {{ animation-delay: 0.15s; }}
.panel:nth-child(5) {{ animation-delay: 0.20s; }}
.panel:nth-child(6) {{ animation-delay: 0.25s; }}
.panel:nth-child(7) {{ animation-delay: 0.30s; }}
.panel:nth-child(8) {{ animation-delay: 0.35s; }}

@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(8px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}

.panel.span2 {{ grid-column: span 2; }}
.panel.span3 {{ grid-column: span 3; }}
.panel.tall  {{ grid-row: span 2; }}

.panel-label {{
  font-size: 9px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 8px;
}}

.panel-label::after {{
  content:'';
  flex:1;
  height:1px;
  background: var(--border2);
}}

.panel-label .tag {{
  background: var(--border2);
  border-radius: 2px;
  padding: 1px 6px;
  font-size: 8px;
}}

/* ── THREADS ── */
ul.threads {{ list-style:none; display:flex; flex-direction:column; gap:5px; }}
ul.threads li.thread {{
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 3px;
  font-size: 11px;
  line-height: 1.4;
  border-left: 2px solid transparent;
  transition: background 0.2s;
}}
ul.threads li.thread:hover {{ background: var(--bg3); }}
li.thread.open {{ border-left-color: var(--teal); }}
li.thread.done {{ border-left-color: var(--green); color: var(--muted); }}
li.thread .marker {{
  font-size: 8px;
  margin-top: 3px;
  flex-shrink: 0;
}}
li.thread.open .marker {{ color: var(--teal); }}
li.thread.done .marker {{ color: var(--green); }}

/* ── JWH SIGNALS ── */
.signal-stack {{ display:flex; flex-direction:column; gap:6px; }}
.signal-row {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: var(--bg3);
  border-radius: 3px;
}}
.signal-badge {{
  font-size: 8px;
  letter-spacing: 0.15em;
  padding: 2px 6px;
  border-radius: 2px;
  flex-shrink: 0;
  font-weight: 700;
}}
.signal-badge.primary   {{ background: rgba(78,205,196,0.15); color:var(--teal); border:1px solid rgba(78,205,196,0.3); }}
.signal-badge.secondary {{ background: rgba(255,230,109,0.12); color:var(--gold); border:1px solid rgba(255,230,109,0.3); }}
.signal-badge.tertiary  {{ background: rgba(232,232,240,0.08); color:var(--muted); border:1px solid var(--border2); }}
.signal-text {{ font-size:11px; color:var(--muted); line-height:1.3; }}

/* ── POSITION TABLE ── */
table.positions {{
  width:100%;
  border-collapse: collapse;
  font-size: 10.5px;
}}
table.positions th {{
  text-align:left;
  color: var(--muted);
  font-size: 8.5px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 6px 8px;
  border-bottom: 1px solid var(--border2);
  font-weight: 400;
}}
table.positions td {{
  padding: 8px 8px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
  line-height: 1.4;
}}
table.positions tr:hover td {{ background: var(--bg3); }}
td.asset {{ color: var(--gold); font-weight:700; font-size:13px; }}
td.tier  {{ color: var(--teal); }}
td.status {{ color: var(--green); }}
td.notes {{ color: var(--muted); font-size:10px; }}

/* ── LENS CARDS ── */
.lens-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}}
.lens-card {{
  background: var(--bg3);
  border-left: 2px solid var(--accent);
  padding: 10px 12px;
  border-radius: 0 3px 3px 0;
  transition: background 0.2s;
}}
.lens-card:hover {{ background: #1A1A28; }}
.lens-name {{
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--accent);
  margin-bottom: 3px;
}}
.lens-desc {{
  font-size: 9.5px;
  color: var(--muted);
  line-height: 1.4;
}}

/* ── EEG CHANNELS ── */
.channel-map {{
  display:flex; gap:10px;
}}
.channel {{
  flex:1;
  background: var(--bg3);
  padding:12px;
  border-radius:3px;
  text-align:center;
  border-top: 2px solid;
}}
.channel.left  {{ border-color: var(--teal); }}
.channel.right {{ border-color: var(--coral); }}
.ch-id {{ font-size:22px; font-weight:700; font-family:var(--serif); margin-bottom:4px; }}
.channel.left  .ch-id {{ color:var(--teal); }}
.channel.right .ch-id {{ color:var(--coral); }}
.ch-label {{ font-size:9px; color:var(--muted); letter-spacing:0.1em; text-transform:uppercase; }}

.protocol-bars {{ display:flex; flex-direction:column; gap:6px; }}
.protocol-bar {{
  display:flex; align-items:center; gap:10px;
  font-size: 10px;
}}
.bar-label {{ color:var(--muted); width:80px; flex-shrink:0; font-size:9px; }}
.bar-track {{
  flex:1; height:4px;
  background: var(--border2);
  border-radius:2px;
  overflow:hidden;
}}
.bar-fill {{
  height:100%;
  border-radius:2px;
  background: var(--teal);
  transition: width 0.8s ease;
}}
.bar-val {{ width:30px; text-align:right; color:var(--muted); font-size:9px; }}

/* ── MUSIC ── */
.music-block {{
  font-family: var(--serif);
  font-size:14px;
  font-weight:300;
  line-height:1.7;
  color: rgba(232,232,240,0.7);
}}
.music-block strong {{
  color:#fff;
  font-weight:600;
  font-style:italic;
}}
.music-act {{
  display:flex; align-items:center; gap:12px;
  padding:8px 0;
  border-bottom: 1px solid var(--border);
}}
.act-num {{
  font-family:var(--mono);
  font-size:9px;
  color:var(--coral);
  flex-shrink:0;
  letter-spacing:0.1em;
}}
.act-desc {{ font-size:11px; color:var(--muted); }}

/* ── SESSION LOG ── */
.log-entry {{
  font-size: 10.5px;
  line-height: 1.6;
  color: var(--muted);
  white-space: pre-wrap;
  background: var(--bg3);
  padding: 12px 14px;
  border-radius: 3px;
  border-left: 2px solid var(--border2);
  max-height: 180px;
  overflow-y: auto;
}}

/* ── STAT PILLS ── */
.stats {{ display:flex; gap:8px; flex-wrap:wrap; }}
.stat {{
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 10px;
  display:flex; align-items:center; gap:6px;
}}
.stat-val {{ color:#fff; font-weight:700; }}
.stat-key {{ color:var(--muted); }}

/* scrollbar */
::-webkit-scrollbar {{ width:4px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:var(--border2); border-radius:2px; }}

</style>
</head>
<body>
<div class="grid">

  <!-- HEADER -->
  <div class="header">
    <div>
      <div class="header-title">AARON <span>/ Mission Control</span></div>
      <div style="font-size:10px;color:var(--muted);margin-top:4px;letter-spacing:0.1em">
        ALL THAT EXISTS IS INFORMATION. MAY THE BEST IDEA WIN.
      </div>
    </div>
    <div class="header-meta">
      <div><span class="pulse"></span>LIVE — {now}</div>
      <div style="margin-top:4px">Last context update: {last_updated or "today"}</div>
      <div style="margin-top:4px">/Users/black/aaron-context/ → Google Drive synced</div>
    </div>
  </div>

  <!-- OPEN THREADS -->
  <div class="panel tall">
    <div class="panel-label">Open Threads <span class="tag">{len([t for t in open_threads if "✅" not in t])} active</span></div>
    <ul class="threads">
      {thread_li(open_threads)}
    </ul>
  </div>

  <!-- JWH SIGNAL HIERARCHY -->
  <div class="panel">
    <div class="panel-label">JWH / Signal Hierarchy</div>
    <div class="signal-stack">
      <div class="signal-row">
        <span class="signal-badge primary">PRIMARY</span>
        <span class="signal-text">Managed Silence — sustained coordination, most intentional</span>
      </div>
      <div class="signal-row">
        <span class="signal-badge secondary">SECONDARY</span>
        <span class="signal-text">Coercion Displacement — deliberate, may be habituated</span>
      </div>
      <div class="signal-row">
        <span class="signal-badge tertiary">TERTIARY</span>
        <span class="signal-text">Consensus Redundancy — semi-emergent, Tier 1 cap alone</span>
      </div>
    </div>
    <div class="panel-label" style="margin-top:4px">Open Signals</div>
    <ul class="threads">
      {thread_li(open_signals) or '<li class="thread open"><span class="marker">◆</span>No open signals logged</li>'}
    </ul>
  </div>

  <!-- EEG STATE -->
  <div class="panel">
    <div class="panel-label">EEG / Crown 3</div>
    <div class="channel-map">
      <div class="channel left">
        <div class="ch-id">ch2</div>
        <div class="ch-label">Left<br>Frontal-Temporal</div>
      </div>
      <div class="channel right">
        <div class="ch-id">ch7</div>
        <div class="ch-label">Right<br>Posterior</div>
      </div>
    </div>
    <div class="panel-label">Calibration Protocol</div>
    <div class="protocol-bars">
      <div class="protocol-bar">
        <span class="bar-label">Solo sessions</span>
        <div class="bar-track"><div class="bar-fill" style="width:20%"></div></div>
        <span class="bar-val">1 / 5</span>
      </div>
      <div class="protocol-bar">
        <span class="bar-label">BroSis sessions</span>
        <div class="bar-track"><div class="bar-fill" style="width:20%; background:var(--coral)"></div></div>
        <span class="bar-val">1 / 5</span>
      </div>
    </div>
    <div style="font-size:9.5px;color:var(--muted);padding:6px 0">
      Alpha suppression = primary emergence gate<br>
      Population baseline: 131 sessions
    </div>
  </div>

  <!-- ACTIVE POSITIONS -->
  <div class="panel span3">
    <div class="panel-label">JWH / Active Positions</div>
    <table class="positions">
      <tr>
        <th>Asset</th><th>Entry Basis</th><th>Tier</th><th>Status</th><th>Notes</th>
      </tr>
      {position_rows(positions)}
    </table>
  </div>

  <!-- LENS PALETTE -->
  <div class="panel span2">
    <div class="panel-label">Lens Palette <span class="tag">{len(lenses)} active</span></div>
    <div class="lens-grid">
      {lens_cards(lenses)}
    </div>
  </div>

  <!-- MUSIC -->
  <div class="panel">
    <div class="panel-label">Music / Active Project</div>
    <div class="music-block">
      <strong>Galaxies</strong> + <strong>Ghost Particle</strong>
    </div>
    <div class="music-act">
      <span class="act-num">ACT I</span>
      <span class="act-desc">Ghost Particle instrumental foundation — triplet-based, same key</span>
    </div>
    <div class="music-act">
      <span class="act-num">ACT II</span>
      <span class="act-desc">Galaxies vocal layer — theological → empirical/epistemic inversion</span>
    </div>
    <div class="music-act">
      <span class="act-num">ACT III</span>
      <span class="act-desc">Live guitar — new compositional voice, synthesis point</span>
    </div>
    <div style="font-size:9.5px;color:var(--muted);margin-top:6px;font-style:italic">
      The inversion isn't cosmetic. It's the spine.
    </div>
  </div>

  <!-- LAST SESSION -->
  <div class="panel span2">
    <div class="panel-label">Last Session</div>
    <div class="log-entry">{last_session}</div>
  </div>

  <!-- STACK STATUS -->
  <div class="panel">
    <div class="panel-label">M5 Stack</div>
    <div class="stats">
      <div class="stat"><span class="stat-val" style="color:var(--green)">●</span><span class="stat-key">Ollama</span></div>
      <div class="stat"><span class="stat-val" style="color:var(--green)">●</span><span class="stat-key">Crown 3</span></div>
      <div class="stat"><span class="stat-val" style="color:var(--green)">●</span><span class="stat-key">Drive Sync</span></div>
      <div class="stat"><span class="stat-val" style="color:var(--green)">●</span><span class="stat-key">MCP Live</span></div>
      <div class="stat"><span class="stat-val" style="color:var(--green)">●</span><span class="stat-key">Claude Code</span></div>
    </div>
    <div class="panel-label" style="margin-top:8px">aaron-context/</div>
    <div style="font-size:9.5px; color:var(--muted); line-height:2;">
      {'<br>'.join(['ACTIVE_STATE.md','FRAMEWORK_CORE.md','EEG_BASELINE.md','JWH_STATE.md','MUSIC_STATE.md','SESSION_LOG.md'])}
    </div>
  </div>

</div>
</body>
</html>"""

# Write and open
out = os.path.join(BASE, ".dashboard.html")
with open(out, "w") as f:
    f.write(html)

subprocess.run(["open", out])
print(f"Dashboard opened. {now}")
