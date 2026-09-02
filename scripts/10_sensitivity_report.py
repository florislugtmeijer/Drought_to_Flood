"""Sanity checks, tabellen en de figuur bij results/2026-09-01_sensitivity_grid/.

Leest alleen de CSV en de gepoolde nulverdelingen, rekent niets aan de pipeline
opnieuw. Elk cijfer in de README van die map komt hieruit, zodat het met één
commando na te rekenen is.

De kop van het antwoord op R4-01 is de gepoolde toets uit Donges et al. 2016,
sectie 2.2, vergelijking 6: het totaal aantal coincidenties over alle locaties
gedeeld door het totaal aantal droogtes over alle locaties. Coincidenties worden
nog steeds per locatie geteld, alleen teller en noemer worden gepoold. De
nulverdeling is de elementsgewijze som van de 48 Monte Carlo-verdelingen.

Draai na scripts/09_sensitivity_grid.py:
    uv run --python 3.12 --with numpy --with scipy --with matplotlib \
        python scripts/10_sensitivity_report.py
"""
import csv, os, sys, collections
import numpy as np

# Post-fix raster. De pre-fix versie staat in results/2026-09-01_sensitivity_grid/
# met zijn eigen report.txt, en wordt niet opnieuw gegenereerd.
GRID = "results/2026-09-02_sensitivity_grid_endfix"
CSV_PATH = f"{GRID}/grid_results.csv"
NULL_DIR = f"{GRID}/pooled_null"
FIG_DIR = f"{GRID}/figures"
ALPHA = 0.05
BASE_THR, BASE_WIN = 0.5, 4
BASE_FQ = 0.6914624612740131          # norm.cdf(0.5), zie het rasterscript

INT = ("drought_count", "flood_count", "match_count_trigger", "match_count_precursor",
       "observed_matches_mc", "n_weeks", "testable")
FLT = ("threshold", "flood_quantile", "p_trigger", "p_precursor", "p_mc_trigger",
       "pct_weeks_flood", "pct_weeks_drought")

rows = list(csv.DictReader(open(CSV_PATH)))
for r in rows:
    for k in INT: r[k] = int(r[k])
    for k in FLT: r[k] = float(r[k])
    r["match_window"] = int(r["match_window"])

cell = lambda r: (r["threshold"], r["flood_quantile"], r["match_window"])
loc = lambda r: (r["river"], r["village"])
tag = lambda t, q, w, p: f"thr{t}_fq{q:.4f}_win{w}_{p}"
fmtq = lambda q: f"{q:.4f}".rstrip("0")
ALLE_CELLS = sorted({cell(r) for r in rows})
# Een cel telt pas mee als beide periodes af zijn, dus als hun gepoolde
# nulverdeling op schijf staat. Zo is dit script ook tijdens een lopende run te
# draaien, en dan rapporteert het over wat af is in plaats van te crashen.
CELLS = [c for c in ALLE_CELLS
         if all(os.path.exists(f"{NULL_DIR}/{tag(*c, p)}.npy") for p in ("first", "second"))]
if len(CELLS) < len(ALLE_CELLS):
    print(f"LET OP: {len(CELLS)} van de {len(ALLE_CELLS)} cellen zijn af. Dit rapport gaat")
    print("alleen over die cellen. Draai opnieuw als het raster klaar is.\n")
rows = [r for r in rows if cell(r) in CELLS]
PLANE = sorted({c for c in CELLS if c[2] == BASE_WIN})
LINE = sorted({c for c in CELLS if (c[0], c[1]) == (BASE_THR, BASE_FQ)}, key=lambda c: c[2])
THRS = sorted({c[0] for c in PLANE})
FQS = sorted({c[1] for c in PLANE})


def head(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def pval(p):
    """Drie significante cijfers, zoals R4-06 vraagt.

    "Table 3: the p-values are shown with many decimals; rounding to three
    significant figures would improve readability."

    De ondergrens is de resolutie van 10000 simulaties: onder 0,0001 haalde geen
    enkele simulatie de waarneming. De bovengrens zit op 0,999 omdat alles daarboven
    op drie significante cijfers als "1" wegrondt, en dat suggereert een zekerheid
    die er niet is.

    LET OP: T-15 staat nog open. Drie significante cijfers botsen met de
    manuscript-afspraak van p < 0.05 of twee decimalen. Zodra die keuze valt geldt
    hij door het hele artikel en verandert deze functie mee.
    """
    if p < 1e-4:
        return "<0.0001"
    if p > 0.999:
        return ">0.999"
    return f"{p:.3g}"


# ---------------------------------------------------------------- sanity checks
head("SANITY CHECKS")

verwacht = len(CELLS) * 2 * 48
print(f"\n1. Volledigheid. {len(rows)} regels, verwacht {verwacht} "
      f"({len(CELLS)} afgeronde cellen maal 2 periodes maal 48 locaties)")
if len(CELLS) == 29:
    print("   29 cellen: 25 in het vlak plus 4 op de vensterlijn, zoals bedoeld")
else:
    print(f"   {len(CELLS)} van de 29 cellen af")
mis = [(c, p) for c in CELLS for p in ("first", "second")
       if sum(1 for r in rows if cell(r) == c and r["period"] == p) != 48]
print(f"   cel-periodes die geen 48 locaties hebben: {len(mis)}"
      + (f"  {mis[:3]}" if mis else ""))
dub = [k for k, n in collections.Counter((cell(r), r["period"], loc(r))
                                         for r in rows).items() if n > 1]
print(f"   dubbele regels: {len(dub)}")
ontbrekend = [tag(*c, p) for c in CELLS for p in ("first", "second")
              if not os.path.exists(f"{NULL_DIR}/{tag(*c, p)}.npy")]
print(f"   ontbrekende gepoolde nulverdelingen: {len(ontbrekend)}")

print("\n2. NaN en inf in de p-waardes")
slecht = [loc(r) for r in rows for k in ("p_trigger", "p_precursor", "p_mc_trigger")
          if not np.isfinite(r[k])]
print(f"   niet-eindige p-waardes: {len(slecht)}" + (f"  {slecht[:3]}" if slecht else ""))

print("\n3. Niet toetsbaar, nul droogtes of nul floods")
nt = collections.Counter()
for r in rows:
    if not r["testable"]:
        nt[cell(r)] += 1
if nt:
    for c, k in sorted(nt.items(), key=lambda x: -x[1])[:8]:
        wie = sorted({r["village"] for r in rows if cell(r) == c and not r["testable"]})
        print(f"   thr={c[0]:<5} fq={fmtq(c[1]):<6} win={c[2]:<3} {k:3} van 96   {', '.join(wie[:4])}")
else:
    print("   geen")
print(f"   totaal {sum(nt.values())} van {len(rows)} runs. Deze tellen NIET mee als")
print("   'niet significant': er valt niets te toetsen. In de gepoolde toets vallen")
print("   ze vanzelf weg, want ze dragen nul bij aan teller en noemer. Zie D-12")

print("\n4. Monotonie")
print("   Het AANDEEL WEKEN moet monotoon dalen: een strengere drempel kan een week")
print("   die er eerst onder viel er niet alsnog boven duwen. Dat is een bugsignaal.")
print("   Het AANTAL EVENTS hoeft dat NIET te zijn. Een event is een aaneengesloten")
print("   reeks weken, dus een strengere drempel kan een lang event in tweeen knippen")
print("   en dan gaat het aantal omhoog terwijl het aandeel weken omlaag gaat.")


def mono(veld, as_):
    """Aantal reeksen dat niet monotoon daalt, plus een voorbeeld."""
    schend, totaal, vb = 0, 0, None
    for p in ("first", "second"):
        for L in {loc(r) for r in rows}:
            d = {(r["threshold"], r["flood_quantile"]): r
                 for r in rows if loc(r) == L and r["period"] == p and r["match_window"] == BASE_WIN}
            vast, loopt = (FQS, THRS) if as_ == "threshold" else (THRS, FQS)
            for v in vast:
                reeks = [d[(x, v)][veld] if as_ == "threshold" else d[(v, x)][veld]
                         for x in loopt if ((x, v) if as_ == "threshold" else (v, x)) in d]
                totaal += 1
                if any(a < b - 1e-9 for a, b in zip(reeks, reeks[1:])):
                    schend += 1
                    if vb is None:
                        vb = f"{L[1]}/{p} bij {v:g}: {[round(x, 2) for x in reeks]}"
    return schend, totaal, vb


for veld, as_, label, bug in (
        ("pct_weeks_drought", "threshold", "aandeel droogteweken bij stijgende SRI-drempel", True),
        ("pct_weeks_flood", "flood_quantile", "aandeel floodweken bij stijgend floodpercentiel", True),
        ("drought_count", "threshold", "aantal droogte-events bij stijgende SRI-drempel", False),
        ("flood_count", "flood_quantile", "aantal flood-events bij stijgend floodpercentiel", False)):
    s, t, vb = mono(veld, as_)
    merk = ("  <-- FOUT, hoort 0 te zijn" if s and bug else
            "" if bug else "  <-- verwacht, geen fout")
    print(f"\n   {label}")
    print(f"     {s} van {t} reeksen niet monotoon dalend{merk}")
    if vb and not bug:
        print(f"     voorbeeld: {vb}")
print("\n   Die laatste twee zijn hetzelfde punt als in T-29: weken en events schalen")
print("   niet mee, en wie over selectiviteit schrijft moet ze uit elkaar houden.")

print("\n5. pct_weeks_flood tegen de nominale 100*(1-flood_quantile)")
print("   Het weekmaximum wordt tegen de dagelijkse verdeling uitgedrukt, dus dit")
print("   hoort systematisch te hoog te liggen. Dat is het effect uit D-11.")
for q in FQS:
    sub = [r["pct_weeks_flood"] for r in rows if r["flood_quantile"] == q and r["match_window"] == BASE_WIN]
    print(f"   fq={fmtq(q):<6} nominaal {100*(1-q):5.2f}%   gemeten mediaan {np.median(sub):5.2f}%"
          f"   {'te hoog' if np.median(sub) > 100*(1-q) else 'TE LAAG, onverwacht'}")

print("\n6. match_count_trigger tegen observed_matches_mc")
print("   Twee tellingen van hetzelfde uit twee stukken code, zie D-08")
af = sum(1 for r in rows if r["match_count_trigger"] != r["observed_matches_mc"])
print(f"   runs waar ze verschillen: {af}   (hoort 0 te zijn)")


# ------------------------------------------------------------ de gepoolde toets
def pooled(c, p):
    """Gepoolde trigger coincidence rate, Donges 2016 verg. 6, met zijn nulverdeling."""
    sub = [r for r in rows if cell(r) == c and r["period"] == p]
    num = sum(r["match_count_trigger"] for r in sub)
    den = sum(r["drought_count"] for r in sub)
    null = np.load(f"{NULL_DIR}/{tag(*c, p)}.npy")
    # Poisson-binomiale benadering als onafhankelijke controle op de Monte Carlo.
    # Per locatie: kans dat een droogte bij onafhankelijkheid door minstens één
    # flood wordt gevolgd, dan som van binomialen met ongelijke slaagkansen.
    mu = var = 0.0
    for r in sub:
        pk = 1 - (1 - c[2] / r["n_weeks"]) ** r["flood_count"]
        mu += r["drought_count"] * pk
        var += r["drought_count"] * pk * (1 - pk)
    return dict(
        num=num, den=den, rate=num / den if den else float("nan"),
        null_rate=null.mean() / den if den else float("nan"),
        ratio=num / null.mean() if null.mean() else float("nan"),
        z=(num - null.mean()) / null.std() if null.std() else float("nan"),
        p=float(np.mean(null >= num)),
        pb_mu=mu, pb_z=(num - mu) / var ** 0.5 if var else float("nan"),
        ongewogen=float(np.mean([r["match_count_trigger"] / r["drought_count"]
                                 for r in sub if r["testable"]])),
        n_sig=sum(1 for r in sub if r["testable"] and r["p_mc_trigger"] < ALPHA),
        n_nt=sum(1 for r in sub if not r["testable"]))


head("CONTROLE: MONTE CARLO TEGEN DE POISSON-BINOMIALE BENADERING")
print("\nDe gepoolde teller is een som van onafhankelijke binomialen met ongelijke")
print("slaagkansen. De twee mogen niet ver uiteenlopen, anders is er iets mis.\n")
print(f"{'cel':34} {'MC nullijn':>11} {'PB nullijn':>11} {'verschil':>9}")
print("-" * 70)
for c in PLANE[:5] + LINE:
    for p in ("first",):
        s = pooled(c, p)
        d = 100 * abs(s["null_rate"] * s["den"] - s["pb_mu"]) / s["pb_mu"]
        print(f"thr={c[0]:<5} fq={fmtq(c[1]):<6} win={c[2]:<3} {p:6} "
              f"{s['null_rate']*s['den']:11.1f} {s['pb_mu']:11.1f} {d:8.1f}%")


head("HOOFDTABEL: GEPOOLDE TOETS PER CEL")
print("\nrate is de gepoolde trigger coincidence rate, het aandeel droogtes dat binnen")
print("het venster door minstens één flood wordt gevolgd, over alle locaties samen.")
print("nullijn is diezelfde grootheid onder onafhankelijkheid. ratio is rate gedeeld")
print("door nullijn. sig is het aantal losse locaties met p < 0,05, alleen als")
print("naslag, de gepoolde p is de toets.\n")
for p in ("first", "second"):
    print(f"\nPERIODE {1 if p == 'first' else 2}")
    print(f"{'thr':>5} {'fq':>7} {'win':>4} | {'rate':>7} {'nullijn':>8} {'ratio':>6} "
          f"{'z':>7} {'p gepoold':>10} | {'ongew':>6} {'sig':>5} {'n.t.':>5}")
    print("-" * 88)
    for c in PLANE + LINE:
        s = pooled(c, p)
        ster = " *" if c == (BASE_THR, BASE_FQ, BASE_WIN) else "  "
        print(f"{c[0]:5} {fmtq(c[1]):>7} {c[2]:4} | {s['rate']:7.4f} {s['null_rate']:8.4f} "
              f"{s['ratio']:6.2f} {s['z']:7.1f} {pval(s['p']):>10} | {s['ongewogen']:6.3f} "
              f"{s['n_sig']:3}/48 {s['n_nt']:5}{ster}")
    print("  * baseline, de gepubliceerde configuratie")


head("VENSTERLIJN")
print("\nDe analytische ECA-p hangt mechanisch van het venster af via")
print("p_single = venster / totaal aantal weken, en de Monte Carlo krimpt de")
print("kandidatenpool met het venster. Daarom staat hier de gepoolde Monte Carlo")
print("voorop en niet de analytische p.\n")
print(f"{'venster':>8} {'periode':>8} {'rate':>8} {'nullijn':>8} {'ratio':>6} {'p gepoold':>10}")
print("-" * 54)
for c in sorted(set(LINE) | ({(BASE_THR, BASE_FQ, BASE_WIN)} & set(CELLS)), key=lambda c: c[2]):
    for p in ("first", "second"):
        s = pooled(c, p)
        print(f"{c[2]:8} {p:>8} {s['rate']:8.4f} {s['null_rate']:8.4f} "
              f"{s['ratio']:6.2f} {pval(s['p']):>10}")


head("WAAR HOUDT DE BEVINDING STAND")
houdt = [(c, p) for c in PLANE for p in ("first", "second") if pooled(c, p)["p"] < ALPHA]
print(f"\nGepoolde p < {ALPHA} in {len(houdt)} van de {len(PLANE)*2} cel-periodes van het vlak.")
valt = [(c, p) for c in PLANE for p in ("first", "second") if pooled(c, p)["p"] >= ALPHA]
if valt:
    print("Valt weg bij:")
    for c, p in valt:
        s = pooled(c, p)
        print(f"   thr={c[0]:<5} fq={fmtq(c[1]):<6} {p:6}  ratio {s['ratio']:.2f}, "
              f"p {pval(s['p'])}, {s['n_nt']} locaties niet toetsbaar")
else:
    print("Nergens. De bevinding houdt over het hele vlak stand.")
ALLE = [c for c in CELLS]
if len(ALLE) > len(PLANE):
    hn = [(c, p) for c in ALLE for p in ("first", "second") if pooled(c, p)["p"] < ALPHA]
    print(f"\nOver de volle kruising: gepoolde p < {ALPHA} in {len(hn)} van de "
          f"{len(ALLE)*2} cel-periodes.")
    print("\nPer venster, aantal cel-periodes van de 50 dat standhoudt:")
    for w in sorted({c[2] for c in ALLE}):
        sub = [c for c in ALLE if c[2] == w]
        k = sum(1 for c in sub for p in ("first", "second") if pooled(c, p)["p"] < ALPHA)
        rr = [pooled(c, p)["ratio"] for c in sub for p in ("first", "second")]
        print(f"   venster {w:2}: {k:3} van {len(sub)*2}   ratio van {min(rr):.2f} tot {max(rr):.2f}")

print("\nLET OP bij het opschrijven: de aggregatieve nulhypothese randomiseert elke")
print("locatie onafhankelijk. Onze locaties zijn dat niet, drie punten op de Dnieper,")
print("drie op de Don, Rijn en Maas onder dezelfde weersystemen. Echte ruimtelijke")
print("correlatie maakt de werkelijke nulvariantie groter dan de gesimuleerde, dus de")
print("gepoolde p valt te laag uit. Dit hoort als beperking in de tekst.")


# ------------------------------------------------------------- tabel voor T-17
os.makedirs(FIG_DIR, exist_ok=True)
uit = f"{GRID}/per_location_table.csv"
with open(uit, "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["threshold", "flood_quantile", "match_window", "period", "river", "village",
                "drought_count", "flood_count", "transitions", "p_mc_trigger", "testable"])
    for r in sorted(rows, key=lambda r: (r["threshold"], r["flood_quantile"],
                                         r["match_window"], r["period"], r["river"])):
        w.writerow([r["threshold"], r["flood_quantile"], r["match_window"], r["period"],
                    r["river"], r["village"], r["drought_count"], r["flood_count"],
                    r["match_count_trigger"], r["p_mc_trigger"], r["testable"]])
print(f"\n\nTabel per variant en per locatie geschreven naar {uit} ({len(rows)} regels).")
print("Dit is de invoer voor T-17.")


# ------------------------------------------------------------------- de figuur
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    print("\nmatplotlib niet beschikbaar, figuur overgeslagen.")
    sys.exit(0)

fig, axes = plt.subplots(1, 2, figsize=(13, 5.6), constrained_layout=True)
M = {p: np.array([[pooled((t, q, BASE_WIN), p)["ratio"] for t in THRS] for q in FQS])
     for p in ("first", "second")}
vmin = min(M[p].min() for p in M)
vmax = max(M[p].max() for p in M)

# Geen beschrijving in de figuur zelf. Die komt als caption onder de afbeelding te
# staan, zie figures/caption_en.md. Labels in het Engels, want het manuscript is dat.
for ax, p, titel in zip(axes, ("first", "second"), ("Period 1, 1995-2009", "Period 2, 2010-2024")):
    im = ax.imshow(M[p], cmap="YlGnBu", vmin=vmin, vmax=vmax, origin="lower", aspect="auto")
    for i, q in enumerate(FQS):
        for j, t in enumerate(THRS):
            s = pooled((t, q, BASE_WIN), p)
            kleur = "white" if (M[p][i, j] - vmin) / (vmax - vmin) > 0.6 else "black"
            # Het getal in het vakje is de ratio, dus dezelfde grootheid als de
            # kleur. De rate stond hier eerst, maar die loopt zichtbaar uit de pas
            # met de kleur: bij een strengere flooddrempel zakt de rate hard terwijl
            # de nullijn meezakt, en dan leest een laag getal als een zwak effect
            # terwijl de samenhang even sterk is. De rate staat in de hoofdtabel.
            ax.text(j, i, f"{s['ratio']:.2f}\np {pval(s['p'])}", ha="center",
                    va="center", fontsize=8.5, color=kleur)
            if (t, q) == (BASE_THR, BASE_FQ):
                ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                           edgecolor="crimson", lw=2.5))
    ax.set_xticks(range(len(THRS))); ax.set_xticklabels([f"{t:g}" for t in THRS])
    ax.set_yticks(range(len(FQS))); ax.set_yticklabels([fmtq(q) for q in FQS])
    ax.set_xlabel("Drought threshold (SRI)")
    ax.set_ylabel("Flood threshold (runoff quantile)")
    ax.set_title(titel, fontsize=11)

cb = fig.colorbar(im, ax=axes, shrink=0.85)
cb.set_label("Coincidence ratio (observed / expected)")
pad = f"{FIG_DIR}/sensitivity_heatmap.png"
fig.savefig(pad, dpi=200)
print(f"Figuur geschreven naar {pad}")
plt.close(fig)

# --------------------------------------------- tweede figuur: raster per venster
WINS = sorted({c[2] for c in CELLS})
VOL = all((t, q, w) in CELLS for t in THRS for q in FQS for w in WINS)
if not VOL:
    print("Volle kruising nog niet compleet, tweede figuur overgeslagen.")
    sys.exit(0)

from matplotlib.colors import LogNorm

R = {(p, w): np.array([[pooled((t, q, w), p)["ratio"] for t in THRS] for q in FQS])
     for p in ("first", "second") for w in WINS}
# Logaritmische kleurschaal. De ratio is een verhouding, dus 2,0 en 0,5 liggen even
# ver van 1,0 af. Lineair zou het paneel bij venster 4 verbleken zodra venster 1 de
# bovenkant van de schaal oprekt, en dat is precies het paneel dat ertoe doet.
norm = LogNorm(vmin=min(m.min() for m in R.values()), vmax=max(m.max() for m in R.values()))

fig, axes = plt.subplots(2, len(WINS), figsize=(4.3 * len(WINS), 9.2),
                         constrained_layout=True)
for ri, p in enumerate(("first", "second")):
    for ci, w in enumerate(WINS):
        ax = axes[ri, ci]
        Z = R[(p, w)]
        im = ax.imshow(Z, cmap="YlGnBu", norm=norm, origin="lower", aspect="auto")
        for i, q in enumerate(FQS):
            for j, t in enumerate(THRS):
                sc = pooled((t, q, w), p)
                kl = "white" if norm(Z[i, j]) > 0.55 else "black"
                # Ratio boven, p eronder. De arcering blijft ernaast staan: die
                # geeft het patroon in één oogopslag, de p geeft het getal.
                ax.text(j, i + 0.13, f"{Z[i, j]:.2f}", ha="center", va="center",
                        fontsize=8, color=kl)
                ax.text(j, i - 0.19, f"p {pval(sc['p'])}", ha="center", va="center",
                        fontsize=5.8, color=kl)
                if sc["p"] >= ALPHA:
                    # Niet significant. Arcering licht en dun houden, anders loopt
                    # hij dwars door de p-waarde heen en is die niet meer te lezen.
                    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                               edgecolor="0.45", lw=0, hatch="\\\\",
                                               alpha=0.45))
                if (t, q, w) == (BASE_THR, BASE_FQ, BASE_WIN):
                    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                               edgecolor="crimson", lw=2.2))
        ax.set_xticks(range(len(THRS))); ax.set_yticks(range(len(FQS)))
        ax.set_xticklabels([f"{t:g}" for t in THRS], fontsize=8)
        ax.set_yticklabels([fmtq(q) for q in FQS] if ci == 0 else [], fontsize=8)
        if ri == 0:
            ax.set_title(f"{w}-week window", fontsize=10)
        if ri == len(("first", "second")) - 1:
            ax.set_xlabel("Drought threshold (SRI)", fontsize=8)
        if ci == 0:
            ax.set_ylabel(f"{'Period 1' if p == 'first' else 'Period 2'}\n"
                          "Flood threshold (quantile)", fontsize=8)
cb = fig.colorbar(im, ax=axes, shrink=0.6, ticks=[0.5, 0.75, 1, 1.5, 2, 3])
cb.ax.set_yticklabels(["0.5", "0.75", "1", "1.5", "2", "3"])
cb.set_label("Coincidence ratio (observed / expected), log scale")
pad2 = f"{FIG_DIR}/sensitivity_by_window.png"
fig.savefig(pad2, dpi=170)
print(f"Figuur geschreven naar {pad2}")
print("  hatch = niet significant bij alpha " + str(ALPHA) + ", rode rand = gepubliceerde configuratie")
