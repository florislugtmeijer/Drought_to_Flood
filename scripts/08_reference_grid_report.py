"""Maakt de sanity checks en de tabellen bij results/2026-09-01_reference_grid/.

Leest alleen de CSV, rekent niets aan de pipeline. Elk cijfer in de README van die
map komt hieruit, zodat het met één commando na te rekenen is.

Draai na scripts/07_reference_grid.py:
    python scripts/08_reference_grid_report.py
"""
import csv, math, sys, collections, statistics as st

GRID = "results/2026-09-01_reference_grid/grid_results.csv"
BASE = "results/2026-08-23_threshold_comparison/eca_results.csv"
OLD = "results/2026-08-23_quantile_reference_variant/variant_results.csv"
ALPHA = 0.05
WINDOW_WEEKS = 4          # period_after_event
NOMINAL_PCT = 30.85       # norm.cdf(-0.5) maal 100, wat symmetrie zou geven bij 0,5
REGULATED = ("Dnieper",)  # te weinig droogte-events om te toetsen, zie D-12

INT = ("drought_count", "flood_count", "match_count_trigger", "match_count_precursor",
       "observed_matches_mc", "n_weeks")
FLT = ("p_trigger", "p_precursor", "p_mc_trigger", "pct_weeks_flood", "pct_weeks_drought")

rows = list(csv.DictReader(open(GRID)))
for r in rows:
    for k in INT: r[k] = int(r[k])
    for k in FLT: r[k] = float(r[k])

cell = lambda r: (r["quantile_reference"], r["reference_scope"])
key = lambda r: (r["period"], r["river"], r["village"])
name = lambda c: c[0] + "+" + c[1]
CELLS = sorted({cell(r) for r in rows})
# toevalsverwachting: de nullijn van de toets, aantal droogtes maal de kans dat er
# binnen het venster minstens één flood valt bij onafhankelijkheid
chance = lambda r: r["drought_count"] * (1 - (1 - WINDOW_WEEKS / r["n_weeks"]) ** r["flood_count"])

def head(t): print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)

head("SANITY CHECKS")

print(f"\n1. Volledigheid. {len(rows)} regels, verwacht {len(CELLS)*2*48}")
for c in CELLS:
    sub = [r for r in rows if cell(r) == c]
    per = collections.Counter(r["period"] for r in sub)
    print(f"   {name(c):22} {len(sub):3} regels, first {per['first']}, second {per['second']}")
dubbel = [k for k, n in collections.Counter((cell(r), key(r)) for r in rows).items() if n > 1]
print(f"   dubbele regels: {len(dubbel)}")
leeg = [key(r) for r in rows if r["drought_count"] == 0 or r["flood_count"] == 0]
print(f"   runs met nul droogtes of nul floods: {len(leeg)}"
      + (f", waaronder {leeg[:3]}" if leeg else ""))

print(f"\n2. Controlecel daily+period tegen {BASE}, threshold 0,5.")
base = {(r["period"], r["river"], r["village"]): r
        for r in csv.DictReader(open(BASE)) if float(r["threshold"]) == 0.5}
ctrl = [r for r in rows if cell(r) == ("daily", "period")]
afw = []
for r in ctrl:
    b = base[key(r)]
    for f in ("drought_count", "flood_count", "match_count_trigger"):
        if r[f] != int(b[f]): afw.append((key(r), f, r[f], int(b[f])))
    for f in ("p_mc_trigger", "p_trigger"):
        if round(r[f], 4) != round(float(b[f]), 4):
            afw.append((key(r), f, round(r[f], 4), round(float(b[f]), 4)))
print(f"   {len(ctrl)} runs vergeleken, {len(afw)} afwijkingen -> "
      + ("POORT OPEN" if not afw else "POORT DICHT"))
for a in afw[:10]: print("      AFWIJKING", a)
if afw:
    print("\n   Niet verder rapporteren, de refactor is niet inert.")
    sys.exit(1)

print("\n3. Droogtezijde mag niet meebewegen met de quantielreferentie.")
for scope in sorted({c[1] for c in CELLS}):
    d = {key(r): r["drought_count"] for r in rows if cell(r) == ("daily", scope)}
    w = {key(r): r["drought_count"] for r in rows if cell(r) == ("weekly_max", scope)}
    diff = [k for k in d if k in w and d[k] != w[k]]
    print(f"   scope={scope:6}: {len(diff)} van {len(d)} locaties wijken af")
    for k in diff[:5]: print(f"      {k}: daily {d[k]}, weekly_max {w[k]}")

print(f"\n4. Selectiviteit per cel. Symmetrie zou {NOMINAL_PCT} aan beide kanten geven.")
print(f"   {'cel':22} {'floodweken':>22} {'droogteweken':>22} {'ratio':>6}")
for c in CELLS:
    sub = [r for r in rows if cell(r) == c]
    f = [r["pct_weeks_flood"] for r in sub]; d = [r["pct_weeks_drought"] for r in sub]
    print(f"   {name(c):22} {st.mean(f):6.1f} ({min(f):4.1f} tot {max(f):4.1f})"
          f" {st.mean(d):8.1f} ({min(d):4.1f} tot {max(d):4.1f}) {st.mean(f)/st.mean(d):6.2f}")
print(f"   weekly_max+period hoort exact op {NOMINAL_PCT} te liggen, dat is de constructie.")
print("   Bij scope=full hoort het per periode juist af te wijken, dat is de bevinding van D-13.")

head("HOOFDTABEL, gemiddelde per locatie")
hdr = (f"{'cel':22} {'per':7} {'droogtes':>9} {'floods':>7} {'matches':>8} "
       f"{'toeval':>7} {'ratio':>6} {'MC<0,05':>9} {'Poisson':>9}")
def tabel(filter_fn, titel):
    print(f"\n{titel}\n{hdr}")
    for c in CELLS:
        for p in ("first", "second"):
            sub = [r for r in rows if cell(r) == c and r["period"] == p and filter_fn(r)]
            if not sub: continue
            m = st.mean(r["match_count_trigger"] for r in sub)
            ch = st.mean(chance(r) for r in sub)
            print(f"{name(c):22} {p:7} {st.mean(r['drought_count'] for r in sub):9.1f} "
                  f"{st.mean(r['flood_count'] for r in sub):7.1f} {m:8.1f} {ch:7.1f} "
                  f"{m/ch:6.2f} {sum(1 for r in sub if r['p_mc_trigger'] < ALPHA):5}/{len(sub):<3} "
                  f"{sum(1 for r in sub if r['p_trigger'] < ALPHA):5}/{len(sub):<3}")
tabel(lambda r: True, "Alle 48 locaties")
tabel(lambda r: r["river"] not in REGULATED,
      f"Zonder {', '.join(REGULATED)}, te weinig droogte-events om te toetsen, zie D-12")

head("VERSCHUIVING TEGENOVER DE HUIDIGE BEREKENING (daily+period)")
cur = {key(r): r for r in rows if cell(r) == ("daily", "period")}
for c in CELLS:
    if c == ("daily", "period"): continue
    sub = {key(r): r for r in rows if cell(r) == c}
    verliest = [k for k in sub if cur[k]["p_mc_trigger"] < ALPHA <= sub[k]["p_mc_trigger"]]
    wint = [k for k in sub if sub[k]["p_mc_trigger"] < ALPHA <= cur[k]["p_mc_trigger"]]
    dp = [sub[k]["p_mc_trigger"] - cur[k]["p_mc_trigger"] for k in sub]
    print(f"\n{name(c)}, {len(sub)} runs")
    print(f"   verliest significantie {len(verliest)}, wint significantie {len(wint)}")
    print(f"   p omhoog {sum(1 for d in dp if d > 0)}, omlaag {sum(1 for d in dp if d < 0)}, "
          f"gelijk {sum(1 for d in dp if d == 0)}, mediane verschuiving {st.median(dp):+.4f}")
    for lab, ks in (("verliest", verliest), ("wint", wint)):
        for k in ks[:10]:
            print(f"   {lab:8}: {k[0]:6} {k[1]:9} {k[2][:22]:22} "
                  f"{cur[k]['p_mc_trigger']:.4f} -> {sub[k]['p_mc_trigger']:.4f}")

head("WEKEN TEGEN EVENTS, waarom een strengere drempel minder doet dan hij lijkt")
print("Een event is een aaneengesloten reeks weken boven de drempel. Een strengere")
print("drempel maakt events vooral korter en neemt ze minder vaak helemaal weg.")
wm = {key(r): r for r in rows if cell(r) == ("weekly_max", "period")}
if wm:
    pw = st.mean(wm[k]["pct_weeks_flood"] / cur[k]["pct_weeks_flood"] - 1 for k in wm)
    pe = st.mean(wm[k]["flood_count"] / cur[k]["flood_count"] - 1 for k in wm
                 if cur[k]["flood_count"])
    print(f"\ndaily+period naar weekly_max+period: floodweken {100*pw:+.0f} procent, "
          f"floodevents {100*pe:+.0f} procent")

def elast(a, b):
    o = []
    for k in a:
        if k not in b: continue
        fa, fb = a[k]["flood_count"], b[k]["flood_count"]
        ma, mb = a[k]["match_count_trigger"], b[k]["match_count_trigger"]
        if 0 in (fa, fb, ma, mb) or fa == fb: continue
        o.append(math.log(mb / ma) / math.log(fb / fa))
    return sorted(o)

print("\nElasticiteit van matches op floods, log op log:")
e = elast(cur, wm)
if e:
    print(f"   threshold 0,5: n={len(e)} mediaan {e[len(e)//2]:.2f} "
          f"p25 {e[len(e)//4]:.2f} p75 {e[3*len(e)//4]:.2f}")
b1 = {(r["period"], r["river"], r["village"]):
      {"flood_count": int(r["flood_count"]), "match_count_trigger": int(r["match_count_trigger"])}
      for r in csv.DictReader(open(BASE)) if float(r["threshold"]) == 1.0}
o1 = {(r["period"], r["river"], r["village"]):
      {"flood_count": int(r["flood_count"]), "match_count_trigger": int(r["match_count_trigger"])}
      for r in csv.DictReader(open(OLD))}
e1 = elast(b1, o1)
print(f"   threshold 1:   n={len(e1)} mediaan {e1[len(e1)//2]:.2f} "
      f"p25 {e1[len(e1)//4]:.2f} p75 {e1[3*len(e1)//4]:.2f}")
print(f"\nSignificante runs, Monte Carlo, van de 96:")
print(f"   threshold 0,5 huidig      {sum(1 for r in cur.values() if r['p_mc_trigger'] < ALPHA)}")
if wm: print(f"   threshold 0,5 spiegelvariant  {sum(1 for r in wm.values() if r['p_mc_trigger'] < ALPHA)}")
print(f"   threshold 1   huidig      {sum(1 for r in csv.DictReader(open(BASE)) if float(r['threshold']) == 1.0 and float(r['p_mc_trigger']) < ALPHA)}")
print(f"   threshold 1   spiegelvariant  {sum(1 for r in csv.DictReader(open(OLD)) if float(r['p_mc_trigger']) < ALPHA)}")

head("LOCATIES MET DE GROOTSTE REGIMEVERSCHUIVING (D-13)")
for river in ("Dnieper", "Tagus", "Don"):
    sub = [r for r in rows if r["river"] == river]
    if not sub: continue
    print(f"\n{river}")
    for r in sorted(sub, key=lambda r: (r["village"], r["reference_scope"],
                                        r["quantile_reference"], r["period"])):
        print(f"   {r['village'][:20]:20} {r['quantile_reference']:10} {r['reference_scope']:6} "
              f"{r['period']:6} dr={r['drought_count']:3} fl={r['flood_count']:3} "
              f"m={r['match_count_trigger']:3} p_mc={r['p_mc_trigger']:.4f} "
              f"dr%={r['pct_weeks_drought']:5.1f} fl%={r['pct_weeks_flood']:5.1f}")
