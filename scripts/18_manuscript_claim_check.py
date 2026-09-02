"""T-11: houden de uitspraken in het manuscript stand na de as-correctie?

Loopt de kwantitatieve beweringen uit secties 3.2, 3.3 en 4 van
manuscript/HYDROL79380_R1.pdf langs en toetst ze tegen de curves uit
results/2026-09-02_copula_definition_variants/curves.csv. Rekent niets opnieuw.

Er zijn twee soorten beweringen en ze vallen verschillend uit.

  Soort A, zwaar tegen mild. Beide curves staan op de rangschaal van de
  post-droogte pieken. Die vergelijking is onderling altijd al consistent geweest
  en verandert **niet** door de as-correctie.

  Soort B, conditioneel tegen unconditioneel. Daar staat de conditionele curve op
  de rangschaal en de unconditionele op de runoff-quantielschaal. Die vergelijking
  verandert wel, en bij vrijwel alle locaties draait het teken om.

De citaten zijn met de hand overgenomen uit de PDF, met paginanummer erbij. Ze
staan in de tabel hieronder zodat de toets herhaalbaar is en zodat dit meteen de
basis kan vormen voor manuscript/claims.yaml, zie T-41.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --no-project python scripts/18_manuscript_claim_check.py
"""
import csv
import numpy as np

VAR = "results/2026-09-02_copula_definition_variants"
Y = np.linspace(0, 1, 101)
YC = [f"y_{i:03d}" for i in range(101)]
QM = 69          # runoff-quantiel 0,69, de flooddrempel uit het manuscript
DP, MS = "drought_peak", "mean_drought_severity"

cond, uncond = {}, {}
for r in csv.DictReader(open(f"{VAR}/curves.csv")):
    v = np.array([float(r[c]) for c in YC])
    if r["curve"] == "unconditioneel":
        uncond[(r["river"], r["village"], r["period"])] = v
    elif r["variant"] == "gepubliceerd":
        cond[(r["river"], r["village"], r["period"], r["pair"],
              r["axis"], r["curve"])] = v
locaties = sorted({(k[0], k[1]) for k in cond})


def A(river, village, period, pair):
    """Soort A: zwaar min mild, op de rangschaal. Ongewijzigd door de correctie."""
    k = (river, village, period, pair)
    d = cond[k + ("rang", "major")] - cond[k + ("rang", "minor")]
    return float(np.median(d)), float(d[QM])


def B(river, village, period, pair, curve="minor"):
    """Soort B: conditioneel min unconditioneel, gepubliceerd en gecorrigeerd."""
    k = (river, village, period, pair)
    u = uncond[(river, village, period)]
    return (float(cond[k + ("rang", curve)][QM] - u[QM]),
            float(cond[k + ("ruwe", curve)][QM] - u[QM]))


def teken(x):
    return "hoger" if x > 0.005 else ("lager" if x < -0.005 else "gelijk")


L = []
add = L.append
add("# Houden de uitspraken van het manuscript stand na de as-correctie?")
add("")
add("Getoetst tegen `curves.csv` in deze map. Alle waardes bij runoff-quantiel 0,69,")
add("de flooddrempel die het manuscript zelf hanteert. Citaten met de hand overgenomen")
add("uit `manuscript/HYDROL79380_R1.pdf`, paginanummer erbij.")
add("")
add("Twee soorten beweringen, en ze vallen verschillend uit.")
add("")
add("**Soort A, zwaar tegen mild.** Beide curves staan op de rangschaal, dus die")
add("vergelijking was altijd al intern consistent en **verandert niet**.")
add("")
add("**Soort B, conditioneel tegen unconditioneel.** Die vergelijking zet een")
add("rangschaal naast een runoff-quantielschaal en **verandert wel**.")
add("")

add("## De uitspraken die overeind blijven")
add("")
add("### C-02, pagina 6, abstract. Soort A")
add("")
add("> The copula models indicate that two different drought characteristics, mean")
add("> severity and drought peak, affect flood likelihood in different ways.")
add("")
add("Blijft staan. Dit gaat over de twee variabelenparen onderling, niet over de")
add("unconditionele lijn.")
add("")
add("### C-03, pagina 27. Soort A")
add("")
add("> In the case of the Po river, we see an increased transition probability only")
add("> during the second period, when a more severe prior drought peak event is")
add("> associated with a higher probability of transitioning to a flood event.")
add("")
add("| periode | zwaar min mild, mediaan | bij q=0,69 | oordeel |")
add("|---|---|---|---|")
for p, pn in (("first", "1"), ("second", "2")):
    m, q = A("Po", "Piacenza", p, DP)
    add(f"| {pn} | {m:+.3f} | {q:+.3f} | {teken(m)} |")
add("")
add("Blijft staan. In periode 1 is er geen verschil, in periode 2 wel, en dat is")
add("precies wat de zin beweert.")
add("")
add("### C-06, pagina 28. Soort A, met een kanttekening")
add("")
add("> For the midstream location of the Ebro river (Fig. 6), an increased prior")
add("> drought condition is associated with a higher transition probability in both")
add("> periods.")
add("")
add("| periode | zwaar min mild, mediaan | bij q=0,69 |")
add("|---|---|---|")
for p, pn in (("first", "1"), ("second", "2")):
    m, q = A("Ebro", "Tudela", p, DP)
    add(f"| {pn} | {m:+.3f} | {q:+.3f} |")
add("")
add("Blijft staan voor periode 1. Voor periode 2 is het effect vrijwel nul, dus")
add("\"in both periods\" is te sterk. Dat is los van de as-correctie, het was ook in de")
add("gepubliceerde berekening al zo.")
add("")
add("### C-08, pagina 30. Soort A")
add("")
add("> In the second period, both locations show a higher transition probabilities")
add("> when conditioning on major drought characteristics.")
add("")
add("| locatie | zwaar min mild, mediaan | bij q=0,69 |")
add("|---|---|---|")
for riv, vil in (("Po", "Piacenza"), ("Ebro", "Tudela")):
    m, q = A(riv, vil, "second", MS)
    add(f"| {riv} {vil} | {m:+.3f} | {q:+.3f} |")
add("")
add("Blijft staan.")
add("")
add("### C-10, pagina 31, de tellingen. Soort A")
add("")
add("> In the first period, increases in transition probability are observed in 5")
add("> locations for Drought Peak and in 6 locations for Mean Severity, while in the")
add("> second period, the count rises slightly to 7 and 9 respectively.")
add("")
add("Aantal van de 48 locaties waar de zware curve boven de milde ligt, bij drie")
add("mogelijke drempels, want het manuscript legt zijn criterium niet vast:")
add("")
add("| criterium | p1 drought peak | p1 mean severity | p2 drought peak | p2 mean severity |")
add("|---|---|---|---|---|")
for drempel in (0.01, 0.02, 0.05):
    rij = []
    for p in ("first", "second"):
        for pair in (DP, MS):
            n = sum(1 for riv, vil in locaties
                    if (riv, vil, p, pair, "rang", "minor") in cond
                    and np.median(cond[(riv, vil, p, pair, "rang", "major")]
                                  - cond[(riv, vil, p, pair, "rang", "minor")]) > drempel)
            rij.append(n)
    add(f"| mediaan > +{drempel:.2f} | {rij[0]} | {rij[1]} | {rij[2]} | {rij[3]} |")
add("")
add("Bij een drempel van +0,02 komt er 7, 5, 6, 9 uit tegen de gepubliceerde 5, 6, 7, 9.")
add("Dezelfde orde, niet exact gelijk. Het criterium staat niet in de tekst en de")
add("gepubliceerde berekening heeft geen seed, dus exact reproduceren kan niet. Het")
add("criterium hoort alsnog opgeschreven te worden.")
add("")

add("## De uitspraken die moeten veranderen")
add("")
add("Alle vier vergelijken de conditionele curve met de unconditionele lijn. Bij alle")
add("vier draait het teken om.")
add("")
add("### C-04 en C-05, pagina 27. Soort B")
add("")
add("> However, compared to the unconditional probability, which can be interpreted as")
add("> the transition probability within the next 4 weeks unconditional on any prior")
add("> drought state, the transition probabilities remain lower. This results in the")
add("> conclusion that: during the second period, transition probabilities are lower")
add("> conditioning on a prior drought event.")
add("")
add("Po midstream, conditioneel min unconditioneel bij q=0,69:")
add("")
add("| periode | curve | gepubliceerde aflezing | gecorrigeerd |")
add("|---|---|---|---|")
for p, pn in (("first", "1"), ("second", "2")):
    for curve, cn in (("minor", "mild"), ("major", "zwaar")):
        g, k = B("Po", "Piacenza", p, DP, curve)
        add(f"| {pn} | {cn} | {g:+.3f} ({teken(g)}) | {k:+.3f} ({teken(k)}) |")
add("")
add("De conclusie draait om. Niet lager maar hoger, en met een marge van ongeveer 0,16")
add("tot 0,21.")
add("")
add("### C-07, pagina 28. Soort B")
add("")
add("> In both periods, conditioning on a prior drought event results in a lower")
add("> transition probability compared to the unconditional transition probability.")
add("")
add("Ebro midstream, conditioneel min unconditioneel bij q=0,69:")
add("")
add("| periode | curve | gepubliceerde aflezing | gecorrigeerd |")
add("|---|---|---|---|")
for p, pn in (("first", "1"), ("second", "2")):
    for curve, cn in (("minor", "mild"), ("major", "zwaar")):
        g, k = B("Ebro", "Tudela", p, DP, curve)
        add(f"| {pn} | {cn} | {g:+.3f} ({teken(g)}) | {k:+.3f} ({teken(k)}) |")
add("")
add("### C-09, pagina 30. Soort B")
add("")
add("> Nevertheless, the transition probabilities remain lower than the unconditional")
add("> transition probabilities.")
add("")
add("Gaat over Po en Ebro midstream bij mean severity. Zelfde beeld:")
add("")
add("| locatie | periode | gepubliceerde aflezing | gecorrigeerd |")
add("|---|---|---|---|")
for riv, vil in (("Po", "Piacenza"), ("Ebro", "Tudela")):
    for p, pn in (("first", "1"), ("second", "2")):
        g, k = B(riv, vil, p, MS)
        add(f"| {riv} {vil} | {pn} | {g:+.3f} ({teken(g)}) | {k:+.3f} ({teken(k)}) |")
add("")
add("### C-11, pagina 31, de Dnieper. Soort B, en die kantelt anders dan de rest")
add("")
add("> One such region is the Dnieper basin, where in the first period the upstream")
add("> location at Krementsjoek shows an increased transition probability when")
add("> conditioning on a major previous mean severity, even compared to the")
add("> unconditional transition probability.")
add("")
add("| locatie | periode | gepubliceerde aflezing | gecorrigeerd |")
add("|---|---|---|---|")
for vil, p, pn in (("Krementsjoek", "first", "1"), ("Dnipro", "second", "2")):
    g, k = B("Dnieper", vil, p, MS, "major")
    add(f"| Dnieper {vil} | {pn} | {g:+.3f} ({teken(g)}) | {k:+.3f} ({teken(k)}) |")
add("")
add("De bewering zelf blijft feitelijk juist, ook na correctie. Maar het woord \"even\"")
add("verliest zijn betekenis. Het was bijzonder omdat vrijwel geen enkele locatie boven")
add("de unconditionele lijn uitkwam. Na de correctie doet ruim de helft dat, dus de")
add("Dnieper is dan niet langer een uitzondering.")
add("")

add("## Wat dit met het verhaal doet")
add("")
add("Het manuscript vertelt nu: conditioneren op een droogte verlaagt de floodkans, en")
add("de zwaarte van de droogte draait dat gedeeltelijk terug. Pagina 27 zegt dat")
add("letterlijk, \"the severity of the drought event reverses this effect partially\".")
add("")
add("Na de correctie is de eerste helft van die zin niet houdbaar en de tweede helft")
add("wel. Wat er overblijft: conditioneren op een droogte verhoogt de floodkans licht,")
add("en bij een zwaardere droogte iets meer.")
add("")
add("Over alle 192 cellen, conditioneel min unconditioneel bij q=0,69:")
add("")
gp = np.array([B(r, v, p, pr)[0] for r, v in locaties for p in ("first", "second")
               for pr in (DP, MS) if (r, v, p, pr, "rang", "minor") in cond])
gc = np.array([B(r, v, p, pr)[1] for r, v in locaties for p in ("first", "second")
               for pr in (DP, MS) if (r, v, p, pr, "rang", "minor") in cond])
add(f"| | mediaan | cellen lager dan unconditioneel |")
add("|---|---|---|")
add(f"| gepubliceerde aflezing | {np.median(gp):+.3f} | {int((gp<0).sum())} van {len(gp)} |")
add(f"| gecorrigeerd | {np.median(gc):+.3f} | {int((gc<0).sum())} van {len(gc)} |")
add("")
add("Dat maakt de twee helften van het artikel juist consistenter. De ECA-kant vindt")
add("meer samenhang dan toeval, met gepoolde ratio's van 1,42 tot 1,59. Een")
add("copula-kant die zegt dat de floodkans na een droogte fors lager is, wringt")
add("daarmee. Een copula-kant die zegt dat hij licht hoger is, niet.")
add("")
add("## Wat hier niet uit volgt")
add("")
add("**Er zijn nog geen betrouwbaarheidsintervallen.** Dat is precies wat T-11 nog moet")
add("opleveren, en het is ook wat R4-03 vraagt. Zonder die intervallen is niet te")
add("zeggen of een verschil van +0,16 bij de Po standhoudt.")
add("")
add("**Het signaal komt niet uit de copula.** De Kendall tau tussen droogtezwaarte en")
add("de piek erna ligt bij Ebro en Po tussen -0,03 en +0,12. Wat het gat met de")
add("unconditionele lijn maakt, is dat het vier-weeks venster na een droogte hogere")
add("pieken bevat dan een willekeurig venster. Dat is een verschil tussen twee")
add("verdelingen, geen afhankelijkheid tussen twee variabelen, en het is precies wat de")
add("ECA-kant al meet. Dat onderscheid hoort in de tekst.")
add("")
add("**Twee dingen zijn nog niet gerepareerd.** De referentiegroepen verschillen, events")
add("tegen weken, en het floodvenster telt aan de conditionele kant vijf weekpunten en")
add("aan de unconditionele vier. Dat laatste is R-02, en voor Ebro en Po is nagegaan")
add("dat het de uitkomst niet verklaart.")
add("")
add("**Appendix E, niet D.** Pagina 30 verwijst naar Appendix E voor de transitiekansen")
add("van alle locaties, terwijl in onze eigen notities Appendix D staat. Nagaan welke")
add("klopt voordat er naar verwezen wordt.")

uit = f"{VAR}/manuscript_claim_check.md"
open(uit, "w").write("\n".join(L) + "\n")
print("\n".join(L))
print(f"\n\ngeschreven naar {uit}", flush=True)
