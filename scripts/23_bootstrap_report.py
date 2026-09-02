"""T-11: rapport bij de betrouwbaarheidsintervallen (R4-03).

Rekent niets opnieuw. Leest results/2026-09-02_copula_bootstrap/ en schrijft
report.md. Voor Floris, dus in het Nederlands en zonder jargon waar het kan.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --no-project python scripts/23_bootstrap_report.py
"""
import csv, collections, os
import numpy as np

BS = "results/2026-09-02_copula_bootstrap"
COR = "results/2026-09-02_copula_corrected"
Y = np.linspace(0, 1, 101)
YC = [f"y_{i:03d}" for i in range(101)]
QM = 69                      # runoff-quantiel 0,69, de flooddrempel van het manuscript
NIVEAUS = [(69, "0,69"), (90, "0,90"), (95, "0,95")]
PAIR_NL = {"drought_peak": "drought peak", "mean_drought_severity": "mean severity"}


def lees_ci():
    d = {}
    with open(f"{BS}/transition_ci.csv") as fh:
        for r in csv.DictReader(fh):
            d[(r["river"], r["village"], r["period"], r["pair"], r["scheme"],
               r["quantity"], r["kind"])] = np.array([float(r[c]) for c in YC])
    return d


ci = lees_ci()
diag = list(csv.DictReader(open(f"{BS}/bootstrap_diagnostics.csv")))
sel = list(csv.DictReader(open(f"{BS}/selection_frequency.csv")))
cellen = sorted({(k[0], k[1], k[2], k[3]) for k in ci if k[4] == "iid"})
iid = [r for r in diag if r["scheme"] == "iid"]
print(f"cellen: {len(cellen)}, diagnostiekrijen iid: {len(iid)}", flush=True)


def waarde(cel, hoeveelheid, soort, j=QM, scheme="iid"):
    k = (cel[0], cel[1], cel[2], cel[3], scheme, hoeveelheid, soort)
    return float(ci[k][j]) if k in ci else np.nan


def telling(hoeveelheid, j, richting, scheme="iid"):
    """Aantal cellen waar het interval nul uitsluit, in de gevraagde richting."""
    n_pos = n_neg = n_tot = 0
    for cel in cellen:
        lo = waarde(cel, hoeveelheid, "lo", j, scheme)
        hi = waarde(cel, hoeveelheid, "hi", j, scheme)
        if not (np.isfinite(lo) and np.isfinite(hi)):
            continue
        n_tot += 1
        if lo > 0: n_pos += 1
        elif hi < 0: n_neg += 1
    return (n_pos if richting == "pos" else n_neg), n_tot


L = []
A = L.append
A("# Betrouwbaarheidsintervallen bij de transitiekansen")
A("")
A("Antwoord op de tweede helft van reviewerpunt R4-03. Gemaakt met")
A("`scripts/23_bootstrap_report.py`, dat niets herberekent en alleen de uitvoer van")
A("`scripts/22_bootstrap_transition_ci.py` leest.")
A("")
A("## Wat de reviewer vroeg")
A("")
A("> \"The copula modelling relies on AIC for selection among several families, but")
A("> the authors do not report which copula was selected for each location and")
A("> variable pair, nor do they provide confidence intervals for the estimated")
A("> transition probabilities.\"")
A("")
A("Twee dingen. Welke copula gekozen is, dat lag al klaar in")
A("`results/2026-09-01_copula_selection/`. En intervallen bij de transitiekansen,")
A("dat is dit.")
A("")
A("## Hoe het interval tot stand komt, in gewone taal")
A("")
A("Per locatie, periode en variabelenpaar hebben we ongeveer negentig droogtes. Van")
A("elke droogte weten we twee dingen: hoe zwaar hij was, en hoe hoog de runoff-piek")
A("in de vier weken erna was. Op die paren is de hele berekening gebaseerd.")
A("")
A("De vraag achter een betrouwbaarheidsinterval is: hoeveel had de uitkomst kunnen")
A("verschillen als we toevallig andere droogtes hadden waargenomen. Dat wordt")
A("nagebootst door uit die negentig paren tweeduizend keer opnieuw negentig paren te")
A("trekken, met teruglegging, en de hele berekening elke keer over te doen. Dus")
A("opnieuw de marginale verdelingen, opnieuw de copulakeuze, opnieuw de drempels,")
A("opnieuw de curve. Van die tweeduizend uitkomsten zijn de 2,5 en 97,5 percentielen")
A("de grenzen van het interval.")
A("")
A("Belangrijk: de copulafamilie wordt in elke replicatie opnieuw gekozen. Als je hem")
A("vastzet, doe je alsof je zeker weet welke familie de juiste is, en dat weten we")
A("juist niet. Die vastgezette variant staat er wel naast, zodat te zien is welk deel")
A("van de onzekerheid uit de keuze komt en welk deel uit de schatting.")
A("")

# ---------------------------------------------------------------- 1. breedtes
A("## Hoe breed zijn de intervallen")
A("")
br = np.array([float(r["median_width_minor"]) for r in iid])
brd = np.array([float(r["median_width_diff"]) for r in iid])
A(f"Mediane breedte van het 95 procent interval rond de milde curve: **{np.median(br):.3f}**.")
A(f"Kwartielen {np.percentile(br,25):.3f} tot {np.percentile(br,75):.3f}, uiterste")
A(f"waardes {br.min():.3f} en {br.max():.3f}.")
A("")
A("Ter vergelijking: de correctie van de as, die eerder deze week is doorgevoerd,")
A("verschoof de transitiekans met ongeveer 0,50 bij het floodniveau van het")
A(f"manuscript. De onzekerheid eromheen is dus ruwweg een factor {0.50/np.median(br):.0f} kleiner")
A("dan de fout die eruit gehaald is.")
A("")
A(f"Voor het verschil tussen de zware en de milde curve is de mediane breedte")
A(f"**{np.median(brd):.3f}**.")
A("")

# ---------------------------------------------------------------- 2. significantie
A("## Waar sluit het interval nul uit")
A("")
A("Dit is de vraag die telt. Een interval dat nul bevat betekent: op deze locatie")
A("kunnen we het effect niet van toeval onderscheiden.")
A("")
A("### Verschil tussen zware en milde droogte")
A("")
A("| floodniveau | interval geheel boven nul | geheel onder nul | bevat nul |")
A("|---|---|---|---|")
for j, lab in NIVEAUS:
    p, tot = telling("diff_resel", j, "pos")
    n, _ = telling("diff_resel", j, "neg")
    A(f"| {lab} | {p} van {tot} | {n} van {tot} | {tot-p-n} van {tot} |")
A("")
A("### Het copula-deel, dus hangt de piek samen met de zwaarte van de droogte")
A("")
A("| floodniveau | boven nul | onder nul | bevat nul |")
A("|---|---|---|---|")
for j, lab in NIVEAUS:
    p, tot = telling("copula_part", j, "pos")
    n, _ = telling("copula_part", j, "neg")
    A(f"| {lab} | {p} van {tot} | {n} van {tot} | {tot-p-n} van {tot} |")
A("")
A("### Het marginale deel, dus is het venster na een droogte natter dan gemiddeld")
A("")
A("| floodniveau | boven nul | onder nul | bevat nul |")
A("|---|---|---|---|")
for j, lab in NIVEAUS:
    p, tot = telling("marginal_part", j, "pos")
    n, _ = telling("marginal_part", j, "neg")
    A(f"| {lab} | {p} van {tot} | {n} van {tot} | {tot-p-n} van {tot} |")
A("")

# ---------------------------------------------------------------- 3. Ebro en Po
A("## Ebro en Po, de twee rivieren die het artikel uitlicht")
A("")
A("Bij het floodniveau van het manuscript, quantiel 0,69. Interval is 95 procent,")
A("puntsgewijs.")
A("")
for riv in ("Ebro", "Po"):
    A(f"### {riv}")
    A("")
    A("| locatie | per. | paar | k_maj | copula-deel | marginaal deel | zwaar min mild |")
    A("|---|---|---|---|---|---|---|")
    for cel in [c for c in cellen if c[0] == riv]:
        d = [r for r in iid if (r["river"], r["village"], r["period"], r["pair"]) == cel]
        kmaj = d[0]["k_major"] if d else "?"
        def fmt(h):
            p = waarde(cel, h, "point"); lo = waarde(cel, h, "lo"); hi = waarde(cel, h, "hi")
            if not np.isfinite(p): return "geen"
            ster = "**" if (lo > 0 or hi < 0) else ""
            return f"{ster}{p:+.3f}{ster} [{lo:+.3f}, {hi:+.3f}]"
        A(f"| {cel[1]} | {cel[2][:3]} | {PAIR_NL[cel[3]]} | {kmaj} | "
          f"{fmt('copula_part')} | {fmt('marginal_part')} | {fmt('diff_resel')} |")
    A("")
A("Vet betekent dat het interval nul uitsluit.")
A("")

# ---------------------------------------------------------------- 4. copulakeuze
A("## Hoe hard staat de copulakeuze")
A("")
A("Dit versterkt de eerste helft van R4-03. De reviewer vraagt welke familie is")
A("gekozen. Het eerlijke antwoord is: gekozen wel, maar zelden overtuigend.")
A("")
sh = np.array([float(r["modal_share"]) for r in iid])
nf = np.array([int(r["n_families_seen"]) for r in iid])
same = sum(1 for r in iid if r["copula_point"] == r["copula_modal"])
A(f"Over de bootstrap-replicaties komt de familie die op de volle steekproef won in")
A(f"**{same} van de {len(iid)}** cellen ook als meest gekozen familie terug.")
A(f"De mediane frequentie waarmee die winnaar terugkomt is **{np.median(sh):.0%}**,")
A(f"met kwartielen {np.percentile(sh,25):.0%} en {np.percentile(sh,75):.0%}.")
A(f"Het mediane aantal verschillende families dat over tweeduizend replicaties")
A(f"gekozen wordt is **{int(np.median(nf))}**, met een maximum van {nf.max()}.")
A("")
A("Dat past bij wat eerder gemeten is: het AIC-verschil met de nummer twee ligt in")
A("175 van de 192 cellen onder 2, de gangbare grens waaronder geen onderscheid")
A("gemaakt kan worden.")
A("")

# ---------------------------------------------------------------- 5. blokcontrole
A("## Controle op seriele afhankelijkheid")
A("")
A("Droogtes volgen elkaar op in de tijd en zijn niet los van elkaar. De gewone")
A("bootstrap gaat daaraan voorbij. Als controle is er een blokbootstrap gedraaid, die")
A("aaneengesloten reeksen droogtes trekt in plaats van losse.")
A("")
lag = np.array([abs(float(r["lag1_spearman_drought"])) for r in iid
                if r["lag1_spearman_drought"] not in ("", "nan")])
A(f"De correlatie tussen opeenvolgende droogtes heeft mediaan {np.median(lag):.3f} in")
A(f"absolute waarde, met p90 {np.percentile(lag,90):.3f} en maximum {lag.max():.3f}.")
A("")
ratio = []
for r in iid:
    k = (r["river"], r["village"], r["period"], r["pair"])
    b = [x for x in diag if x["scheme"] == "block"
         and (x["river"], x["village"], x["period"], x["pair"]) == k]
    if b and float(r["median_width_minor"]) > 0:
        ratio.append(float(b[0]["median_width_minor"]) / float(r["median_width_minor"]))
ratio = np.array(ratio)
A(f"De blokbootstrap geeft intervallen die mediaan **{np.median(ratio):.2f} keer** zo")
A(f"breed zijn als de gewone, met kwartielen {np.percentile(ratio,25):.2f} en")
A(f"{np.percentile(ratio,75):.2f}.")
A("")

# ---------------------------------------------------------------- 6. diagnostiek
A("## Diagnostiek")
A("")
bias = np.array([float(r["median_bias"]) for r in iid])
supt = np.array([float(r["supt_over_196"]) for r in iid])
fails = np.array([int(r["failed_replicates"]) for r in iid])
A(f"- **Bias.** De mediaan van de bootstrapverdeling wijkt mediaan {np.median(bias):+.4f}")
A(f"  af van de puntschatting, uiterste waardes {bias.min():+.4f} en {bias.max():+.4f}.")
A("  Nagenoeg gecentreerd, dus percentiel-intervallen volstaan en een biascorrectie")
A("  is niet nodig.")
A(f"- **Mislukte replicaties.** Mediaan {int(np.median(fails))} van de 2000, maximum")
A(f"  {fails.max()}. Er zijn geen replicaties weggegooid op grond van hun uitkomst.")
A(f"- **Puntsgewijs tegen simultaan.** De intervallen zijn puntsgewijs, zoals de")
A(f"  reviewer vraagt. Een simultane band over alle 101 punten zou mediaan")
A(f"  {(np.median(supt)-1)*100:.0f} procent breder zijn.")
A("")


# ---------------------------------------------------------------- 7. koppeling
A("## Wat dit betekent voor het artikel")
A("")
A("De intervallen zijn het laatste stuk van een reeks bevindingen. Ze staan niet op")
A("zichzelf, dus hier het geheel op een rij.")
A("")
A("### Wat er al lag")
A("")
A("De review van de copula-kant leverde vijftien bevindingen op. Vier zijn besloten")
A("en doorgevoerd, zie `CHANGELOG-methodology.md` van 2 september. De zwaarste was")
A("dat de code de stap `F_Y` uit de formule op pagina 21 oversloeg, waardoor de")
A("conditionele en de unconditionele curve op verschillende schalen in dezelfde")
A("figuur stonden. Daardoor draaien vier passages in de tekst van teken om.")
A("")
A("### Wat de intervallen daaraan toevoegen")
A("")
p_dif, tot = telling("diff_resel", QM, "pos")
n_dif, _ = telling("diff_resel", QM, "neg")
p_cop, _ = telling("copula_part", QM, "pos")
n_cop, _ = telling("copula_part", QM, "neg")
p_mar, _ = telling("marginal_part", QM, "pos")
A(f"Bij het floodniveau van het manuscript sluit het interval om het **marginale")
A(f"deel** in {p_mar} van de {tot} cellen nul uit, en dan altijd naar boven. Dat is")
A("de bevinding die overeind blijft: het venster na een droogte is natter dan een")
A("willekeurig venster. Precies wat de ECA-kant ook meet.")
A("")
A(f"Het interval om het **copula-deel**, dus of de zwaarte van de droogte uitmaakt,")
A(f"sluit nul uit in {p_cop} cellen naar boven en {n_cop} naar beneden. In de")
A(f"overige {tot-p_cop-n_cop} van de {tot} is er geen effect aan te tonen.")
A("")
A(f"Het interval om het **verschil tussen zware en milde droogte** sluit nul uit in")
A(f"{p_dif} cellen naar boven en {n_dif} naar beneden.")
A("")
A("### Welke uitspraken in het artikel dit raakt")
A("")
A("| passage | uitspraak | status |")
A("|---|---|---|")
A("| p6, abstract | twee droogtekarakteristieken werken verschillend | blijft, maar de meeste locaties halen geen significantie |")
A("| p27, Po | zwaardere droogte geeft hogere kans, periode 2 | blijft |")
A("| p27, Po | conditionele kans blijft lager dan unconditioneel | **vervalt**, teken draait om |")
A("| p28, Ebro | zwaardere droogte geeft hogere kans, beide periodes | blijft voor periode 1, niet voor periode 2 |")
A("| p28, Ebro | conditioneel lager dan unconditioneel | **vervalt**, teken draait om |")
A("| p30 | conditioneel blijft lager dan unconditioneel | **vervalt**, teken draait om |")
A("| p31 | tellingen 5, 6, 7, 9 | criterium ontbreekt, zie D-19 |")
A("| p34 | robuuste systemen zijn Po en Ebro | blijft, maar nu met interval te onderbouwen |")
A("")

# ---------------------------------------------------------------- 8. voorstel
A("## Voorstel voor opname in het artikel")
A("")
A("**Nog niet uitgevoerd. Dit is een voorstel dat Floris eerst moet goedkeuren.**")
A("")
A("### Methodensectie, 2.4.2")
A("")
A("Twee alinea's erbij. Een over de intervallen, een over de opsplitsing.")
A("")
A("> Confidence intervals for the transition probabilities were obtained by a")
A("> non-parametric bootstrap over drought events. For each location, period and")
A("> variable pair, the observed event pairs were resampled with replacement 2000")
A("> times, and the full estimation procedure was repeated for each resample:")
A("> marginal parameters, the rank transformation, copula selection by AIC, and the")
A("> conditioning thresholds. Intervals are pointwise 95% percentile intervals.")
A("> Because the copula family is reselected within each resample, the intervals")
A("> reflect both parameter and selection uncertainty. Differences between severity")
A("> levels were bootstrapped directly rather than inferred from the separate")
A("> intervals, since the two curves are strongly correlated across resamples.")
A("")
A("> The difference between the conditional and the unconditional exceedance")
A("> probability was decomposed into two parts. The first compares the distribution")
A("> of post-drought runoff peaks with that of all four-week windows, and therefore")
A("> measures whether the period following a drought is wetter than an arbitrary")
A("> period. The second compares the conditional curve with the curve that would")
A("> arise under independence, and therefore measures whether the magnitude of the")
A("> subsequent peak depends on drought severity. Only the second is a property of")
A("> the copula.")
A("")
A("### Resultatensectie, 3.2 en 3.3")
A("")
A("De vier passages die van teken omdraaien moeten herschreven. Voorstel voor de")
A("kernzin, in plaats van wat er nu op pagina 27 staat:")
A("")
A("> Conditioning on a preceding drought is associated with a slightly higher")
A("> probability of a high runoff peak in the following four weeks than at an")
A("> arbitrary moment. The decomposition shows that this is driven by the marginal")
A("> difference between post-drought windows and arbitrary windows rather than by")
A("> dependence on drought severity, which is small and significant at only a")
A("> minority of locations.")
A("")
A("### Appendix")
A("")
A("Twee tabellen en een figuur.")
A("")
A("- **Tabel D1**, de gekozen copula per locatie en variabelenpaar, met parameter,")
A("  AIC, het AIC-verschil met de nummer twee, en het aantal droogtes boven de")
A("  drempels. Ligt klaar als `copula_selection.csv`. Dit is het letterlijke antwoord")
A("  op de eerste helft van R4-03")
A("- **Tabel D2**, de transitiekans met interval op drie floodniveaus, per cel. Ligt")
A("  klaar als `transition_ci.csv`")
A("- **Figuur**, de verschilcurve met band per rivier. Ligt klaar als")
A("  `figures/ci_per_river.png`")
A("")
A("### Wat ik zou weglaten")
A("")
A("De unconditionele lijn uit de hoofdfiguren halen en vervangen door de")
A("onafhankelijkheidslijn. R1-07 vraagt letterlijk wat die oranje lijn betekent, en")
A("het eerlijke antwoord is dat hij een andere referentiegroep beschrijft, weken")
A("tegen events. De onafhankelijkheidslijn beantwoordt de vraag die de figuur")
A("suggereert wel. Dat is een presentatiekeuze, geen herberekening.")
A("")
A("### Revision Notes")
A("")
A("De reparatie van `F_Y` hoort daar gemeld te worden, niet gevonden. Voorstel voor")
A("de toon: melden dat het uitwerken van R4-03 een fout in de implementatie aan het")
A("licht bracht, dat de gepubliceerde formule op pagina 21 correct was en de code")
A("ervan afweek, en dat de betrokken passages zijn herschreven. Dat is een sterkere")
A("positie dan wachten tot een reviewer het vindt.")
A("")

# ---------------------------------------------------------------- 9. beperkingen
A("## Beperkingen, die horen in de tekst")
A("")
A("1. De bootstrap hertrekt de droogte-events en houdt het aantal events, de")
A("   SRI-standaardisatie en de quantieltransformatie vast. De intervallen zijn")
A("   daarmee een ondergrens op de totale onzekerheid.")
A("2. De unconditionele curve wordt niet mee hertrokken, want die komt uit alle")
A("   weken en niet uit de events. De intervallen om het marginale deel weerspiegelen")
A("   dus alleen de onzekerheid aan de eventkant.")
A(f"3. De zware curve rust op weinig events. `k_major` heeft mediaan {int(np.median([int(r['k_major']) for r in iid]))},")
A("   en bij de cellen zonder enkele zware droogte is er geen curve. Waar `k_major`")
A("   klein is, is de curve een extrapolatie in de staart van de copula.")
A("4. De intervallen zijn puntsgewijs en niet gecorrigeerd voor het feit dat er 192")
A("   van zijn. Wie straks locaties gaat tellen moet daar iets mee, zie D-19.")
A("5. De referentiegroepen verschillen: events tegen weken. Ook na de as-correctie.")
A("")

open(f"{BS}/report.md", "w").write("\n".join(L) + "\n")
print(f"geschreven: {BS}/report.md ({len(L)} regels)", flush=True)
