"""
Vector 5 - Retrodictive Scoping Test
SIS-Fold Theorem: stability <-> mode-locked phase coherence at integer p/q.
Vector 1 (precise predictions) incomplete - this is a SCOPING test asking
whether rational-ratio clustering appears in nuclear data qualitatively.
"""
import urllib.request
import numpy as np
from collections import Counter

# 1. Pull AME 2020
AME_URL = "https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20.txt"
print("Fetching AME 2020 mass table...")
raw = None
try:
    req = urllib.request.Request(AME_URL, headers={"User-Agent": "v5/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("latin-1")
    print(f"  Downloaded: {len(raw)} bytes")
except Exception as e:
    print(f"  AME fetch failed: {e}")

records = []
if raw:
    lines = raw.splitlines()
    # AME 2020 has ~38 lines of header before data
    # Try to auto-detect data start: look for lines where positions [4:9] are an integer
    data_start = None
    for i, line in enumerate(lines):
        if len(line) > 80:
            try:
                n_test = int(line[4:9].strip())
                z_test = int(line[9:14].strip())
                a_test = int(line[14:19].strip())
                if n_test + z_test == a_test and a_test > 0:
                    data_start = i
                    break
            except (ValueError, IndexError):
                continue
    print(f"  Data starts at line {data_start}")
    if data_start is not None:
        print(f"  Sample line: {lines[data_start][:100]!r}")
        for line in lines[data_start:]:
            if len(line) < 80:
                continue
            try:
                N = int(line[4:9].strip())
                Z = int(line[9:14].strip())
                A = int(line[14:19].strip())
                el = line[20:23].strip()
                ba_raw = line[54:67].replace('#','').replace('*','').strip()
                if not ba_raw:
                    continue
                ba_kev = float(ba_raw)
                records.append({"N":N, "Z":Z, "A":A, "el":el, "ba_kev":ba_kev})
            except (ValueError, IndexError):
                continue
print(f"  Parsed {len(records)} nuclide records")

# Fallback: embedded most-abundant stable isotope per element
if not records:
    print("  Using embedded fallback dataset")
    stable = [
        (1,1),(2,4),(3,7),(4,9),(5,11),(6,12),(7,14),(8,16),(9,19),(10,20),
        (11,23),(12,24),(13,27),(14,28),(15,31),(16,32),(17,35),(18,40),(19,39),(20,40),
        (21,45),(22,48),(23,51),(24,52),(25,55),(26,56),(27,59),(28,58),(29,63),(30,64),
        (31,69),(32,74),(33,75),(34,80),(35,79),(36,84),(37,85),(38,88),(39,89),(40,90),
        (41,93),(42,98),(43,98),(44,102),(45,103),(46,106),(47,107),(48,114),(49,115),(50,120),
        (51,121),(52,130),(53,127),(54,132),(55,133),(56,138),(57,139),(58,140),(59,141),(60,142),
        (61,145),(62,152),(63,153),(64,158),(65,159),(66,164),(67,165),(68,166),(69,169),(70,174),
        (71,175),(72,180),(73,181),(74,184),(75,187),(76,192),(77,193),(78,195),(79,197),(80,202),
        (81,205),(82,208),(83,209),(90,232),(92,238)
    ]
    for z, a in stable:
        records.append({"N":a-z, "Z":z, "A":a, "el":"?", "ba_kev":None})

# Identify peak-stability isotope per element
by_z = {}
for r in records:
    z = r["Z"]
    cur = by_z.get(z)
    if cur is None:
        by_z[z] = r
        continue
    if r["ba_kev"] is not None and (cur["ba_kev"] is None or r["ba_kev"] > cur["ba_kev"]):
        by_z[z] = r

peak = sorted(by_z.values(), key=lambda r: r["Z"])
print(f"\n  Peak-stability isotope identified for {len(peak)} elements")
print(f"  Sample Z=26: {by_z.get(26)}")
print(f"  Sample Z=82: {by_z.get(82)}")

# Compute Z/A ratios
ratios = []
for r in peak:
    if r["A"] > 0 and r["Z"] >= 2:
        ratios.append({"Z":r["Z"], "A":r["A"], "z_over_a":r["Z"]/r["A"]})
print(f"\n  {len(ratios)} ratios computed (excluding H)")

# Nearest rational with denominator <= max_denom
def nearest_rational(x, max_denom):
    best = (0, 1, abs(x))
    for q in range(1, max_denom+1):
        p = round(x * q)
        d = abs(x - p/q)
        if d < best[2]:
            best = (p, q, d)
    return best

# Test 1: clustering vs uniform null
np.random.seed(42)
for max_denom in [3, 5, 8, 13]:
    distances = np.array([nearest_rational(r["z_over_a"], max_denom)[2] for r in ratios])
    null_samples = np.random.uniform(0.35, 0.50, size=(2000, len(ratios)))
    null_means = []
    for i in range(null_samples.shape[0]):
        nd = [nearest_rational(x, max_denom)[2] for x in null_samples[i]]
        null_means.append(np.mean(nd))
    null_means = np.array(null_means)
    obs = distances.mean()
    nm = null_means.mean()
    ns = null_means.std()
    z = (obs - nm)/ns if ns > 0 else float('nan')
    p_lower = (null_means <= obs).mean()
    flag = "  <-- significant clustering" if p_lower < 0.05 else ""
    print(f"\n=== max_denom = {max_denom} ===")
    print(f"  Observed mean dist:  {obs:.5f}")
    print(f"  Null mean (uniform): {nm:.5f} +/- {ns:.5f}")
    print(f"  Z-score: {z:.3f}")
    print(f"  P(null <= obs): {p_lower:.4f}{flag}")

# Test 2: which specific rationals?
print("\n\n=== Specific rationals (max_denom=8, within 0.01) ===")
hits = Counter()
for r in ratios:
    p, q, d = nearest_rational(r["z_over_a"], 8)
    if d < 0.01:
        hits[f"{p}/{q}"] += 1
for frac, n in hits.most_common():
    print(f"    {frac:>6} : {n} hits")

# Stability valley walk
print("\n=== Z/A across stability valley ===")
for z_check in [2, 8, 20, 26, 50, 82, 92]:
    if z_check in by_z:
        r = by_z[z_check]
        ratio = r["Z"]/r["A"]
        p, q, d = nearest_rational(ratio, 8)
        print(f"  Z={z_check:>3} A={r['A']:>3}: Z/A={ratio:.4f}  near {p}/{q}={p/q:.4f}  (d={d:.4f})")

print("\n=== Done ===")
