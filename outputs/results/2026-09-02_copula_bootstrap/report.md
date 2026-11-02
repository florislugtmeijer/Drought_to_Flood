# T-11 eindrapport: copulakeuze en betrouwbaarheid van de transitiekansen

Antwoord op reviewerpunt R4-03, beide helften, plus de vervolgvraag of de
copula's echt zo weinig betekenis hebben. Alles hieronder is berekend op de
gerepareerde eventdefinities van 2 september: einddetectie, duur als telling,
floodvenster strikt na het event, F_Y toegepast, parametrische marginalen.
Gemaakt met `scripts/23_bootstrap_report.py`, dat alleen bestaande uitvoer leest.

## Hoe dit rapport te lezen

Drie instrumenten, elk met een eigen vraag.

**De permutatietoetsen** vragen: bestaat de samenhang tussen droogtezwaarte en de
piek erna, of is het toeval. Vier toetsen per cel: Kendall tau en Spearman rho
(monotone samenhang), Hoeffding D (ook niet-monotoon), en een permutatietoets op
de copulafit zelf waarbij de selectie over vijftien families in de nulverdeling
zit. Een cel telt hieronder als **sterk** wanneer minstens drie van de vier onder
p 0,05 komen.

**De bootstrap-intervallen** vragen: hoe groot is het effect en hoe onzeker. 2000
replicaties per cel, waarbij elke keer de hele keten opnieuw wordt gedaan,
inclusief de copulakeuze. 95 procent, percentiel, puntsgewijs.

**De opsplitsing** haalt uit elkaar wat vaak door elkaar loopt: het *marginale*
deel, is het venster na een droogte natter dan een willekeurig venster, en het
*copula*-deel, hangt de hoogte van de piek samen met de zwaarte van de droogte.
Alleen dat tweede is waar een copula voor dient, en alleen dat tweede staat
hieronder centraal.

## 1. Waar is de samenhang sterk, en welke kant op

Van de 190 cellen halen er **12** drie of vier van de vier
toetsen. Gerangschikt op de sterkte van de samenhang (tau):

| rivier | locatie | periode | variabele | richting | tau | copula-deel bij 0,69 | zwaar min mild bij 0,69 | toetsen |
|---|---|---|---|---|---|---|---|---|
| Tagus | La Bazagona | 2 | mean severity | verhoogt | +0.234 | **+0.156** [+0.063, +0.273] | +0.026 [-0.148, +0.198] | 4/4 |
| Tagus | La Bazagona | 2 | drought peak | verhoogt | +0.229 | **+0.126** [+0.053, +0.214] | +0.033 [-0.014, +0.251] | 4/4 |
| Vistula | Turon | 1 | drought peak | verlaagt | -0.219 | **-0.128** [-0.229, -0.046] | **-0.235** [-0.294, -0.015] | 4/4 |
| Vistula | Turon | 1 | mean severity | verlaagt | -0.211 | **-0.204** [-0.321, -0.053] | -0.216 [-0.339, +0.005] | 4/4 |
| Po | Piacenza | 2 | mean severity | verhoogt | +0.206 | **+0.020** [+0.003, +0.044] | +0.015 [-0.079, +0.039] | 3/4 |
| Po | Piacenza | 1 | mean severity | verhoogt | +0.175 | **+0.092** [+0.022, +0.157] | +0.025 [-0.337, +0.109] | 3/4 |
| Ebro | Haro | 2 | mean severity | verhoogt | +0.171 | **+0.080** [+0.012, +0.114] | geen | 4/4 |
| Po | Piacenza | 2 | drought peak | verhoogt | +0.164 | **+0.008** [+0.002, +0.029] | -0.002 [-0.022, +0.027] | 3/4 |
| Ebro | Tudela | 2 | mean severity | verhoogt | +0.155 | **+0.064** [+0.014, +0.131] | +0.067 [-0.070, +0.142] | 3/4 |
| Po | Piacenza | 1 | drought peak | verhoogt | +0.151 | +0.073 [-0.002, +0.138] | +0.008 [-0.051, +0.092] | 4/4 |
| Danube | Aschach an der Donau | 1 | mean severity | verhoogt | +0.146 | **+0.116** [+0.030, +0.198] | **+0.106** [+0.002, +0.172] | 3/4 |
| Weser | Bodenwerder | 1 | drought peak | verlaagt | -0.143 | **-0.073** [-0.114, -0.011] | -0.029 [-0.374, +0.044] | 3/4 |

Vet betekent dat het 95 procent interval nul uitsluit. "Richting" leest als: een
zwaardere droogte *verhoogt* dan wel *verlaagt* de kans op een hoge piek erna.

Het beeld splitst in twee clusters. **Positief**, 9 cellen: de zuidelijke
rivieren, met Po Piacenza in beide periodes, Ebro en Tagus in periode 2, en Danube
Aschach in periode 1. **Negatief**, 3 cellen: Centraal-Europa in periode 1,
Vistula en Weser. Daar geeft een zwaardere droogte een lagere kans op een hoge
piek, wat past bij een uitgedroogde bodem die de eerste neerslag opvangt. Dat
negatieve cluster staat nu nergens in het artikel en is materiaal voor R4-04.

Daarnaast halen 6 cellen twee van de vier toetsen. De overige cellen zijn
niet van toeval te onderscheiden.

### Over heel Europa gewogen

Over alle 190 cellen: 19 significant op tau tegen 9.5
verwacht bij puur toeval, mediaan tau -0.013, positief in
80 van de 190. Geen enkele cel overleeft een
FDR-correctie over alle cellen tegelijk. De juiste lezing: er is geen breed
Europees severity-effect, er zijn specifieke plekken waar het echt is. Voor
locaties die het artikel al aanwijst, Po en Ebro, is de ongecorrigeerde p het
relevante bewijs, want de correctie hoort bij zoeken over de hele kaart.

## 2. De copulakeuze en hoe hard hij staat

Dit is de eerste helft van R4-03. Per cel is de familie gekozen met AIC over
vijftien kandidaten, zoals het manuscript beschrijft. De volledige tabel per
locatie en variabelenpaar staat in `bootstrap_diagnostics.csv` en is als
appendixtabel klaar te zetten.

| familie | gekozen in | familie | gekozen in |
|---|---|---|---|
| Clayton90 | 45 | Clayton0 | 31 |
| Clayton270 | 30 | Clayton180 | 27 |
| Joe270 | 18 | Frank | 9 |
| Joe90 | 9 | Joe180 | 5 |
| Joe0 | 5 | Student | 5 |
| Gumbel270 | 3 | Gumbel90 | 2 |
| Gumbel0 | 1 | | |

**Hoe betrouwbaar is die keuze.** Over de 2000 bootstrap-replicaties per cel:

- de familie die op de volle steekproef wint komt in 140 van de 190
  cellen ook als meest gekozen familie terug
- maar de mediane frequentie van die winnaar is **37%**, met
  kwartielen 28% en 51%
- het mediane aantal verschillende families dat over de replicaties gekozen
  wordt is **12** van de vijftien, maximum 15

De keuze welke familie is dus zelden hard. Dat is geen ramp voor de
transitiekansen, want de intervallen hieronder herselecteren de familie per
replicatie en dragen die onzekerheid dus al in zich. Maar het hoort wel zo in het
artikel: niet alleen welke familie won, ook dat de marge klein is.

## 3. De betrouwbaarheidsintervallen

Mediane breedte van het 95 procent interval rond de milde curve: **0.128**,
kwartielen 0.082 tot 0.213. Ter
vergelijking: de as-correctie van eerder deze week verschoof diezelfde curve met
ongeveer 0,5 bij het floodniveau van het manuscript. De gerepareerde fout was dus
ruwweg drie tot vier keer zo groot als de onzekerheid die eromheen zit.

Waar sluit het interval nul uit, per floodniveau:

| grootheid | niveau | boven nul | onder nul | bevat nul |
|---|---|---|---|---|
| marginaal deel | 0,69 | 46 van 190 | 14 van 190 | 130 van 190 |
| marginaal deel | 0,90 | 26 van 190 | 12 van 190 | 152 van 190 |
| marginaal deel | 0,95 | 16 van 190 | 16 van 190 | 158 van 190 |
| copula-deel | 0,69 | 13 van 190 | 9 van 190 | 168 van 190 |
| copula-deel | 0,90 | 14 van 190 | 8 van 190 | 168 van 190 |
| copula-deel | 0,95 | 13 van 190 | 8 van 190 | 169 van 190 |
| zwaar min mild | 0,69 | 1 van 190 | 2 van 190 | 187 van 190 |
| zwaar min mild | 0,90 | 2 van 190 | 2 van 190 | 186 van 190 |
| zwaar min mild | 0,95 | 1 van 190 | 2 van 190 | 187 van 190 |

Het marginale deel is de stevigste bevinding: op ongeveer een derde van de
locaties is het venster na een droogte aantoonbaar natter dan een willekeurig
venster, vrijwel altijd in de positieve richting. Dat is dezelfde bevinding als
de ECA-kant, langs een andere weg. Het copula-deel en het verschil zwaar-mild
halen op de meeste plekken geen significantie, met de clusters uit sectie 1 als
uitzondering.

## 4. Ebro en Po, de rivieren van het artikel

Bij het floodniveau van het manuscript, quantiel 0,69. Vet sluit nul uit.

### Po

| locatie | per. | variabele | n | copula | stabiliteit | copula-deel | zwaar min mild | toetsen <0,05 |
|---|---|---|---|---|---|---|---|---|
| Cermede / Castelmassa | 1 | drought peak | 76 | Clayton90 | 52% | +0.029 [-0.062, +0.085] | +0.075 [-0.124, +0.147] | 0/4 |
| Cermede / Castelmassa | 1 | mean severity | 76 | Frank | 30% | +0.037 [-0.079, +0.136] | +0.024 [-0.259, +0.095] | 0/4 |
| Cermede / Castelmassa | 2 | drought peak | 88 | Clayton0 | 36% | -0.017 [-0.078, +0.052] | -0.005 [-0.361, +0.081] | 0/4 |
| Cermede / Castelmassa | 2 | mean severity | 88 | Clayton180 | 29% | +0.014 [-0.097, +0.085] | +0.023 [-0.292, +0.091] | 0/4 |
| Piacenza | 1 | drought peak | 79 | Joe180 | 61% | +0.073 [-0.002, +0.138] | +0.008 [-0.051, +0.092] | 4/4 |
| Piacenza | 1 | mean severity | 79 | Joe180 | 61% | **+0.092** [+0.022, +0.157] | +0.025 [-0.337, +0.109] | 3/4 |
| Piacenza | 2 | drought peak | 92 | Clayton270 | 66% | **+0.008** [+0.002, +0.029] | -0.002 [-0.022, +0.027] | 3/4 |
| Piacenza | 2 | mean severity | 92 | Frank | 42% | **+0.020** [+0.003, +0.044] | +0.015 [-0.079, +0.039] | 3/4 |
| Turijn | 1 | drought peak | 85 | Clayton90 | 47% | +0.036 [-0.029, +0.110] | +0.106 [-0.241, +0.162] | 0/4 |
| Turijn | 1 | mean severity | 85 | Frank | 28% | +0.034 [-0.071, +0.131] | +0.015 [-0.235, +0.153] | 0/4 |
| Turijn | 2 | drought peak | 75 | Clayton0 | 46% | -0.041 [-0.104, +0.052] | -0.078 [-0.169, +0.112] | 0/4 |
| Turijn | 2 | mean severity | 75 | Clayton0 | 63% | -0.069 [-0.148, +0.071] | -0.155 [-0.730, +0.256] | 0/4 |

### Ebro

| locatie | per. | variabele | n | copula | stabiliteit | copula-deel | zwaar min mild | toetsen <0,05 |
|---|---|---|---|---|---|---|---|---|
| Haro | 1 | drought peak | 124 | Clayton90 | 88% | +0.065 [-0.049, +0.107] | +0.060 [-0.027, +0.111] | 1/4 |
| Haro | 1 | mean severity | 124 | Clayton90 | 89% | +0.086 [-0.048, +0.142] | +0.039 [-0.024, +0.077] | 1/4 |
| Haro | 2 | drought peak | 120 | Clayton90 | 60% | +0.026 [-0.010, +0.048] | +0.062 [-0.178, +0.098] | 0/4 |
| Haro | 2 | mean severity | 120 | Clayton90 | 86% | **+0.080** [+0.012, +0.114] | geen | 4/4 |
| Tudela | 1 | drought peak | 127 | Clayton90 | 64% | +0.051 [-0.021, +0.093] | +0.091 [-0.037, +0.140] | 0/4 |
| Tudela | 1 | mean severity | 127 | Clayton90 | 75% | +0.077 [-0.016, +0.133] | +0.081 [-0.010, +0.125] | 1/4 |
| Tudela | 2 | drought peak | 111 | Clayton270 | 28% | **+0.024** [+0.008, +0.102] | +0.007 [-0.021, +0.147] | 0/4 |
| Tudela | 2 | mean severity | 111 | Gumbel0 | 22% | **+0.064** [+0.014, +0.131] | +0.067 [-0.070, +0.142] | 3/4 |
| Zaragoza | 1 | drought peak | 114 | Clayton90 | 52% | +0.039 [-0.028, +0.086] | +0.094 [-0.106, +0.154] | 0/4 |
| Zaragoza | 1 | mean severity | 114 | Clayton90 | 81% | +0.092 [-0.020, +0.138] | +0.080 [-0.035, +0.134] | 1/4 |
| Zaragoza | 2 | drought peak | 116 | Frank | 20% | +0.051 [-0.011, +0.099] | +0.047 [-0.089, +0.171] | 1/4 |
| Zaragoza | 2 | mean severity | 116 | Frank | 22% | +0.065 [-0.014, +0.122] | +0.028 [-0.062, +0.119] | 2/4 |

## 5. Wat dit betekent voor de uitspraken in het artikel

| passage | uitspraak | wat de toetsen nu zeggen |
|---|---|---|
| p27 | Po: zwaardere droogte geeft hogere kans, alleen periode 2 | de samenhang is echt, maar in **beide** periodes: periode 1 4/4 toetsen, periode 2 3/4. "Only during the second period" klopt niet meer |
| p28 | Ebro midstream: hogere kans in beide periodes (drought peak) | mager: periode 1 0/4, periode 2 0/4 toetsen. Het echte Ebro-signaal zit bij **mean severity in periode 2**, Haro 4/4 en Tudela 3/4 |
| p27, p28, p30 | conditioneel blijft lager dan unconditioneel | vervalt, dat was de as-fout. Na correctie ligt de conditionele curve op of licht boven de unconditionele |
| p31 | Dnieper Krementsjoek en Dnipro als regio met verhoogde kans | niet toetsbaar op deze data: te weinig droogte-events voor een bootstrap (11 tot 19). Terughoudend formuleren |
| p31 | Tagus La Bazagona, lichte toename in periode 1 | de toetsen vinden La Bazagona juist in **periode 2**, 4/4 voor drought peak en 4/4 voor mean severity, het op een na sterkste punt van de kaart |
| p34 | robuuste systemen: Po en Ebro | houdt stand en wordt sterker: Po Piacenza en Ebro periode 2 zijn nu met vier onafhankelijke toetsen onderbouwd. Tagus La Bazagona hoort in dat rijtje thuis |

En de bevinding die er nog niet in staat: het negatieve cluster. Vistula Turon en
Weser in periode 1, waar zwaardere droogte de kans verlaagt. Dat is fysisch
interpreteerbaar, bodemvochtdeficit dat de eerste neerslag bufffert, en het is
precies het soort mechanisme waar R4-04 om vraagt.

## 6. Controles en diagnostiek

- **Seriele afhankelijkheid.** Lag-1 correlatie tussen opeenvolgende droogtes:
  mediaan 0.082 absoluut, maximum 0.505. De circulaire
  blokbootstrap geeft intervallen die mediaan 1.00 keer zo breed
  zijn als de gewone, kwartielen 0.94 en
  1.07. De iid-intervallen zijn dus niet merkbaar te smal
- **Bias.** Mediane afwijking tussen bootstrapmediaan en puntschatting
  +0.0012, uitersten -0.0259 en +0.1035.
  Percentiel-intervallen volstaan, een biascorrectie is niet nodig
- **Mislukte replicaties.** Mediaan 0 van de 2000, maximum
  5. Niets weggegooid op grond van de uitkomst
- **Puntsgewijs tegen simultaan.** Een band die over alle 101 punten tegelijk
  geldt zou mediaan 70 procent breder zijn
- **Dekking.** 190 van de 192 cellen. De 2 ontbrekende zijn Dnieper
  Cherson periode 1, elf droogte-events, te weinig voor een bootstrap

## 7. Voorstel voor het artikel

**Nog niet uitgevoerd. Ter goedkeuring aan Floris, daarna eventueel co-auteurs.**

### Methoden, 2.4.2, twee alinea's erbij

> Confidence intervals for the transition probabilities were obtained by a
> non-parametric bootstrap over drought events (B = 2000). For each resample the
> full estimation procedure was repeated, including marginal parameter estimation
> and copula selection by AIC, so that the intervals reflect both parameter and
> model-selection uncertainty. Intervals are pointwise 95% percentile intervals;
> differences between severity levels were bootstrapped directly. In addition,
> the existence of drought-severity dependence was tested per location with a
> permutation test in which the null distribution incorporates the same
> fifteen-family selection step, complemented by Kendall's tau, Spearman's rho
> and Hoeffding's D.

> The difference between the conditional and unconditional exceedance
> probability was decomposed into a marginal component, comparing post-drought
> windows with arbitrary four-week windows, and a dependence component,
> measuring whether the magnitude of the subsequent peak depends on drought
> severity. Only the latter is a property of the copula.

### Resultaten, 3.2 en 3.3, de kern van de herschrijving

> Across all basins, conditioning on a preceding drought is associated with a
> modestly higher probability of a high runoff peak, driven mainly by the
> marginal component. Dependence on drought severity is not detectable at most
> locations, but emerges consistently at specific rivers: the Po (midstream, both
> periods), the Ebro and the Tagus (second period), where more severe droughts
> increase the probability of a subsequent high peak, and, with opposite sign,
> the Vistula and Weser (first period), where more severe droughts decrease it.

### Appendix

- de tabel met per cel de gekozen familie, de stabiliteit ervan, en de
  transitiekansen met intervallen op drie floodniveaus, uit
  `bootstrap_diagnostics.csv` en `transition_ci.csv`
- de verschilcurve met band per rivier, `figures/ci_per_river.png`

### Revision Notes

Melden, niet laten vinden: de F_Y-reparatie, de einddetectie-reparatie en het
effect daarvan op de gepubliceerde cijfers, met de changelog als bron. De toon:
het uitwerken van R4-03 bracht twee implementatiefouten aan het licht, de
beschreven methode was correct, de cijfers zijn opnieuw berekend en de
conclusies zijn waar nodig aangepast.

## 8. Beperkingen, die mee de tekst in moeten

1. De bootstrap hertrekt de droogte-events en houdt het aantal events, de
   SRI-standaardisatie en de quantieltransformatie vast. De intervallen zijn een
   ondergrens op de totale onzekerheid.
2. De zware curve rust op weinig events, mediaan k_major 1.
   Waar dat aantal klein is, is de curve staart-extrapolatie van de copula.
3. De intervallen zijn puntsgewijs en niet gecorrigeerd voor 190 gelijktijdige
   cellen. Tellingen over locaties heen moeten daar rekening mee houden; voor
   vooraf benoemde locaties is de ongecorrigeerde p het relevante getal.
4. Met 1000 permutaties is de kleinst mogelijke p 0,001; uitspraken over
   FDR-overleving steunen daarom op de analytische p van tau en rho.
5. De Dnieper valt grotendeels buiten de analyse door te weinig events.
6. De referentiegroepen van conditioneel en unconditioneel verschillen: events
   tegen weken. Dat lost geen enkele as-keuze op.

## Bestanden en figuren

- `transition_ci.csv`, per cel en grootheid de puntschatting en de grenzen
- `bootstrap_diagnostics.csv`, per cel de copulakeuze, stabiliteit en diagnostiek
- `selection_frequency.csv`, de familiekeuze per cel over de replicaties
- `../2026-09-02_dependence_tests/dependence_tests.csv`, de vier toetsen
- `figures/ci_example.png`, een cel groot met banden en de verschilcurve
- `figures/ci_decomposition.png`, marginaal tegen copula-deel, met banden
- `figures/ci_per_river.png`, de verschilcurve met band per rivier
- `figures/dependence_overview.png`, sterkte en richting van de samenhang per cel
