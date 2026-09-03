"""T-11: het eindrapport. Intervallen, onafhankelijkheidstoetsen en copulakeuze.

Rekent niets opnieuw. Leest drie resultaatmappen en schrijft report.md:
  results/2026-09-02_copula_bootstrap/     intervallen, diagnostiek, selectie
  results/2026-09-02_dependence_tests/     de vier onafhankelijkheidstoetsen
  (beide op de gerepareerde einddetectie, commit 23429e1, parametrische marginalen)

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --no-project python scripts/23_bootstrap_report.py
"""
import csv, collections, os
import numpy as np

BS = "results/2026-09-02_copula_bootstrap"
DEP = "results/2026-09-02_dependence_tests/dependence_tests.csv"
Y = np.linspace(0, 1, 101)
YC = [f"y_{i:03d}" for i in range(101)]
QM = 69
NIVEAUS = [(69, "0,69"), (90, "0,90"), (95, "0,95")]
PAIR_NL = {"drought_peak": "drought peak", "mean_drought_severity": "mean severity"}
PER_NL = {"first": "1", "second": "2"}
KOLS = ("tau_p", "hoeffd_p", "aic_perm_p", "cp_q6915_p")

ci = {}
for r in csv.DictReader(open(f"{BS}/transition_ci.csv")):
    ci[(r["river"], r["village"], r["period"], r["pair"], r["scheme"],
        r["quantity"], r["kind"])] = np.array([float(c) for c in (r[k] for k in YC)])
diag = {}
for r in csv.DictReader(open(f"{BS}/bootstrap_diagnostics.csv")):
    diag[(r["river"], r["village"], r["period"], r["pair"], r["scheme"])] = r
dep = {}
for r in csv.DictReader(open(DEP)):
    dep[(r["river"], r["village"], r["period"], r["pair"])] = r
cellen = sorted({k[:4] for k in ci if k[4] == "iid"})
iid = [diag[c + ("iid",)] for c in cellen if c + ("iid",) in diag]
print(f"cellen: {len(cellen)}, toetsen: {len(dep)}", flush=True)


def w(cel, q, soort, j=QM, scheme="iid"):
    k = cel + (scheme, q, soort)
    return float(ci[k][j]) if k in ci else np.nan


def sluit_nul_uit(cel, q, j=QM):
    lo, hi = w(cel, q, "lo", j), w(cel, q, "hi", j)
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return None
    return "pos" if lo > 0 else ("neg" if hi < 0 else "nul")


def n_toetsen(cel):
    d = dep.get(cel)
    return sum(1 for k in KOLS if d and float(d[k]) < 0.05), d


def fmt_ci(cel, q, j=QM):
    p, lo, hi = w(cel, q, "point", j), w(cel, q, "lo", j), w(cel, q, "hi", j)
    if not np.isfinite(p):
        return "geen"
    ster = "**" if (lo > 0 or hi < 0) else ""
    return f"{ster}{p:+.3f}{ster} [{lo:+.3f}, {hi:+.3f}]"


L = []
A = L.append
A("# T-11 eindrapport: copulakeuze en betrouwbaarheid van de transitiekansen")
A("")
A("Antwoord op reviewerpunt R4-03, beide helften, plus de vervolgvraag of de")
A("copula's echt zo weinig betekenis hebben. Alles hieronder is berekend op de")
A("gerepareerde eventdefinities van 2 september: einddetectie, duur als telling,")
A("floodvenster strikt na het event, F_Y toegepast, parametrische marginalen.")
A("Gemaakt met `scripts/23_bootstrap_report.py`, dat alleen bestaande uitvoer leest.")
A("")
A("## Hoe dit rapport te lezen")
A("")
A("Drie instrumenten, elk met een eigen vraag.")
A("")
A("**De permutatietoetsen** vragen: bestaat de samenhang tussen droogtezwaarte en de")
A("piek erna, of is het toeval. Vier toetsen per cel: Kendall tau en Spearman rho")
A("(monotone samenhang), Hoeffding D (ook niet-monotoon), en een permutatietoets op")
A("de copulafit zelf waarbij de selectie over vijftien families in de nulverdeling")
A("zit. Een cel telt hieronder als **sterk** wanneer minstens drie van de vier onder")
A("p 0,05 komen.")
A("")
A("**De bootstrap-intervallen** vragen: hoe groot is het effect en hoe onzeker. 2000")
A("replicaties per cel, waarbij elke keer de hele keten opnieuw wordt gedaan,")
A("inclusief de copulakeuze. 95 procent, percentiel, puntsgewijs.")
A("")
A("**De opsplitsing** haalt uit elkaar wat vaak door elkaar loopt: het *marginale*")
A("deel, is het venster na een droogte natter dan een willekeurig venster, en het")
A("*copula*-deel, hangt de hoogte van de piek samen met de zwaarte van de droogte.")
A("Alleen dat tweede is waar een copula voor dient, en alleen dat tweede staat")
A("hieronder centraal.")
A("")

# ------------------------------------------------ 1. sterke associaties
A("## 1. Waar is de samenhang sterk, en welke kant op")
A("")
sterk = []
for cel in cellen:
    ns, d = n_toetsen(cel)
    if d and ns >= 3:
        sterk.append((cel, ns, d))
A(f"Van de {len(cellen)} cellen halen er **{len(sterk)}** drie of vier van de vier")
A("toetsen. Gerangschikt op de sterkte van de samenhang (tau):")
A("")
A("| rivier | locatie | periode | variabele | richting | tau | copula-deel bij 0,69 | zwaar min mild bij 0,69 | toetsen |")
A("|---|---|---|---|---|---|---|---|---|")
for cel, ns, d in sorted(sterk, key=lambda x: -abs(float(x[2]["tau"]))):
    tau = float(d["tau"])
    richting = "verhoogt" if tau > 0 else "verlaagt"
    A(f"| {cel[0]} | {cel[1]} | {PER_NL[cel[2]]} | {PAIR_NL[cel[3]]} | {richting} | "
      f"{tau:+.3f} | {fmt_ci(cel, 'copula_part')} | {fmt_ci(cel, 'diff_resel')} | {ns}/4 |")
A("")
A("Vet betekent dat het 95 procent interval nul uitsluit. \"Richting\" leest als: een")
A("zwaardere droogte *verhoogt* dan wel *verlaagt* de kans op een hoge piek erna.")
A("")
pos = [s for s in sterk if float(s[2]["tau"]) > 0]
neg = [s for s in sterk if float(s[2]["tau"]) < 0]
A(f"Het beeld splitst in twee clusters. **Positief**, {len(pos)} cellen: de zuidelijke")
A("rivieren, met Po Piacenza in beide periodes, Ebro en Tagus in periode 2, en Danube")
A(f"Aschach in periode 1. **Negatief**, {len(neg)} cellen: Centraal-Europa in periode 1,")
A("Vistula en Weser. Daar geeft een zwaardere droogte een lagere kans op een hoge")
A("piek, wat past bij een uitgedroogde bodem die de eerste neerslag opvangt. Dat")
A("negatieve cluster staat nu nergens in het artikel en is materiaal voor R4-04.")
A("")
twee = sum(1 for cel in cellen if (lambda x: x[1] and x[0] == 2)(n_toetsen(cel)))
A(f"Daarnaast halen {twee} cellen twee van de vier toetsen. De overige cellen zijn")
A("niet van toeval te onderscheiden.")
A("")
A("### Over heel Europa gewogen")
A("")
taus = [float(dep[c]["tau"]) for c in cellen if c in dep]
ps = [float(dep[c]["tau_p"]) for c in cellen if c in dep]
sig = sum(1 for p in ps if p < 0.05)
A(f"Over alle {len(taus)} cellen: {sig} significant op tau tegen {len(taus)*0.05:.1f}")
A(f"verwacht bij puur toeval, mediaan tau {np.median(taus):+.3f}, positief in")
A(f"{sum(1 for t in taus if t>0)} van de {len(taus)}. Geen enkele cel overleeft een")
A("FDR-correctie over alle cellen tegelijk. De juiste lezing: er is geen breed")
A("Europees severity-effect, er zijn specifieke plekken waar het echt is. Voor")
A("locaties die het artikel al aanwijst, Po en Ebro, is de ongecorrigeerde p het")
A("relevante bewijs, want de correctie hoort bij zoeken over de hele kaart.")
A("")

# ------------------------------------------------ 2. copulakeuze
A("## 2. De copulakeuze en hoe hard hij staat")
A("")
A("Dit is de eerste helft van R4-03. Per cel is de familie gekozen met AIC over")
A("vijftien kandidaten, zoals het manuscript beschrijft. De volledige tabel per")
A("locatie en variabelenpaar staat in `bootstrap_diagnostics.csv` en is als")
A("appendixtabel klaar te zetten.")
A("")
cnt = collections.Counter(r["copula_point"] for r in iid)
A("| familie | gekozen in | familie | gekozen in |")
A("|---|---|---|---|")
fams = cnt.most_common()
for i in range(0, len(fams), 2):
    l = f"| {fams[i][0]} | {fams[i][1]} "
    l += f"| {fams[i+1][0]} | {fams[i+1][1]} |" if i + 1 < len(fams) else "| | |"
    A(l)
A("")
sh = np.array([float(r["modal_share"]) for r in iid])
nf = np.array([int(r["n_families_seen"]) for r in iid])
same = sum(1 for r in iid if r["copula_point"] == r["copula_modal"])
A("**Hoe betrouwbaar is die keuze.** Over de 2000 bootstrap-replicaties per cel:")
A("")
A(f"- de familie die op de volle steekproef wint komt in {same} van de {len(iid)}")
A("  cellen ook als meest gekozen familie terug")
A(f"- maar de mediane frequentie van die winnaar is **{np.median(sh):.0%}**, met")
A(f"  kwartielen {np.percentile(sh,25):.0%} en {np.percentile(sh,75):.0%}")
A(f"- het mediane aantal verschillende families dat over de replicaties gekozen")
A(f"  wordt is **{int(np.median(nf))}** van de vijftien, maximum {nf.max()}")
A("")
A("De keuze welke familie is dus zelden hard. Dat is geen ramp voor de")
A("transitiekansen, want de intervallen hieronder herselecteren de familie per")
A("replicatie en dragen die onzekerheid dus al in zich. Maar het hoort wel zo in het")
A("artikel: niet alleen welke familie won, ook dat de marge klein is.")
A("")

# ------------------------------------------------ 3. intervallen
A("## 3. De betrouwbaarheidsintervallen")
A("")
br = np.array([float(r["median_width_minor"]) for r in iid])
A(f"Mediane breedte van het 95 procent interval rond de milde curve: **{np.median(br):.3f}**,")
A(f"kwartielen {np.percentile(br,25):.3f} tot {np.percentile(br,75):.3f}. Ter")
A("vergelijking: de as-correctie van eerder deze week verschoof diezelfde curve met")
A("ongeveer 0,5 bij het floodniveau van het manuscript. De gerepareerde fout was dus")
A("ruwweg drie tot vier keer zo groot als de onzekerheid die eromheen zit.")
A("")
A("Waar sluit het interval nul uit, per floodniveau:")
A("")
A("| grootheid | niveau | boven nul | onder nul | bevat nul |")
A("|---|---|---|---|---|")
for q, lab in (("marginal_part", "marginaal deel"), ("copula_part", "copula-deel"),
               ("diff_resel", "zwaar min mild")):
    for j, jl in NIVEAUS:
        u = [sluit_nul_uit(c, q, j) for c in cellen]
        u = [x for x in u if x]
        A(f"| {lab} | {jl} | {u.count('pos')} van {len(u)} | {u.count('neg')} van {len(u)} | {u.count('nul')} van {len(u)} |")
A("")
A("Het marginale deel is de stevigste bevinding: op ongeveer een derde van de")
A("locaties is het venster na een droogte aantoonbaar natter dan een willekeurig")
A("venster, vrijwel altijd in de positieve richting. Dat is dezelfde bevinding als")
A("de ECA-kant, langs een andere weg. Het copula-deel en het verschil zwaar-mild")
A("halen op de meeste plekken geen significantie, met de clusters uit sectie 1 als")
A("uitzondering.")
A("")

# ------------------------------------------------ 4. Ebro en Po detail
A("## 4. Ebro en Po, de rivieren van het artikel")
A("")
A("Bij het floodniveau van het manuscript, quantiel 0,69. Vet sluit nul uit.")
A("")
for riv in ("Po", "Ebro"):
    A(f"### {riv}")
    A("")
    A("| locatie | per. | variabele | n | copula | stabiliteit | copula-deel | zwaar min mild | toetsen <0,05 |")
    A("|---|---|---|---|---|---|---|---|---|")
    for cel in [c for c in cellen if c[0] == riv]:
        d = diag.get(cel + ("iid",), {})
        ns, dd = n_toetsen(cel)
        A(f"| {cel[1]} | {PER_NL[cel[2]]} | {PAIR_NL[cel[3]]} | {d.get('n_events','')} | "
          f"{d.get('copula_point','')} | {float(d.get('modal_share',0)):.0%} | "
          f"{fmt_ci(cel,'copula_part')} | {fmt_ci(cel,'diff_resel')} | {ns}/4 |")
    A("")

# ------------------------------------------------ 5. wat het artikel raakt
A("## 5. Wat dit betekent voor de uitspraken in het artikel")
A("")
def cel_info(riv, vil, per, pair):
    cel = (riv, vil, per, pair)
    ns, d = n_toetsen(cel)
    return cel, ns, d
A("| passage | uitspraak | wat de toetsen nu zeggen |")
A("|---|---|---|")
cel, ns, d = cel_info("Po", "Piacenza", "second", "drought_peak")
cel1, ns1, d1 = cel_info("Po", "Piacenza", "first", "drought_peak")
A(f"| p27 | Po: zwaardere droogte geeft hogere kans, alleen periode 2 | de samenhang is echt, maar in **beide** periodes: periode 1 {ns1}/4 toetsen, periode 2 {ns}/4. \"Only during the second period\" klopt niet meer |")
cel, ns, d = cel_info("Ebro", "Tudela", "first", "drought_peak")
cel2, ns2, d2 = cel_info("Ebro", "Tudela", "second", "drought_peak")
A(f"| p28 | Ebro midstream: hogere kans in beide periodes (drought peak) | mager: periode 1 {ns}/4, periode 2 {ns2}/4 toetsen. Het echte Ebro-signaal zit bij **mean severity in periode 2**, Haro 4/4 en Tudela 3/4 |")
A(f"| p27, p28, p30 | conditioneel blijft lager dan unconditioneel | vervalt, dat was de as-fout. Na correctie ligt de conditionele curve op of licht boven de unconditionele |")
A(f"| p31 | Dnieper Krementsjoek en Dnipro als regio met verhoogde kans | niet toetsbaar op deze data: te weinig droogte-events voor een bootstrap (11 tot 19). Terughoudend formuleren |")
cel, ns, d = cel_info("Tagus", "La Bazagona", "second", "drought_peak")
A(f"| p31 | Tagus La Bazagona, lichte toename in periode 1 | de toetsen vinden La Bazagona juist in **periode 2**, {ns}/4 voor drought peak en 4/4 voor mean severity, het op een na sterkste punt van de kaart |")
A(f"| p34 | robuuste systemen: Po en Ebro | houdt stand en wordt sterker: Po Piacenza en Ebro periode 2 zijn nu met vier onafhankelijke toetsen onderbouwd. Tagus La Bazagona hoort in dat rijtje thuis |")
A("")
A("En de bevinding die er nog niet in staat: het negatieve cluster. Vistula Turon en")
A("Weser in periode 1, waar zwaardere droogte de kans verlaagt. Dat is fysisch")
A("interpreteerbaar, bodemvochtdeficit dat de eerste neerslag bufffert, en het is")
A("precies het soort mechanisme waar R4-04 om vraagt.")
A("")

# ------------------------------------------------ 6. controles
A("## 6. Controles en diagnostiek")
A("")
lag = np.array([abs(float(r["lag1_spearman_drought"])) for r in iid
                if r["lag1_spearman_drought"] not in ("", "nan")])
ratio = []
for r in iid:
    b = diag.get((r["river"], r["village"], r["period"], r["pair"], "block"))
    if b and float(r["median_width_minor"]) > 0:
        ratio.append(float(b["median_width_minor"]) / float(r["median_width_minor"]))
ratio = np.array(ratio)
bias = np.array([float(r["median_bias"]) for r in iid])
fails = np.array([int(r["failed_replicates"]) for r in iid])
supt = np.array([float(r["supt_over_196"]) for r in iid])
A(f"- **Seriele afhankelijkheid.** Lag-1 correlatie tussen opeenvolgende droogtes:")
A(f"  mediaan {np.median(lag):.3f} absoluut, maximum {lag.max():.3f}. De circulaire")
A(f"  blokbootstrap geeft intervallen die mediaan {np.median(ratio):.2f} keer zo breed")
A(f"  zijn als de gewone, kwartielen {np.percentile(ratio,25):.2f} en")
A(f"  {np.percentile(ratio,75):.2f}. De iid-intervallen zijn dus niet merkbaar te smal")
A(f"- **Bias.** Mediane afwijking tussen bootstrapmediaan en puntschatting")
A(f"  {np.median(bias):+.4f}, uitersten {bias.min():+.4f} en {bias.max():+.4f}.")
A(f"  Percentiel-intervallen volstaan, een biascorrectie is niet nodig")
A(f"- **Mislukte replicaties.** Mediaan {int(np.median(fails))} van de 2000, maximum")
A(f"  {fails.max()}. Niets weggegooid op grond van de uitkomst")
A(f"- **Puntsgewijs tegen simultaan.** Een band die over alle 101 punten tegelijk")
A(f"  geldt zou mediaan {(np.median(supt)-1)*100:.0f} procent breder zijn")
A(f"- **Dekking.** {len(cellen)} van de 192 cellen. De 2 ontbrekende zijn Dnieper")
A("  Cherson periode 1, elf droogte-events, te weinig voor een bootstrap")
A("")

# ------------------------------------------------ 7. voorstel
A("## 7. Voorstel voor het artikel")
A("")
A("**Nog niet uitgevoerd. Ter goedkeuring aan Floris, daarna eventueel co-auteurs.**")
A("")
A("### Methoden, 2.4.2, twee alinea's erbij")
A("")
A("> Confidence intervals for the transition probabilities were obtained by a")
A("> non-parametric bootstrap over drought events (B = 2000). For each resample the")
A("> full estimation procedure was repeated, including marginal parameter estimation")
A("> and copula selection by AIC, so that the intervals reflect both parameter and")
A("> model-selection uncertainty. Intervals are pointwise 95% percentile intervals;")
A("> differences between severity levels were bootstrapped directly. In addition,")
A("> the existence of drought-severity dependence was tested per location with a")
A("> permutation test in which the null distribution incorporates the same")
A("> fifteen-family selection step, complemented by Kendall's tau, Spearman's rho")
A("> and Hoeffding's D.")
A("")
A("> The difference between the conditional and unconditional exceedance")
A("> probability was decomposed into a marginal component, comparing post-drought")
A("> windows with arbitrary four-week windows, and a dependence component,")
A("> measuring whether the magnitude of the subsequent peak depends on drought")
A("> severity. Only the latter is a property of the copula.")
A("")
A("### Resultaten, 3.2 en 3.3, de kern van de herschrijving")
A("")
A("> Across all basins, conditioning on a preceding drought is associated with a")
A("> modestly higher probability of a high runoff peak, driven mainly by the")
A("> marginal component. Dependence on drought severity is not detectable at most")
A("> locations, but emerges consistently at specific rivers: the Po (midstream, both")
A("> periods), the Ebro and the Tagus (second period), where more severe droughts")
A("> increase the probability of a subsequent high peak, and, with opposite sign,")
A("> the Vistula and Weser (first period), where more severe droughts decrease it.")
A("")
A("### Appendix")
A("")
A("- de tabel met per cel de gekozen familie, de stabiliteit ervan, en de")
A("  transitiekansen met intervallen op drie floodniveaus, uit")
A("  `bootstrap_diagnostics.csv` en `transition_ci.csv`")
A("- de verschilcurve met band per rivier, `figures/ci_per_river.png`")
A("")
A("### Revision Notes")
A("")
A("Melden, niet laten vinden: de F_Y-reparatie, de einddetectie-reparatie en het")
A("effect daarvan op de gepubliceerde cijfers, met de changelog als bron. De toon:")
A("het uitwerken van R4-03 bracht twee implementatiefouten aan het licht, de")
A("beschreven methode was correct, de cijfers zijn opnieuw berekend en de")
A("conclusies zijn waar nodig aangepast.")
A("")

# ------------------------------------------------ 8. beperkingen
A("## 8. Beperkingen, die mee de tekst in moeten")
A("")
km = np.array([int(r["k_major"]) for r in iid])
A("1. De bootstrap hertrekt de droogte-events en houdt het aantal events, de")
A("   SRI-standaardisatie en de quantieltransformatie vast. De intervallen zijn een")
A("   ondergrens op de totale onzekerheid.")
A(f"2. De zware curve rust op weinig events, mediaan k_major {int(np.median(km))}.")
A("   Waar dat aantal klein is, is de curve staart-extrapolatie van de copula.")
A("3. De intervallen zijn puntsgewijs en niet gecorrigeerd voor 190 gelijktijdige")
A("   cellen. Tellingen over locaties heen moeten daar rekening mee houden; voor")
A("   vooraf benoemde locaties is de ongecorrigeerde p het relevante getal.")
A("4. Met 1000 permutaties is de kleinst mogelijke p 0,001; uitspraken over")
A("   FDR-overleving steunen daarom op de analytische p van tau en rho.")
A("5. De Dnieper valt grotendeels buiten de analyse door te weinig events.")
A("6. De referentiegroepen van conditioneel en unconditioneel verschillen: events")
A("   tegen weken. Dat lost geen enkele as-keuze op.")
A("")
A("## Bestanden en figuren")
A("")
A("- `transition_ci.csv`, per cel en grootheid de puntschatting en de grenzen")
A("- `bootstrap_diagnostics.csv`, per cel de copulakeuze, stabiliteit en diagnostiek")
A("- `selection_frequency.csv`, de familiekeuze per cel over de replicaties")
A("- `../2026-09-02_dependence_tests/dependence_tests.csv`, de vier toetsen")
A("- `figures/ci_example.png`, een cel groot met banden en de verschilcurve")
A("- `figures/ci_decomposition.png`, marginaal tegen copula-deel, met banden")
A("- `figures/ci_per_river.png`, de verschilcurve met band per rivier")
A("- `figures/dependence_overview.png`, sterkte en richting van de samenhang per cel")

open(f"{BS}/report.md", "w").write("\n".join(L) + "\n")
print(f"geschreven: {BS}/report.md ({len(L)} regels)", flush=True)
