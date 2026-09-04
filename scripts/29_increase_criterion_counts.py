"""D-19: welk criterium hoort achter de tellingen op pagina 31, en wat komt eruit.

Pagina 31 telt locaties waar een zwaardere droogte de transitiekans verhoogt: 5 en 6
in periode 1, 7 en 9 in periode 2, voor drought peak en mean severity. Het
manuscript zegt niet wanneer iets als toename telt. Dit script rekent een reeks
kandidaat-criteria door op de gerepareerde definities (bootstrap van 3 september,
onafhankelijkheidstoetsen van 2 september) en legt ze naast elkaar. Het kiest niet.

Alle criteria kijken naar het verschil zwaar min mild, dus naar de twee curves die
figuur 5 tot 8 en Appendix E tonen. Toename en afname worden allebei geteld, zodat
ook de zin "most locations exhibit either no difference or a decrease" te toetsen is.

  punt         het puntverschil bij het floodniveau van het manuscript, quantiel
               0,69, boven een drempel van 0, +0,02 of +0,05. Dit is wat je met
               het oog uit de figuren afleest
  mediaan      de mediaan van het verschil over het hele y-raster boven +0,02 of
               +0,05. Dit is het criterium dat script 18 gebruikte om de
               gepubliceerde tellingen te reproduceren, nu op de gerepareerde
               definities en op de quantielas
  interval     het 95 procent bootstrapinterval van het verschil ligt geheel boven
               of onder nul, bij 0,69, of bij minstens een van de niveaus 0,69,
               0,90 en 0,95
  toetsen      minstens drie van de vier onafhankelijkheidstoetsen p < 0,05, met de
               richting uit het teken van tau. Zelfde definitie als sectie 1 van
               het bootstraprapport

Rekent niets opnieuw, leest alleen results/. Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --no-project python scripts/29_increase_criterion_counts.py
"""
import csv, hashlib, os, subprocess, sys
from datetime import date
import numpy as np

BS = "results/2026-09-02_copula_bootstrap/transition_ci.csv"
DEP = "results/2026-09-02_dependence_tests/dependence_tests.csv"
OUT = "results/2026-09-04_increase_criterion"
YC = [f"y_{i:03d}" for i in range(101)]
QM = 69                                   # runoff-quantiel 0,69, de flooddrempel
NIVEAUS = (69, 90, 95)                    # voor het criterium "op een van de niveaus"
DREMPELS_PUNT = (0.0, 0.02, 0.05)         # kandidaat-drempels op het puntverschil
DREMPELS_MEDIAAN = (0.02, 0.05)           # kandidaat-drempels op de mediaan, als script 18
TOETSEN = ("tau_p", "hoeffd_p", "aic_perm_p", "cp_q6915_p")   # als script 23
MIN_TOETSEN = 3
ALPHA = 0.05
DP, MS = "drought_peak", "mean_drought_severity"
PAIRS = (DP, MS)
PERIODES = ("first", "second")
PAIR_NL = {"drought_peak": "drought peak", "mean_drought_severity": "mean severity"}
GEPUBLICEERD = {("first", "drought_peak"): 5, ("first", "mean_drought_severity"): 6,
                ("second", "drought_peak"): 7, ("second", "mean_drought_severity"): 9}

os.makedirs(OUT, exist_ok=True)

ci, ligging = {}, {}
for r in csv.DictReader(open(BS)):
    if r["scheme"] != "iid" or r["quantity"] != "diff_resel":
        continue
    ci[(r["river"], r["village"], r["period"], r["pair"], r["kind"])] = \
        np.array([float(r[c]) for c in YC])
    ligging[(r["river"], r["village"])] = r["river_location"]
dep = {(r["river"], r["village"], r["period"], r["pair"]): r
       for r in csv.DictReader(open(DEP))}
cellen = sorted({k[:4] for k in ci})
print(f"cellen in bootstrap: {len(cellen)}, in toetsen: {len(dep)}")


def d(cel, kind):
    return ci.get(cel + (kind,))


def richting_punt(cel, drempel):
    p = d(cel, "point")
    if p is None or not np.isfinite(p[QM]):
        return None
    return "toename" if p[QM] > drempel else ("afname" if p[QM] < -drempel else "geen")


def richting_mediaan(cel, drempel):
    p = d(cel, "point")
    if p is None or not np.isfinite(p).any():
        return None
    m = float(np.nanmedian(p))
    return "toename" if m > drempel else ("afname" if m < -drempel else "geen")


def richting_interval(cel, j):
    # Vereist ook een eindige puntschatting. Bij een cel zonder zware droogte
    # geeft de parametrische route geen zware curve, maar de bootstrap heeft dan
    # toch een interval uit de replicaties die er toevallig wel een trokken. Dat
    # interval beschrijft een selectie van replicaties, niet de cel. Zonder deze
    # eis telden 13 zulke cellen mee bij het interval en niet bij het punt.
    p, lo, hi = d(cel, "point"), d(cel, "lo"), d(cel, "hi")
    if p is None or not (np.isfinite(p[j]) and np.isfinite(lo[j]) and np.isfinite(hi[j])):
        return None
    return "toename" if lo[j] > 0 else ("afname" if hi[j] < 0 else "geen")


def richting_interval_niveaus(cel):
    u = [richting_interval(cel, j) for j in NIVEAUS]
    if all(x is None for x in u):
        return None
    if "toename" in u and "afname" in u:
        return "beide"
    return "toename" if "toename" in u else ("afname" if "afname" in u else "geen")


def verschil_txt(cel, j=QM):
    p, lo, hi = d(cel, "point"), d(cel, "lo"), d(cel, "hi")
    if p is None or not np.isfinite(p[j]):
        return "geen zware curve"
    return f"verschil bij {j/100:.2f} {p[j]:+.3f} [{lo[j]:+.3f}, {hi[j]:+.3f}]"


def toetsen_txt(cel):
    r = dep.get(cel)
    if r is None:
        return "geen toetsen"
    nt = sum(1 for k in TOETSEN if float(r[k]) < ALPHA)
    return f"{nt}/4 toetsen, tau {float(r['tau']):+.3f}"


def richting_toetsen(cel):
    r = dep.get(cel)
    if r is None:
        return None
    n = sum(1 for k in TOETSEN if float(r[k]) < ALPHA)
    if n < MIN_TOETSEN:
        return "geen"
    return "toename" if float(r["tau"]) > 0 else "afname"


CRITERIA = []
for t in DREMPELS_PUNT:
    CRITERIA.append((f"punt bij 0,69 voorbij {t:+.2f}".replace("+0.00", "0"),
                     lambda c, t=t: richting_punt(c, t)))
for t in DREMPELS_MEDIAAN:
    CRITERIA.append((f"mediaan over y voorbij {t:+.2f}",
                     lambda c, t=t: richting_mediaan(c, t)))
CRITERIA.append(("95% interval sluit nul uit bij 0,69", lambda c: richting_interval(c, QM)))
CRITERIA.append(("95% interval sluit nul uit bij 0,69, 0,90 of 0,95", richting_interval_niveaus))
CRITERIA.append((f"minstens {MIN_TOETSEN} van 4 toetsen p < {ALPHA}, richting uit tau",
                 richting_toetsen))

# ------------------------------------------------------------- per cel en tellingen
per_cel = []
for cel in cellen:
    p, lo, hi = d(cel, "point"), d(cel, "lo"), d(cel, "hi")
    r = dep.get(cel)
    rij = {"river": cel[0], "village": cel[1], "period": cel[2], "pair": cel[3],
           "diff_q69": p[QM] if p is not None else np.nan,
           "lo_q69": lo[QM] if lo is not None else np.nan,
           "hi_q69": hi[QM] if hi is not None else np.nan,
           "diff_median_y": float(np.nanmedian(p)) if p is not None and np.isfinite(p).any() else np.nan,
           "n_tests_p05": sum(1 for k in TOETSEN if r and float(r[k]) < ALPHA) if r else "",
           "tau": r["tau"] if r else ""}
    for naam, f in CRITERIA:
        rij[naam] = f(cel) or "geen zware curve"
    per_cel.append(rij)

with open(f"{OUT}/per_cell.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(per_cel[0].keys()))
    w.writeheader()
    w.writerows(per_cel)

tellingen = []
for naam, f in CRITERIA:
    for per in PERIODES:
        for pair in PAIRS:
            u = [f(c) for c in cellen if c[2] == per and c[3] == pair]
            geldig = [x for x in u if x]
            tellingen.append({"criterium": naam, "period": per, "pair": pair,
                              "toename": geldig.count("toename"),
                              "afname": geldig.count("afname"),
                              "beide": geldig.count("beide"),
                              "geen": geldig.count("geen"),
                              "n_beoordeeld": len(geldig),
                              "n_zonder_zware_curve": u.count(None),
                              "gepubliceerd": GEPUBLICEERD[(per, pair)]})
with open(f"{OUT}/counts.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(tellingen[0].keys()))
    w.writeheader()
    w.writerows(tellingen)

# ------------------------------------------------------------------------ rapport
L = []
A = L.append
A("# D-19: het criterium achter de tellingen op pagina 31")
A("")
A("Pagina 31 van het manuscript:")
A("")
A("> In the first period, increases in transition probability are observed in 5")
A("> locations for Drought Peak and in 6 locations for Mean Severity, while in the")
A("> second period, the count rises slightly to 7 and 9 respectively.")
A("")
A("Er staat niet wanneer iets als toename telt. Hieronder acht kandidaat-criteria, alle")
A("op het verschil zwaar min mild uit de bootstrap van 3 september op de gerepareerde")
A("definities, iid-schema, parametrische marginalen, quantielas. Het toetsencriterium")
A("komt uit de onafhankelijkheidstoetsen van 2 september. Beide bronnen zijn post-fix.")
A("")
zonder = sum(1 for c in cellen if richting_punt(c, 0) is None)
A(f"Cellen: {len(cellen)} van 192. Dnieper Cherson periode 1 valt buiten de bootstrap,")
A(f"minder dan 15 events. Van de {len(cellen)} hebben er {zonder} geen zware curve, omdat er")
A("geen enkele droogte boven de zware drempel ligt. Die tellen nergens mee, ook niet als")
A("\"geen verschil\", want er is niets vergeleken.")
A("")
A("## Tellingen per criterium")
A("")
A("Kolommen: periode 1 drought peak, periode 1 mean severity, periode 2 drought peak,")
A("periode 2 mean severity. Elke cel toont toename / afname / geen verschil, met tussen")
A("haakjes het aantal beoordeelde cellen als dat afwijkt van 48.")
A("")
A("| criterium | p1 DP | p1 MS | p2 DP | p2 MS | toename totaal |")
A("|---|---|---|---|---|---|")
A("| gepubliceerd, pagina 31, alleen toenames | 5 | 6 | 7 | 9 | 27 |")
A("| script 18, pre-fix, rangas, mediaan > +0,02, alleen toenames | 7 | 5 | 6 | 9 | 27 |")
for naam, _ in CRITERIA:
    rijen = [t for t in tellingen if t["criterium"] == naam]
    cellen_txt = []
    for t in rijen:
        s = f"{t['toename']} / {t['afname']} / {t['geen']}"
        if t["beide"]:
            s += f" / {t['beide']} beide"
        if t["n_beoordeeld"] != 48:
            s += f" ({t['n_beoordeeld']})"
        cellen_txt.append(s)
    A(f"| {naam} | " + " | ".join(cellen_txt) + f" | {sum(t['toename'] for t in rijen)} |")
A("")
A("Bij het interval-criterium over drie niveaus betekent \"beide\" dat het interval op")
A("het ene niveau boven nul ligt en op een ander niveau onder nul.")
A("")

# ----------------------------------------------------- welke locaties per criterium
A("## Welke locaties, per criterium")
A("")
A("Alleen de criteria die als tekstcriterium in aanmerking komen. Het puntcriterium")
A("zonder drempel staat er voor de vergelijking bij.")
A("")
for naam in ("punt bij 0,69 voorbij +0.02", "95% interval sluit nul uit bij 0,69",
             "95% interval sluit nul uit bij 0,69, 0,90 of 0,95",
             f"minstens {MIN_TOETSEN} van 4 toetsen p < {ALPHA}, richting uit tau"):
    f = dict(CRITERIA)[naam]
    A(f"### {naam}")
    A("")
    for label in ("toename", "afname", "beide"):
        hits = [c for c in cellen if f(c) == label]
        if not hits:
            continue
        A(f"**{label}**, {len(hits)} cellen:")
        A("")
        for c in hits:
            A(f"- {c[0]} {c[1]}, periode {'1' if c[2] == 'first' else '2'}, {PAIR_NL[c[3]]}: "
              f"{verschil_txt(c)}, {toetsen_txt(c)}")
        A("")

# ------------------------------------------------------ overlap tussen de criteria
A("## Overlap: houden de tellingen van het mediaancriterium stand onder onzekerheid")
A("")
A("Het mediaancriterium bij +0,02 komt post-fix het dichtst bij de gepubliceerde")
A("tellingen. Van de cellen die het als toename aanwijst, hoeveel halen ook een")
A("onzekerheidscriterium:")
A("")
med = [c for c in cellen if richting_mediaan(c, 0.02) == "toename"]
med_int = [c for c in med if richting_interval(c, QM) == "toename"]
med_int3 = [c for c in med if richting_interval_niveaus(c) == "toename"]
med_toets = [c for c in med if richting_toetsen(c) == "toename"]
A(f"| criterium | van de {len(med)} mediaan-toenames |")
A("|---|---|")
A(f"| 95% interval boven nul bij 0,69 | {len(med_int)} |")
A(f"| 95% interval boven nul bij 0,69, 0,90 of 0,95 | {len(med_int3)} |")
A(f"| minstens {MIN_TOETSEN} van 4 toetsen, tau > 0 | {len(med_toets)} |")
A("")
A("Omgekeerd, de toetsen-toenames die het mediaancriterium mist:")
A("")
for c in cellen:
    if richting_toetsen(c) == "toename" and c not in med:
        A(f"- {c[0]} {c[1]}, periode {'1' if c[2] == 'first' else '2'}, {PAIR_NL[c[3]]}: "
          f"{verschil_txt(c)}, mediaan over y "
          f"{float(np.nanmedian(d(c, 'point'))):+.3f}" if np.isfinite(d(c, 'point')).any() else
          f"- {c[0]} {c[1]}, periode {'1' if c[2] == 'first' else '2'}, {PAIR_NL[c[3]]}: "
          f"geen zware curve, {toetsen_txt(c)}")
A("")
A("De twee criteria meten iets anders. De mediaan over y en het interval kijken naar")
A("de afstand tussen twee gesimuleerde curves, waarvan de zware op weinig events rust,")
A("mediaan 1 event boven de zware drempel. De toetsen kijken naar de samenhang tussen")
A("droogtezwaarte en piek over alle events van de cel, en dat is de samenhang die het")
A("verschil tussen de curves hoort uit te drukken.")
A("")

# ------------------------------------------------------------------- conceptteksten
def tel(f, per, pair, label):
    return sum(1 for c in cellen if c[2] == per and c[3] == pair and f(c) == label)


A("## Conceptteksten voor pagina 31, per criterium")
A("")
A("Engelse tekst met de post-fix tellingen ingevuld, ter vervanging van de alinea")
A("\"In the first period, increases ... 7 and 9 respectively.\" De keuze is aan Floris.")
A("")
ft = richting_toetsen
A("### Optie A: de onafhankelijkheidstoetsen")
A("")
A("> We count a location as showing an increase (decrease) in transition probability")
A("> with drought severity when at least three of the four dependence tests described")
A("> in Section 2.4.2 reject independence at the 5% level and Kendall's tau is")
A(f"> positive (negative). In the first period, increases are found at {tel(ft, 'first', DP, 'toename')} location(s)")
A(f"> for Drought Peak and {tel(ft, 'first', MS, 'toename')} for Mean Severity; in the second period at")
A(f"> {tel(ft, 'second', DP, 'toename')} and {tel(ft, 'second', MS, 'toename')} respectively. Decreases are found at {tel(ft, 'first', DP, 'afname')} and {tel(ft, 'first', MS, 'afname')}")
A(f"> locations in the first period and at {tel(ft, 'second', DP, 'afname')} and {tel(ft, 'second', MS, 'afname')} in the second. At the")
A("> remaining locations the dependence between drought severity and the subsequent")
A("> runoff peak cannot be distinguished from independence.")
A("")
fi = lambda c: richting_interval(c, QM)
A("### Optie B: het bootstrapinterval bij het floodniveau van het manuscript")
A("")
A("> We count a location as showing an increase (decrease) in transition probability")
A("> when the 95% bootstrap interval of the difference between the major and the minor")
A("> conditional curve, evaluated at the 0.69 runoff quantile, lies entirely above")
A(f"> (below) zero. Under this criterion, {tel(fi, 'first', DP, 'toename')} and {tel(fi, 'first', MS, 'toename')} locations show an increase")
A(f"> in the first period for Drought Peak and Mean Severity, and {tel(fi, 'second', DP, 'toename')} and {tel(fi, 'second', MS, 'toename')} in the")
A(f"> second period; {tel(fi, 'first', DP, 'afname')} and {tel(fi, 'first', MS, 'afname')} locations show a decrease in the first period and")
A(f"> {tel(fi, 'second', DP, 'afname')} and {tel(fi, 'second', MS, 'afname')} in the second. At all other locations the interval includes zero.")
A("")
fm = lambda c: richting_mediaan(c, 0.02)
A("### Optie C: het puntcriterium dat de gepubliceerde tellingen benadert")
A("")
A("> We count a location as showing an increase (decrease) in transition probability")
A("> when the median difference between the major and the minor conditional curve over")
A(f"> all flood quantiles exceeds +0.02 (falls below -0.02). In the first period, increases are observed at {tel(fm, 'first', DP, 'toename')} locations")
A(f"> for Drought Peak and {tel(fm, 'first', MS, 'toename')} for Mean Severity, and at {tel(fm, 'second', DP, 'toename')} and {tel(fm, 'second', MS, 'toename')} in the second period;")
A(f"> decreases at {tel(fm, 'first', DP, 'afname')} and {tel(fm, 'first', MS, 'afname')}, and at {tel(fm, 'second', DP, 'afname')} and {tel(fm, 'second', MS, 'afname')}. These counts are based on point")
A("> estimates only; see Appendix E for the bootstrap intervals.")
A("")
A("Bij optie C hoort de kanttekening dat een reviewer die R4-03 heeft gesteld het")
A("ontbreken van onzekerheid in een telling zal opmerken.")
A("")

# ---------------------------------------------- de met naam genoemde locaties op p31
A("## De locaties die pagina 31 met naam noemt")
A("")
A("Wat het verschil zwaar min mild daar doet, met het 95 procent interval bij 0,69 en")
A("het aantal toetsen. Vet als het interval nul uitsluit.")
A("")
A("| locatie | periode | variabele | verschil bij 0,69 | interval | toetsen | tekst zegt |")
A("|---|---|---|---|---|---|---|")
GENOEMD = [
    ("Dnieper", "Krementsjoek", "first", "mean_drought_severity", "toename, ook boven unconditioneel"),
    ("Dnieper", "Dnipro", "second", "mean_drought_severity", "toename"),
    ("Tagus", "La Bazagona", "first", "drought_peak", "lichte toename"),
    ("Tagus", "La Bazagona", "first", "mean_drought_severity", "lichte toename"),
    ("Tagus", "Vila Velha de Rodao", "first", "drought_peak", "afname"),
    ("Tagus", "Vila Velha de Rodao", "first", "mean_drought_severity", "afname"),
    ("Tagus", "Vila Velha de Rodao", "second", "drought_peak", "toename"),
    ("Tagus", "Vila Velha de Rodao", "second", "mean_drought_severity", "toename"),
    ("Tagus", "Toledo", "second", "drought_peak", "geen toename"),
    ("Tagus", "Toledo", "second", "mean_drought_severity", "geen toename"),
]
for riv, vil, per, pair, zegt in GENOEMD:
    c = (riv, vil, per, pair)
    if c not in cellen:
        A(f"| {riv} {vil} | {'1' if per == 'first' else '2'} | {PAIR_NL[pair]} | niet in bootstrap | | | {zegt} |")
        continue
    p, lo, hi = d(c, "point"), d(c, "lo"), d(c, "hi")
    r = dep.get(c)
    nt = sum(1 for k in TOETSEN if r and float(r[k]) < ALPHA) if r else 0
    if not np.isfinite(p[QM]):
        A(f"| {riv} {vil} | {'1' if per == 'first' else '2'} | {PAIR_NL[pair]} | geen zware curve | | {nt}/4 | {zegt} |")
        continue
    vet = "**" if (lo[QM] > 0 or hi[QM] < 0) else ""
    A(f"| {riv} {vil} | {'1' if per == 'first' else '2'} | {PAIR_NL[pair]} | {vet}{p[QM]:+.3f}{vet} | "
      f"[{lo[QM]:+.3f}, {hi[QM]:+.3f}] | {nt}/4 | {zegt} |")
A("")
A("Vistula en Oder midstream, drought peak: de tekst zegt toename alleen bij hogere")
A("floodquantielen. Verschil zwaar min mild bij 0,69, 0,90 en 0,95 met interval:")
A("")
A("| locatie | ligging | periode | 0,69 | 0,90 | 0,95 |")
A("|---|---|---|---|---|---|")
for c in cellen:
    if c[0] in ("Vistula", "Oder") and c[3] == "drought_peak":
        p, lo, hi = d(c, "point"), d(c, "lo"), d(c, "hi")
        vals = []
        for j in NIVEAUS:
            if np.isfinite(p[j]):
                vet = "**" if (lo[j] > 0 or hi[j] < 0) else ""
                vals.append(f"{vet}{p[j]:+.3f}{vet} [{lo[j]:+.3f}, {hi[j]:+.3f}]")
            else:
                vals.append("geen zware curve")
        A(f"| {c[0]} {c[1]} | {ligging[c[:2]]} | {'1' if c[2] == 'first' else '2'} | " + " | ".join(vals) + " |")
A("")

# ------------------------------------------------------------------------ bestanden
A("## Bestanden")
A("")
A("- `counts.csv`: de tellingen per criterium, periode en variabele")
A("- `per_cell.csv`: per cel het verschil bij 0,69 met interval, de mediaan over y, het")
A("  aantal toetsen en de uitkomst onder elk criterium")
A("- `manifest.yaml`: herkomst en checksums van de twee bronbestanden")
A("")
A("De weging van de criteria en het voorstel staan in `docs/open-decisions.md`, D-19.")
open(f"{OUT}/report.md", "w").write("\n".join(L) + "\n")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def git(*args):
    try:
        return subprocess.check_output(["git", *args], text=True).strip()
    except Exception:
        return "onbekend"


man = f"""run_date: {date.today().isoformat()}
script: scripts/29_increase_criterion_counts.py
git_commit: {git("rev-parse", "HEAD")}
git_dirty: {"true" if git("status", "--porcelain") else "false"}
config:
  taak: D-19, criterium achter de tellingen op pagina 31
  rekent_opnieuw: nee, leest alleen results/
  quantity: diff_resel        # zwaar min mild, familie-herselectie per replicatie
  scheme: iid
  marginals: parametric       # zoals de bootstrap
  axis: quantile
  niveau_manuscript: y_{QM:03d}  # runoff-quantiel {QM/100:.2f}
  niveaus_extra: {list(NIVEAUS)}
  drempels_punt: {list(DREMPELS_PUNT)}
  drempels_mediaan: {list(DREMPELS_MEDIAAN)}
  toetsen: {list(TOETSEN)}
  min_toetsen: {MIN_TOETSEN}
  alpha: {ALPHA}
  cells: {len(cellen)}
  cells_zonder_zware_curve: {zonder}
inputs:
  {BS}: {sha(BS)}
  {DEP}: {sha(DEP)}
packages:
  python: {sys.version.split()[0]}
  numpy: {np.__version__}
"""
open(f"{OUT}/manifest.yaml", "w").write(man)
print("\n".join(L[:60]))
print(f"\ngeschreven naar {OUT}/")
