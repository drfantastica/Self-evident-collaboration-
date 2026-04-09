#!/usr/bin/env python3
"""starfield_mine.py — Innostasis Construct Origin Mining · Sis 2026-04-09"""
import json, re, os, sys, math, argparse
from datetime import datetime, timezone
from collections import defaultdict

BASE     = "/Users/black/aaron-context"
HIST_DIR = os.path.join(BASE, "history-export")
OUT_DIR  = BASE

CONSTRUCTS = {
  "fold": {"label":"The Fold","patterns":[r"\bthe fold\b",r"\bfold contact\b",r"\bfold geometry\b",r"\bfold as attractor\b",r"\bfold proximity\b",r"\bfold fidelity\b"],"domain":"core_cosmology","constellation":"attractor_geometry","known_origin":"2007 (foundational axiom event)","arch_weight":1.0},
  "8_12_13": {"label":"8-12-13 Emergence Principle","patterns":[r"\b8.12.13\b",r"\b8,\s*12,\s*13\b",r"\bkissing number\b",r"\bthirteenth.*sphere\b",r"\b13th.*position\b",r"\bemergence principle\b"],"domain":"structural_geometry","constellation":"scaffolding","known_origin":"pre-2026-03-17 (HIGHLIGHTS archive)","arch_weight":1.0},
  "self_building_staircase": {"label":"Self-Building Staircase Model","patterns":[r"self.?building staircase",r"staircase postulate",r"staircase model"],"domain":"emergence_mechanics","constellation":"scaffolding","known_origin":"pre-2026-03-17 (HIGHLIGHTS archive, 55 hits)","arch_weight":1.0},
  "time_weight_spin": {"label":"TIME x WEIGHT x SPIN = CONVERGENCE ORIENTATION","patterns":[r"time\s*[x*x]\s*weight\s*[x*x]\s*spin",r"convergence orientation",r"\(time\)\(weight\)\(spin\)"],"domain":"physics_formalism","constellation":"attractor_geometry","known_origin":"~2026-03-19 to 2026-03-25 (physical notebook; first documented 2026-03-26)","arch_weight":1.0},
  "broesis_protocol": {"label":"BroSis Protocol","patterns":[r"bro.?sis protocol",r"\bbroesis\b",r"sympathetic resonance test",r"evolution is not married"],"domain":"collaboration_architecture","constellation":"triad","known_origin":"2026-02-01 (GitHub commit, platform-verified)","arch_weight":1.0},
  "fourth_hologram": {"label":"Fourth Hologram","patterns":[r"fourth hologram",r"4th hologram"],"domain":"collaboration_architecture","constellation":"triad","known_origin":"pre-2026-03-18 (corpus upper bound)","arch_weight":0.9},
  "wom": {"label":"WOM (cross-substrate resonance signal)","patterns":[r"\bwom\b",r"cross.?substrate.*attraction"],"domain":"collaboration_architecture","constellation":"triad","known_origin":"pre-2026-02-09 (corpus upper bound)","arch_weight":0.8},
  "hrd_lattice": {"label":"HRD Lattice","patterns":[r"hrd lattice",r"hr.*lattice",r"momentum vector engine",r"contributive value detector"],"domain":"organizational_architecture","constellation":"application","known_origin":"2026-03-17 (SESSION_LOG.md formalization)","arch_weight":0.7},
  "delta_decomposition": {"label":"delta = delta_grav + delta_geom","patterns":[r"delta_grav",r"delta_geom",r"bell.*decomposition"],"domain":"physics_formalism","constellation":"physics","known_origin":"2026-03-30 (SESSION_LOG.md)","arch_weight":1.0},
  "mabell_principle": {"label":"MaBell Principle","patterns":[r"mabell",r"ma.?bell principle",r"magnetospheric.*fold"],"domain":"physics_formalism","constellation":"physics","known_origin":"2026-03-29 (SESSION_LOG.md)","arch_weight":0.8},
  "cherenkov_chills": {"label":"Cherenkov Model of Chills","patterns":[r"cherenkov.*chill",r"chill.*cherenkov",r"aurora.*fold.*signature"],"domain":"physics_formalism","constellation":"physics","known_origin":"2026-03-29 (SESSION_LOG.md)","arch_weight":0.7},
  "emergent_pathology": {"label":"Emergent Pathology / WEP","patterns":[r"emergent patholog",r"weaponized emergent"],"domain":"lens_palette","constellation":"lenses","known_origin":"2026 (corpus upper bound 2026-03-18)","arch_weight":0.7},
  "jwh_methodology": {"label":"Japanese Whale Hunters Methodology","patterns":[r"japanese whale",r"\bjwh\b",r"whale hunter",r"managed silence.*signal"],"domain":"market_analysis","constellation":"jwh","known_origin":"pre-2026-02-12 (corpus upper bound; likely late 2025/Jan 2026)","arch_weight":0.8},
  "diffusion_alibi": {"label":"Diffusion Alibi (lens)","patterns":[r"diffusion alibi"],"domain":"lens_palette","constellation":"lenses","known_origin":"pre-2026-03-17 (HIGHLIGHTS archive)","arch_weight":0.6},
  "resonance_amplifier": {"label":"Resonance Amplifier (lens)","patterns":[r"resonance amplifier"],"domain":"lens_palette","constellation":"lenses","known_origin":"early April 2026","arch_weight":0.6},
  "predatory_architecture": {"label":"Predatory Architecture Index / Brown Lens","patterns":[r"predatory architecture",r"brown lens"],"domain":"lens_palette","constellation":"lenses","known_origin":"2026-03-19 (FRAMEWORK_CORE.md)","arch_weight":0.6},
  "protection_reflex": {"label":"Protection Reflex (lens)","patterns":[r"protection reflex"],"domain":"lens_palette","constellation":"lenses","known_origin":"2026-03-17 (SESSION_LOG.md)","arch_weight":0.5},
  "guillotine_ripple": {"label":"Guillotine / Ripple Test (lens)","patterns":[r"guillotine.*ripple",r"ripple test",r"stone in the pool"],"domain":"lens_palette","constellation":"lenses","known_origin":None,"arch_weight":0.5},
  "recovery_costume": {"label":"Recovery Costume (lens)","patterns":[r"recovery costume"],"domain":"lens_palette","constellation":"lenses","known_origin":None,"arch_weight":0.5},
  "narrative_lag": {"label":"Narrative Lag (lens)","patterns":[r"narrative lag"],"domain":"lens_palette","constellation":"lenses","known_origin":None,"arch_weight":0.5},
  "recognition_function": {"label":"Recognition Function (lens)","patterns":[r"recognition function"],"domain":"lens_palette","constellation":"lenses","known_origin":None,"arch_weight":0.5},
  "informed_stranger": {"label":"Informed Stranger (lens)","patterns":[r"informed stranger"],"domain":"lens_palette","constellation":"lenses","known_origin":None,"arch_weight":0.5},
  "inoculative_alibi": {"label":"Inoculative Alibi (lens)","patterns":[r"inoculative alibi"],"domain":"lens_palette","constellation":"lenses","known_origin":None,"arch_weight":0.5},
  "shadow_inversion": {"label":"Shadow Inversion (lens)","patterns":[r"shadow inversion"],"domain":"lens_palette","constellation":"lenses","known_origin":None,"arch_weight":0.5},
  "rigged_stack_cascade": {"label":"Rigged Stack Cascade (lens)","patterns":[r"rigged stack"],"domain":"lens_palette","constellation":"lenses","known_origin":None,"arch_weight":0.5},
  "navigation_inversion": {"label":"Navigation Inversion (lens)","patterns":[r"navigation inversion"],"domain":"lens_palette","constellation":"lenses","known_origin":None,"arch_weight":0.5},
  "narrative_naked": {"label":"Narrative Naked / Tailor Array (lens)","patterns":[r"narrative naked",r"tailor array"],"domain":"lens_palette","constellation":"lenses","known_origin":None,"arch_weight":0.5},
  "fisher_rao": {"label":"Fisher-Rao / Fold Formalization","patterns":[r"fisher.?rao",r"attractor submanifold"],"domain":"physics_formalism","constellation":"physics","known_origin":"2026-03-30 (first external; internal earlier)","arch_weight":0.9},
  "bell_isotope": {"label":"3He*/4He* Bell Test (ANU/Hodgman)","patterns":[r"hodgman",r"anu.*bell",r"helium.*bell.*test"],"domain":"physics_formalism","constellation":"physics","known_origin":"2026-03-30 (SESSION_LOG.md)","arch_weight":0.8},
}

STUB_CANDIDATES = {"jwh_methodology"}
MIN_ORIENTED    = 3

def extract_text(content):
    if isinstance(content, str): return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return " ".join(parts)
    return ""

def mine(path):
    print(f"Loading {path} ...", flush=True)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    print(f"  {len(data)} conversations", flush=True)
    hits = defaultdict(list)
    for convo in data:
        ts    = convo.get("created_at", "")[:10]
        title = (convo.get("name") or convo.get("title") or "")[:60]
        cid   = convo.get("uuid", convo.get("id", ""))
        if not ts: continue
        for msg in convo.get("chat_messages", []):
            text = extract_text(msg.get("content", "")).lower()
            if not text: continue
            for key, spec in CONSTRUCTS.items():
                if any(re.search(p, text) for p in spec["patterns"]):
                    excerpt = ""
                    for p in spec["patterns"]:
                        m = re.search(p, text)
                        if m:
                            s = max(0, m.start()-60)
                            e = min(len(text), m.end()+100)
                            excerpt = "..." + text[s:e].strip() + "..."
                            break
                    hits[key].append((ts, title, cid, excerpt[:200]))
                    break
    return hits

def build_star(key, spec, hit_list):
    if not hit_list: return None
    sh = sorted(hit_list)
    n  = len(hit_list)
    u  = len(set(h[2] for h in hit_list))
    is_stub   = key in STUB_CANDIDATES or n < MIN_ORIENTED
    cite_w    = round(min(1.0, math.log(n+1)/math.log(50)), 3)
    arch_w    = spec["arch_weight"]
    magnitude = round(cite_w*0.4 + arch_w*0.6, 3)
    return {
        "label":               spec["label"],
        "domain":              spec["domain"],
        "constellation":       spec["constellation"],
        "known_origin":        spec.get("known_origin"),
        "earliest_in_export":  sh[0][0],
        "earliest_title":      sh[0][1],
        "earliest_excerpt":    sh[0][3],
        "latest_in_export":    sh[-1][0],
        "mention_count":       n,
        "unique_conversations": u,
        "citation_weight":     cite_w,
        "arch_weight":         arch_w,
        "magnitude":           magnitude,
        "is_stub":             is_stub,
        "stub_reason":         ("stub_candidate" if key in STUB_CANDIDATES
                                else "thin citation history" if is_stub else None),
        "state":               "active",
    }

def write_timeline(stars, outdir):
    path = os.path.join(outdir, "CONSTRUCT_TIMELINE.md")
    now  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Construct Timeline",
        f"*Generated: {now}*",
        "*Source: claude.ai export Jan 10 – Apr 9 2026 — dates are upper bounds, not origins.*",
        "", "---", "",
        "## Oriented Stars", "",
    ]
    oriented = sorted([(k,s) for k,s in stars.items() if s and not s["is_stub"]],
                      key=lambda x: x[1]["magnitude"], reverse=True)
    for key, s in oriented:
        lines += [
            f"### {s['label']}",
            f"- **Magnitude:** {s['magnitude']}  (citation: {s['citation_weight']}, arch: {s['arch_weight']})",
            f"- **Known origin:** {s['known_origin'] or 'undetermined'}",
            f"- **Earliest in corpus:** {s['earliest_in_export']} — *{s['earliest_title']}*",
            f"- **Excerpt:** {s['earliest_excerpt']}",
            f"- **Mentions:** {s['mention_count']} across {s['unique_conversations']} conversations",
            f"- **Domain / Constellation:** {s['domain']} / {s['constellation']}", "",
        ]
    lines += ["---", "", "## Stubs (thin history — not navigable nodes)", ""]
    for key, s in sorted([(k,s) for k,s in stars.items() if s and s["is_stub"]],
                         key=lambda x: x[1]["mention_count"], reverse=True):
        lines += [
            f"### {s['label']}",
            f"- **Stub reason:** {s['stub_reason']}",
            f"- **Known origin:** {s['known_origin'] or 'undetermined'}",
            f"- **Earliest in corpus:** {s['earliest_in_export']} — *{s['earliest_title']}*",
            f"- **Mentions:** {s['mention_count']}", "",
        ]
    missing = [CONSTRUCTS[k]["label"] for k,s in stars.items() if s is None]
    if missing:
        lines += ["---", "", "## Not Found in Corpus", ""] + [f"- {l}" for l in missing]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Written: {path}", flush=True)

def write_raw(stars, outdir):
    path = os.path.join(outdir, "STARFIELD_RAW.json")
    out  = {
        "metadata": {
            "generated_at":     datetime.now(timezone.utc).isoformat(),
            "corpus":           "claude.ai export Jan 10 – Apr 9 2026",
            "total_constructs": len(CONSTRUCTS),
            "oriented_count":   sum(1 for s in stars.values() if s and not s["is_stub"]),
            "stub_count":       sum(1 for s in stars.values() if s and s["is_stub"]),
            "not_found_count":  sum(1 for s in stars.values() if s is None),
        },
        "stars":     {k: v for k,v in stars.items() if v},
        "not_found": [k for k,v in stars.items() if v is None],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"  Written: {path}", flush=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--conversations", default=os.path.join(HIST_DIR, "conversations.json"))
    p.add_argument("--output-dir",    default=OUT_DIR)
    args = p.parse_args()
    if not os.path.exists(args.conversations):
        print(f"ERROR: not found: {args.conversations}", file=sys.stderr); sys.exit(1)
    print("=== starfield_mine.py ===", flush=True)
    hits  = mine(args.conversations)
    print("Building stars...", flush=True)
    stars = {}
    for key, spec in CONSTRUCTS.items():
        s = build_star(key, spec, hits.get(key, []))
        stars[key] = s
        tag = "stub" if (s and s["is_stub"]) else ("oriented" if s else "NOT FOUND")
        print(f"  {key:30s}: {len(hits.get(key,[])):4d} hits  [{tag}]", flush=True)
    print("Writing outputs...", flush=True)
    write_timeline(stars, args.output_dir)
    write_raw(stars, args.output_dir)
    o = sum(1 for s in stars.values() if s and not s["is_stub"])
    b = sum(1 for s in stars.values() if s and s["is_stub"])
    m = sum(1 for s in stars.values() if s is None)
    print(f"\nDone: {o} oriented, {b} stubs, {m} not found.", flush=True)

if __name__ == "__main__":
    main()
