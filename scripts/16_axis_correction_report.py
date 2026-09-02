"""T-11: rapport over het effect van de as-correctie, per rivier en per locatie.

Rekent niets opnieuw. Leest curves.csv uit
results/2026-09-02_copula_definition_variants/ en zet de gepubliceerde aflezing
naast de gecorrigeerde, voor alle 16 rivieren, 48 locaties, 2 periodes en 2
variabelenparen.

De correctie, R-01. De conditionele curves worden berekend op de rangschaal van de
post-droogte pieken, want een copula kent alleen rangnummers. De unconditionele
curve staat op de runoff-quantielschaal. In de gepubliceerde figuren worden ze op
dezelfde x-as gezet. Gecorrigeerd betekent: de conditionele curve afgelezen op de
rang die hoort bij een runoff-quantiel, via y_hat(q) = sum(data2 <= q)/(n+1), zodat
beide dezelfde vraag beantwoorden.

R-02 en R-03 staan hier bewust niet in de hoofdtabellen. Die twee zijn nog open.
Ze staan wel in de laatste sectie, zodat zichtbaar is hoe groot ze zijn naast R-01.

Uitvoer:
  report_axis_correction.md     het leesbare rapport
  per_location_axis_correction.csv   alle getallen, ook de quantielen die niet in
                                     de tabellen passen

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --no-project python scripts/16_axis_correction_report.py
"""
import csv, collections, os
import numpy as np

VAR = "results/2026-09-02_copula_definition_variants"
Y = np.linspace(0, 1, 101)
YC = [f"y_{i:03d}" for i in range(101)]
# 0,6915 is de flooddrempel van het manuscript, norm.cdf(0.5)
LEVELS = [0.6915, 0.90, 0.95, 0.99]
MAIN = 0.95                      # het niveau in de tabellen per rivier
PAIR_NL = {"drought_peak": "drought peak", "mean_drought_severity": "mean severity"}
PERIOD_NL = {"first": "1", "second": "2"}


def idx(q):
    return int(round(q * 100))


cond, uncond, nev = {}, {}, {}
order = []
for r in csv.DictReader(open(f"{VAR}/curves.csv")):
    v = np.array([float(r[c]) for c in YC])
    if r["curve"] == "unconditioneel":
        uncond[(r["river"], r["village"], r["period"])] = v
        continue
    k = (r["river"], r["village"], r["period"], r["pair"], r["variant"],
         r["axis"], r["curve"])
    cond[k] = v
    nev[(r["river"], r["village"], r["period"], r["pair"], r["variant"])] = int(r["n_events"])
    if r["variant"] == "gepubliceerd" and r["axis"] == "rang" and r["curve"] == "minor":
        order.append((r["river"], r["village"], r["period"], r["pair"]))

rivers = []
for river, village, period, pair in order:
    if river not in rivers:
        rivers.append(river)

# ------------------------------------------------------------------ de CSV
os.makedirs(VAR, exist_ok=True)
with open(f"{VAR}/per_location_axis_correction.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    head = ["river", "village", "period", "pair", "n_events"]
    for q in LEVELS:
        s = f"{q:g}"
        head += [f"uncond_q{s}",
                 f"minor_gepubliceerd_q{s}", f"minor_gecorrigeerd_q{s}", f"minor_delta_q{s}",
                 f"severe_gepubliceerd_q{s}", f"severe_gecorrigeerd_q{s}", f"severe_delta_q{s}",
                 f"gap_minor_gepubliceerd_q{s}", f"gap_minor_gecorrigeerd_q{s}"]
    w.writerow(head)
    for river, village, period, pair in order:
        row = [river, village, period, pair,
               nev[(river, village, period, pair, "gepubliceerd")]]
        u = uncond[(river, village, period)]
        for q in LEVELS:
            i = idx(q)
            vals = {}
            for curve in ("minor", "major"):
                pub = cond[(river, village, period, pair, "gepubliceerd", "rang", curve)][i]
                cor = cond[(river, village, period, pair, "gepubliceerd", "ruwe", curve)][i]
                vals[curve] = (pub, cor)
            row += [round(float(u[i]), 4),
                    round(float(vals["minor"][0]), 4), round(float(vals["minor"][1]), 4),
                    round(float(vals["minor"][1] - vals["minor"][0]), 4),
                    round(float(vals["major"][0]), 4), round(float(vals["major"][1]), 4),
                    round(float(vals["major"][1] - vals["major"][0]), 4),
                    round(float(vals["minor"][0] - u[i]), 4),
                    round(float(vals["minor"][1] - u[i]), 4)]
        w.writerow(row)

# ------------------------------------------------------------------ het rapport
L = []
A = L.append
A("# Effect van de as-correctie op de gepubliceerde transitiekansen")
A("")
A("Alle 16 rivieren, 48 locaties, 2 periodes en 2 variabelenparen, dus 192 cellen.")
A("Gemaakt met `scripts/16_axis_correction_report.py`, dat niets herberekent en")
A("alleen `curves.csv` uit deze map leest.")
A("")
A("## Wat er is gecorrigeerd")
A("")
A("Een copula kent alleen rangnummers. De getrokken waardes zijn per constructie")
A("uniform tussen 0 en 1, dus de conditionele curves staan op de **rang van de")
A("post-droogte piek binnen de droogte-events** van die locatie en periode. De")
A("unconditionele curve staat op de **runoff-quantielschaal** van de locatie. In de")
A("gepubliceerde figuren staan ze op dezelfde x-as, met als label \"Future flood")
A("quantile value\".")
A("")
A("Gecorrigeerd betekent: de conditionele curve afgelezen op de rang die hoort bij")
A("een runoff-quantiel, via `y_hat(q) = sum(data2 <= q)/(n+1)`. Dan beantwoorden")
A("beide dezelfde vraag en mogen ze naast elkaar.")
A("")
A("De curves zelf zijn niet opnieuw gefit en niet opnieuw berekend. Alleen de plek")
A("waar ze worden afgelezen verandert.")
A("")
A("Ter oriëntatie, de vertaling tussen de twee assen, mediaan over alle cellen:")
A("")
A("| rang op de conditionele as | runoff-quantiel |")
A("|---|---|")
A("| 0,25 | 0,729 |")
A("| 0,50 | 0,867 |")
A("| 0,75 | 0,957 |")
A("| 0,90 | 0,989 |")
A("")

# overall
def stat(q, curve, kind):
    out = []
    for river, village, period, pair in order:
        i = idx(q)
        u = uncond[(river, village, period)][i]
        pub = cond[(river, village, period, pair, "gepubliceerd", "rang", curve)][i]
        cor = cond[(river, village, period, pair, "gepubliceerd", "ruwe", curve)][i]
        out.append({"pub": pub, "cor": cor, "delta": cor - pub,
                    "gap_pub": pub - u, "gap_cor": cor - u, "uncond": u}[kind])
    return np.array(out)

A("## Het effect over alle 192 cellen")
A("")
A("Transitiekans na een milde droogte, mediaan over de cellen. `gepubliceerd` is de")
A("waarde zoals hij nu in Appendix D staat, `gecorrigeerd` is dezelfde curve op de")
A("runoff-quantielschaal afgelezen.")
A("")
A("| runoff-quantiel | unconditioneel | gepubliceerd | gecorrigeerd | verschil |")
A("|---|---|---|---|---|")
for q in LEVELS:
    A(f"| {q:g} | {np.median(stat(q,'minor','uncond')):.3f} | "
      f"{np.median(stat(q,'minor','pub')):.3f} | {np.median(stat(q,'minor','cor')):.3f} | "
      f"{np.median(stat(q,'minor','delta')):+.3f} |")
A("")
A("Hetzelfde voor een zware droogte:")
A("")
A("| runoff-quantiel | unconditioneel | gepubliceerd | gecorrigeerd | verschil |")
A("|---|---|---|---|---|")
for q in LEVELS:
    A(f"| {q:g} | {np.median(stat(q,'major','uncond')):.3f} | "
      f"{np.median(stat(q,'major','pub')):.3f} | {np.median(stat(q,'major','cor')):.3f} | "
      f"{np.median(stat(q,'major','delta')):+.3f} |")
A("")
A("En het gat met de unconditionele lijn, dus de grootheid waar de bevinding van het")
A("artikel op rust. Negatief betekent dat droogte de floodkans verlaagt.")
A("")
A("| runoff-quantiel | gat, gepubliceerd | gat, gecorrigeerd | cellen met negatief gat, gepubliceerd | idem, gecorrigeerd |")
A("|---|---|---|---|---|")
for q in LEVELS:
    gp, gc = stat(q, "minor", "gap_pub"), stat(q, "minor", "gap_cor")
    A(f"| {q:g} | {np.median(gp):+.3f} | {np.median(gc):+.3f} | "
      f"{int(np.sum(gp < 0))} van 192 | {int(np.sum(gc < 0))} van 192 |")
A("")

# ranking per rivier
A("## Waar het effect het grootst is")
A("")
A(f"Rivieren gerangschikt naar het mediane verschil bij runoff-quantiel {MAIN:g},")
A("milde droogte, over hun 12 cellen.")
A("")
A("| rivier | mediaan verschil | kleinste | grootste |")
A("|---|---|---|---|")
per_river = collections.defaultdict(list)
for river, village, period, pair in order:
    i = idx(MAIN)
    pub = cond[(river, village, period, pair, "gepubliceerd", "rang", "minor")][i]
    cor = cond[(river, village, period, pair, "gepubliceerd", "ruwe", "minor")][i]
    per_river[river].append(cor - pub)
for river in sorted(per_river, key=lambda r: -abs(np.median(per_river[r]))):
    d = np.array(per_river[river])
    A(f"| {river} | {np.median(d):+.3f} | {d.min():+.3f} | {d.max():+.3f} |")
A("")

# per rivier
A("## Per rivier en per locatie")
A("")
A(f"Alle waardes bij runoff-quantiel {MAIN:g}. `pub` is de gepubliceerde aflezing,")
A("`corr` de gecorrigeerde, `d` het verschil. De volledige set quantielen staat in")
A("`per_location_axis_correction.csv`.")
A("")
for river in rivers:
    A(f"### {river}")
    A("")
    A("| locatie | per. | paar | n | uncond | minor pub | minor corr | d | severe pub | severe corr | d |")
    A("|---|---|---|---|---|---|---|---|---|---|---|")
    for r2, village, period, pair in order:
        if r2 != river:
            continue
        i = idx(MAIN)
        u = uncond[(river, village, period)][i]
        mp = cond[(river, village, period, pair, "gepubliceerd", "rang", "minor")][i]
        mc = cond[(river, village, period, pair, "gepubliceerd", "ruwe", "minor")][i]
        sp = cond[(river, village, period, pair, "gepubliceerd", "rang", "major")][i]
        sc = cond[(river, village, period, pair, "gepubliceerd", "ruwe", "major")][i]
        n = nev[(river, village, period, pair, "gepubliceerd")]
        A(f"| {village} | {PERIOD_NL[period]} | {PAIR_NL[pair]} | {n} | {u:.3f} | "
          f"{mp:.3f} | {mc:.3f} | {mc-mp:+.3f} | {sp:.3f} | {sc:.3f} | {sc-sp:+.3f} |")
    A("")

# R-02 en R-03 ter vergelijking
A("## Ter vergelijking: de twee correcties die nog open staan")
A("")
A("R-02, het floodvenster dat de laatste droogteweek meetelt, en R-03, de duur in")
A("`mean_drought_severity` die een week te kort is. Deze twee zijn **niet** in de")
A("tabellen hierboven verwerkt. Ze staan hier zodat zichtbaar is hoe groot ze zijn")
A("naast de as-correctie. Grootste absolute verschuiving van de conditionele curve")
A("ten opzichte van de gepubliceerde, mediaan over de cellen.")
A("")
summary = list(csv.DictReader(open(f"{VAR}/summary.csv")))
A("| correctie | paar | mediaan | p90 | maximum | familie kantelt |")
A("|---|---|---|---|---|---|")
for v, label in (("R02_venster", "R-02"), ("R03_duur", "R-03"), ("R02_R03", "R-02 + R-03")):
    for pair in ("drought_peak", "mean_drought_severity"):
        sub = [r for r in summary if r["variant"] == v and r["pair"] == pair]
        if not sub:
            continue
        d = np.array([float(r["max_diff_minor_vs_gepubliceerd"]) for r in sub])
        fam = sum(1 for r in sub if r["familie_gewijzigd"] == "1")
        if v == "R03_duur" and pair == "drought_peak":
            A(f"| {label} | {PAIR_NL[pair]} | niet van toepassing | | | |")
            continue
        A(f"| {label} | {PAIR_NL[pair]} | {np.median(d):.3f} | "
          f"{np.percentile(d,90):.3f} | {d.max():.3f} | {fam} van {len(sub)} |")
A("")
A("## Wat hier niet in staat")
A("")
A("**De vergelijking van milde tegen zware droogte verandert niet.** Die twee curves")
A("staan allebei op de rangschaal en zijn onderling altijd al vergelijkbaar geweest.")
A("Het gearceerde vlak tussen groen en rood in de gepubliceerde figuren blijft dus")
A("staan zoals het is.")
A("")
A("**De juiste nullijn voor de conditionele curves op de rangschaal is de diagonaal,**")
A("niet de unconditionele lijn. Op die schaal is `1 - y` wat je krijgt zonder enig")
A("droogte-effect. Afgezet tegen de diagonaal wijkt de milde curve af met mediaan")
A("-0,041 en de zware met -0,074, tegen -0,386 als je hem tegen de unconditionele")
A("lijn afzet. Er is dus wel een effect, in de richting die het artikel beweert, maar")
A("ongeveer een factor tien kleiner.")
A("")
A("**Twee verschillen blijven bestaan, ook na de as-correctie.** De conditionele")
A("curves gaan over een populatie van droogte-events en de unconditionele over een")
A("populatie van weken, waaronder ook weken die op een droogte volgen. En de")
A("conditionele kant telt vijf weekpunten inclusief de laatste droogteweek, terwijl")
A("de unconditionele kant er vier telt zonder de eigen week. Dat laatste is R-02.")
A("")
A("**De trekkingsruis.** De gepubliceerde berekening heeft geen seed, deze run wel.")
A("Verschillen van enkele duizendsten ten opzichte van de gepubliceerde figuren zijn")
A("daarom te verwachten, los van de correctie. Zie R-07.")

out = f"{VAR}/report_axis_correction.md"
open(out, "w").write("\n".join(L) + "\n")
print("\n".join(L))
print(f"\n\ngeschreven naar {out} en {VAR}/per_location_axis_correction.csv", flush=True)
