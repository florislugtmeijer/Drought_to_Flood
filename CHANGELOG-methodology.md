# Methodologische wijzigingen

Elke wijziging die de uitkomsten kan veranderen, met de reden en het effect.
Bron voor de Revision Notes. Nieuwste bovenaan.

Beslissingen die nog open staan: `docs/open-decisions.md`. Voorstellen van
Floris: `docs/proposed-changes.md`. Werk dat eruit volgt: `docs/todo.md`.

---

## 2026-09-04 (tweede) — Strengere drempels getoetst en afgewezen, 0,5 met gespiegeld floodniveau blijft

**Beslist door Floris op 4 september 2026.** De drempel blijft 0,5 met het
gespiegelde floodniveau `norm.cdf(0.5) = 0,6915`. **Aan de cijfers verandert
niets**, dit is de bestaande configuratie. De strengere variant is doorgerekend als
gevoeligheidscontrole en afgewezen.

### Wat is doorgerekend

Droogte bij SRI onder -1 in plaats van -0,5, met het floodniveau meegespiegeld naar
`norm.cdf(1) = 0,8413`. Volledig gescheiden van de hoofdanalyse: eigen scripts
(`scripts/27` tot `30`), eigen resultaatmappen met `strict` in de naam, geen
bestaande code aangepast. De referentie op 0,5 is in dezelfde run met dezelfde seeds
opnieuw berekend. Rapport in `results/2026-09-04_strict_definition_report/`.

### Wat de strengere drempel oplevert

De aanleiding was terecht: bij 0,5 kan een week tegelijk droogte en flood zijn. Dat
gebeurt bij 1440 van de 26.917 droogteweken, dus 5,3 procent. Bij drempel 1 daalt
dat naar 38 van de 11.361, dus 0,3 procent. De strengere definitie scheidt de twee
toestanden dus daadwerkelijk.

### Waarom hij toch is afgewezen

**Het venster na de droogte meet dan iets anders.** Een droogte eindigt zodra de SRI
boven de drempel komt. Bij drempel 1 is dat boven -1, en dan zit de rivier vaak nog
in milde droogte. Gemeten over de vier weken na afloop: 46 procent van die weken ligt
onder SRI -0,5, tegen 36 procent van alle weken. Bij drempel 0,5 is dat 22 procent,
dus daar betekent het einde dat de omstandigheden echt zijn omgeslagen. Gevolg: het
marginale deel draait van teken om, van +0,054 bij 0,5 naar -0,098 bij 1,0, en het
venster na een strenge droogte is droger dan een willekeurig venster in 136 van de
187 cellen. Dat is een definitieartefact, geen hydrologische bevinding.

**De categorieën uit pagina 22 vallen samen.** De grens voor een milde droogte staat
daar op drought peak 1. Met droogtedrempel 1 heeft elke droogte per definitie een
piek van minstens 1, dus valt alles onder mild en wordt de milde curve gelijk aan de
onafhankelijkheidslijn. Dat gebeurt in 82 van de 188 cellen.

**De statistische basis wordt dunner.** Droogte-events per cel gaan van mediaan 85
naar 55, de mediane intervalbreedte rond de milde curve van 0,128 naar 0,237, en het
aantal cellen zonder enkele zware droogte van 45 naar 94.

### Eén uitkomst die als beperking in de tekst hoort

De locatiespecifieke severity-afhankelijkheid is **niet robuust onder de
drempelkeuze**. Over de 186 cellen die in beide analyses zitten is de correlatie
tussen Kendall's tau bij 0,5 en bij 1,0 slechts +0,12, en het teken komt in 52
procent van de cellen overeen, ongeveer wat muntje opgooien geeft. Van de achttien
cellen die bij 0,5 door minstens twee toetsen werden aangewezen, blijven er twee
over bij 1,0. De gemeten spreiding van het verschil tussen beide tau's is 0,129,
terwijl pure toevalsvariatie bij 55 events al 0,093 geeft.

Dat raakt de hoofdanalyse, niet alleen deze variant. De twaalf sterke cellen die in
`results/2026-09-02_copula_bootstrap/report.md` staan, waaronder Po Piacenza en Ebro,
zijn onderbouwd bij drempel 0,5 en verdwijnen bij 1,0. Wie ze in het artikel noemt
moet die koppeling aan de drempel expliciet maken. Zie D-22.

### Concept voor de Revision Notes, bij R4-01

> We additionally tested a stricter event definition in which droughts are defined at
> SRI < -1 and the flood level is mirrored accordingly to the 84.13th percentile. This
> reduces the overlap between drought and flood weeks from 5.3% to 0.3% of drought
> weeks, but it changes what the post-event window measures: after a drought defined
> at SRI < -1, 46% of the following four weeks still fall below SRI -0.5, against 36%
> of all weeks, so the window captures recovery from within drought conditions rather
> than a transition to wet conditions. It also collapses the minor and severe drought
> categories, since every drought then exceeds the minor threshold by construction. We
> therefore retain the -0.5 threshold with the mirrored flood level. We note, however,
> that the location-specific dependence results are sensitive to this choice: the rank
> correlation between Kendall's tau at the two thresholds is 0.12 across the 186
> comparable cells.

---

## 2026-09-04 — Telcriterium voor de toenames op pagina 31: de onafhankelijkheidstoetsen

**Beslist door Floris.** Sluit D-19. Schrijfwerk in T-60. Raakt R4-03, R1-07, R1-08,
D-17 en D-18.

### Wat er verandert

Pagina 31 telt locaties waar een zwaardere droogte de transitiekans verhoogt, 5, 6,
7 en 9, zonder te zeggen wanneer iets als toename telt. Er is nu een criterium: een
cel telt als toename als minstens drie van de vier onafhankelijkheidstoetsen uit
`scripts/25_dependence_tests.py` p < 0,05 geven en Kendall's tau positief is, en als
afname bij negatieve tau. De vier toetsen zijn Kendall's tau, Hoeffding's D, een
permutatietoets op de copulafit met de familieselectie in de nulverdeling, en de
permutatie-p van het copula-deel bij floodquantiel 0,69. 1000 permutaties, seed 43,
cellen met minder dan 15 events uitgesloten.

### Waarom

De gepubliceerde tellingen zijn op het oog gemaakt. Een drempel van +0,02 op het
mediane verschil tussen de zware en de milde curve reproduceert ze bijna, post-fix
5, 4, 7, 8, maar dat criterium negeert onzekerheid terwijl R4-03 daar juist om
vraagt. De zware curve rust op mediaan één event boven de zware drempel. Van de 24
toenames onder dat criterium overleeft er nul het bootstrapinterval bij 0,69 en twee
de toetsen. De toetsen meten de samenhang tussen droogtezwaarte en piek over alle
events van een cel, en dat is wat het verschil tussen de curves hoort uit te
drukken. Volledige weging, acht criteria naast elkaar, en de afwijzing van het
mediaancriterium in vijf punten: `docs/open-decisions.md` D-19 en
`results/2026-09-04_increase_criterion/report.md`.

### Effect op de resultaten

Geen berekening verandert, wel de tellingen in de tekst. Volgorde periode 1 drought
peak, periode 1 mean severity, periode 2 drought peak, periode 2 mean severity:

| | gepubliceerd | nu |
|---|---|---|
| toenames | 5, 6, 7, 9 | 1, 2, 2, 4 |
| afnames | niet gegeven | 2, 1, 0, 0 |

Toenames bij Po Piacenza in beide periodes en beide variabelen, Ebro Haro en Tudela
in periode 2 voor mean severity, Tagus La Bazagona in periode 2 voor beide
variabelen, en Danube Aschach in periode 1 voor mean severity. Afnames bij Vistula
Turon in periode 1 voor beide variabelen en Weser Bodenwerder in periode 1 voor
drought peak. De toename van periode 1 naar 2 blijft, van 3 naar 6 cellen.

Van de met naam genoemde locaties op pagina 31 houdt de Dnieper niet stand,
verschuift La Bazagona van periode 1 naar 2, is Vila Velha de Rodao niet toetsbaar
door het ontbreken van een zware curve, en blijft bij Vistula en Oder midstream
alleen een puntschatting over waarvan elk interval nul bevat.

### Kanttekening voor de tekst

Over 190 cellen overleeft geen enkele toets een Benjamini-Hochberg-correctie. De
telling is beschrijvend. Voor de vooraf benoemde locaties is de ongecorrigeerde p
legitiem, want daar wordt een aangewezen claim getoetst. Dat onderscheid moet in de
tekst.

---

## 2026-09-02 — De copula-kant gerepareerd: F_Y, het floodvenster en de duur

Uit de review van de copula-kant, T-11, kwamen vijftien bevindingen. Vier daarvan
zijn besloten en doorgevoerd. De review zelf en de volledige lijst staan in
`results/2026-09-02_copula_definition_variants/` en
`results/2026-09-02_copula_corrected/`.

### R-01, de ontbrekende stap F_Y

Pagina 21 van het manuscript geeft de formule

    P(Y > y | X >= x) = (1 - F_X(x) - F_Y(y) + C(F_X(x), F_Y(y))) / (1 - F_X(x))

De code stopte `y` rechtstreeks in de copula in plaats van `F_Y(y)`. Omdat een
copula alleen rangnummers kent, stond de conditionele curve daardoor op de rang van
de post-droogte piek terwijl de unconditionele curve op de runoff-quantielschaal
stond. In de figuren werden ze op dezelfde x-as gezet.

Dit is geen methodewijziging maar een reparatie. De regel die het oplost,
`prob_flood = dist2.cdf(Y, *params2)`, stond al in de bron en werd nergens gelezen.
Dat is meteen de verklaring waarom de gefitte marginalen ongebruikt bleven, wat in
de review als aparte bevinding R-08 stond.

**Effect op de cijfers.** Bij het floodniveau van het manuscript, quantiel 0,6915,
gaat de transitiekans na een milde droogte van mediaan 0,274 naar 0,775. Het gat met
de unconditionele lijn gaat van -0,422 naar +0,057, en het aantal cellen waar de
conditionele curve onder de unconditionele ligt van 188 van de 192 naar 33.

De vergelijking van milde tegen zware droogte verandert niet. Die twee staan
allebei op de rangschaal en waren onderling altijd al consistent.

### R-02, het floodvenster

`extract_events` nam het maximum vanaf de laatste week van de droogte zelf, en
omdat `.sel` met een slice aan beide kanten inclusief is, telde dat venster vijf
weekpunten. Pagina 19 zegt vier weken na afloop. Bovendien sloot
`calculate_rolling_max`, die de unconditionele curve voedt, de eigen week wel uit,
dus de twee kanten waren onderling ongelijk.

Gecorrigeerd naar vier weken na afloop, zonder droogteweek.

**Effect.** Mediaan verschuiving van de conditionele curve 0,010, p90 0,045,
maximaal 0,399. De gekozen copulafamilie kantelt in 30 van de 96 locatie-periodes.
Dertig droogtes aan het einde van de reeks vallen weg, van de 7925.

### R-03, de duur in mean_drought_severity

De deling gebruikte einde min begin, en dat is een week te kort. Een droogte over
twee weekpunten werd door 1 gedeeld, een droogte van één weekpunt door nul, met
NaN als gevolg. Gecorrigeerd naar het aantal weekpunten.

**Effect.** Alleen op `mean_drought_severity`. Mediaan verschuiving 0,033, p90
0,108, maximaal 0,231. Familie kantelt in 36 van de 96. Zeven eenweekse droogtes
komen terug in de analyse.

### Marginalen: parametrisch

Het manuscript beschrijft op pagina 21 dat de marginale verdelingen met maximum
likelihood zijn geschat en met chi-kwadraat geselecteerd. De code gebruikte voor de
droogtezijde de empirische verdeling. Besloten is de tekst te volgen.

**Effect.** Mediaan verschil met de empirische route -0,004, mediaan absoluut 0,03,
p90 0,10. Geen systematische richting. Wel valt de zware curve weg bij 24 van de 192
cellen, en dat zijn precies de cellen met `k_major = 0`, dus zonder enkele zware
droogte. De empirische route maakte daar wel een curve, uit de bovenste procent van
een gesimuleerde copula op nul waarnemingen.

### Verder in dezelfde beweging

- **Seed toegevoegd.** De gepubliceerde berekening seedde niet, dus was niet exact
  reproduceerbaar. Eigen seedstroom per locatie-periode via
  `SeedSequence(42).spawn(96)`
- **Dode code verwijderd.** `flood_score = 0.9` voedde alleen `prob_flood_fixed`,
  dat nergens werd gelezen. De regel in `docs/open-decisions.md` die het "het vaste
  floodquantiel in `fit_copula`" noemde is gecorrigeerd
- **Figuur 1 en 2 op dezelfde precisie.** Het Z-oppervlak gebruikte een tweede
  trekking van 10.000 tegen 100.000 voor de curves
- **Niet-eindige trekkingen.** `random` levert bij de Joe-families 0,1 tot 0,4
  procent NaN. De bron liet die stil wegvallen bij een `>=` vergelijking, nu worden
  ze geteld en verwijderd zodat teller en noemer dezelfde steekproef gebruiken
- **`src/dtf/copula.py` aangelegd**, T-46. De copula-kant zat nog in de notebook.
  Geverifieerd tegen de eerdere run: bit-identiek op de afronding na

### Wat dit voor de tekst betekent

Vier passages vergelijken de conditionele curve met de unconditionele lijn en
draaien van teken om: pagina 27 tweemaal, pagina 28 en pagina 30. De zin op pagina
27 dat de zwaarte van de droogte het effect gedeeltelijk terugdraait blijft staan,
de eerste helft van die redenering niet. Zie
`results/2026-09-02_copula_definition_variants/manuscript_claim_check.md`.

Wat er nog niet in zit zijn de betrouwbaarheidsintervallen, de tweede helft van
R4-03.

---

## 2026-09-02 (tweede) — Einddetectie van events gerepareerd, met duur en flood-piekvenster

**Beslist door Floris op 2 september 2026, na de code-review van de ECA-keten.**
Drie reparaties in `extract_events`, dit verandert gepubliceerde cijfers. Branch
`eca-endtime-fix`, commit "ECA-review: einddetectie, duur en quantile_max_value
gerepareerd". Het volledige gevoeligheidsraster wordt opnieuw gedraaid naar
`results/2026-09-02_sensitivity_grid_endfix/`; de pre-fix run blijft staan in
`results/2026-09-01_sensitivity_grid/` als vergelijkingsbasis.

### 1. end_time van eenweekse events lag een week te laat

De einddetectie zocht de eerste week waarvan de vólgende week nul is, maar eiste
`valid_time > starttijd`. Daardoor viel de eigen index af, en bij een event van
precies één week is dat juist de index die het einde is. Het einde schoof dan door
naar het eerstvolgende gat verderop.

**Bewijs, uitputtend.** Alle 1024 patronen van tien weken, vergeleken met een
onafhankelijke implementatie: 2816 events, waarvan 1280 met een fout einde, en
alle 1280 zijn eenweekse events. Elk event van twee weken of langer was goed. Na
de reparatie: 0 afwijkingen in start, einde én duur over dezelfde 2816.

**Omvang.** Een derde van de droogtes duurt precies één week, gemeten 33,5 procent
over 10 locaties maal 2 periodes bij threshold 0,5. De floodzijde heeft dezelfde
fout maar die raakt de ECA niet, want van floods wordt alleen `start_time`
gebruikt.

**Waarom het de toets raakt.** `end_time` is het matching-anker. Het venster na
een eenweekse droogte in week t was daardoor (t+1, t+5] in plaats van (t, t+4]:
de methode miste week t+1, precies de vertraging waar de samenhang het sterkst
zit, en pakte in plaats daarvan t+5. De Monte Carlo gebruikte dezelfde verschoven
ankers, dus de toets was intern consistent maar mat het verkeerde venster.

### 2. duration_weeks van tijdspanne naar telling

Was `einde min start` in weken, dus nul voor een eenweeks event. Met reparatie 1
zou dat `mean_drought_severity = NaN` geven en zouden eenweekse droogtes uit de
copula vallen. Nu een telling: een event van één week duurt 1, van drie weken 3.
**Let op: dit verschuift de duur van elk meerweeks event met één**, en daarmee
`mean_drought_severity` van elk event. Raakt de ECA niet, wel de copula-invoer
van T-11.

### 3. quantile_max_value strikt na het event

Het venster was `slice(einde, einde + 4 weken)`, aan beide kanten inclusief: vijf
weekwaardes waarvan de eerste de laatste week van de droogte zelf. Het manuscript
zegt "within four weeks after a drought ends" en de matching gebruikt
(einde, einde + venster]. Nu doet dit veld hetzelfde. Eindigt een event op de
laatste week van de reeks, dan is de waarde NaN, en de copula filtert die al weg.
Raakt de ECA niet, wel de copula-invoer van T-11.

### Gemeten effect op de ECA-baseline

96 runs, threshold 0,5, floodpercentiel 0,6915, venster 4, seed per locatie,
vergeleken met dezelfde regels uit het pre-fix raster:

| | pre-fix | post-fix |
|---|---|---|
| droogte-, floodaantallen, n_weeks | — | **0 van 96 veranderd**, zoals hoort |
| matches, totaal | 4764 | **5503, plus 15,5 procent** |
| runs met meer matches | | 89 omhoog, 1 omlaag |
| significant van 96, Monte Carlo | 91 | 92 |
| significant van 96, analytisch | 90 | 91 |
| gepoolde rate periode 1 | 0,5994 | 0,6878 |
| gepoolde ratio periode 1 | 1,59 | **1,82** |
| gepoolde ratio periode 2 | 1,55 | **1,81** |

De ene locatie die significant wordt is Rostov in periode 1, 0,0599 naar 0,0268.
**De fout drukte de samenhang dus systematisch omlaag.** Dat is de goede kant op
voor de bevinding, maar het betekent ook dat elke eerder gerapporteerde ratio een
onderschatting was, en dat moet eerlijk in de Revision Notes.

### Wat opnieuw moet

- het volledige gevoeligheidsraster, 12000 runs, loopt
- Tabel 3 zodra T-54 wordt uitgevoerd, met de gerepareerde code
- de conceptteksten en figuren van T-58, zodra het nieuwe raster er is
- **T-11 let op, en dit is dringend.** De copula-review van vandaag heeft R-02 en
  R-03 onafhankelijk ook gevonden en gecompenseerd in `src/dtf/copula.py`, met
  `flood_peak_after_drought` en `mean_severity_per_week`, expliciet als
  tijdelijke plek gemarkeerd. Twee gevolgen van de ECA-reparatie:
  1. `mean_severity_per_week` deelde door duur plus één. Nu `duration_weeks` uit
     `extract_events` zelf al een telling is, zou dat dubbel corrigeren. De
     functie deelt daarom nu rechtstreeks door de duur, en beide helpers geven
     bewezen exact dezelfde waardes als de velden uit de gerepareerde
     `extract_events`. Scripts 20, 22 en 25 blijven werken
  2. **de copula-runs van vandaag zijn gedraaid met de oude `end_time`.** Voor
     een derde van de droogtes, de eenweekse, stond het floodvenster daardoor
     alsnog een week te laat, ook ná de R-02-correctie, want die corrigeerde het
     venster ten opzichte van een anker dat zelf fout was.
     `results/2026-09-02_copula_corrected/` en de bootstrap moeten dus opnieuw
     zodra dit gemerged is

---

## 2026-09-02 — Gevoeligheidsraster uitgebreid naar de volle kruising

**Vervolg op de entry hieronder.** Het raster van 29 cellen is uitgebreid naar de
volledige kruising van de drie assen, 125 cellen en 12000 runs. De 29 bestaande
cellen zijn niet opnieuw berekend, hun cijfers zijn ongewijzigd. Draaitijd van het
tweede deel 315,8 minuten. `results/2026-09-01_sensitivity_grid/`.

**Waarom.** In de eerste opzet liep het venster alleen als lijn door de baseline,
dus over de interactie tussen het venster en de twee drempels viel niets te zeggen.
Dat stond als beperking in de tekst. Die beperking is nu weg.

### Wat de volle kruising erbij oplevert

**193 van de 250 cel-periodes houden stand bij p < 0,05.**

**De SRI-drempel doet niets, en dat geldt bij elk venster.** Bij floodpercentiel
0,60 en periode 1 loopt de ratio over de drempel-as van 3,58 naar 2,15 bij venster
1, van 1,46 naar 1,42 bij venster 4 en van 1,12 naar 1,15 bij venster 12. Overal
vlak, terwijl het aantal droogtes met bijna een factor zes daalt.

**Het floodpercentiel doet alles, en het venster versterkt dat.** Niet-significante
cel-periodes per venster, van de 50: 7 bij één week, 6 bij twee, 12 bij vier, 15
bij acht en 17 bij twaalf. Bij elk venster liggen ze allemaal in de hoek met een
hoog floodpercentiel.

**De uiterste hoek herstelt bij geen enkel venster.** Bij drempel 1,5 en percentiel
0,95 is de ratio 0,85 / 0,78 / 0,75 / 0,73 / 0,76 in periode 1 over de vijf
vensters, en 0,62 tot 0,77 in periode 2. Nergens significant. **Dat een droogte
minder vaak door een extreme flood wordt gevolgd dan bij toeval is dus geen artefact
van de vensterkeuze.** Dat maakt het een steviger aanknopingspunt voor R4-04 dan het
was.

### Een cijfer dat niet vergeleken mag worden

De ratio's zijn **niet tussen vensters vergelijkbaar.** De nullijn stijgt van 0,113
bij één week naar 0,737 bij twaalf, dus de ratio zakt per constructie naar 1. Wat
wel iets zegt is de omvang van de excess bij een kort venster: 38,0 procent van de
droogtes wordt binnen één week door een flood gevolgd waar 11,3 procent verwacht is.
Dit moet in de tekst staan, anders leest iemand de dalende reeks als een
verzwakkend effect.

### Sanity checks

Alle checks schoon: 12000 regels, geen duplicaten, alle 250 nulverdelingen
aanwezig, geen NaN, `match_count_trigger` gelijk aan `observed_matches_mc` in alle
12000 runs, en het aandeel weken monotoon in beide assen bij alle 480 reeksen. 25
runs niet toetsbaar, alle 25 Vila Velha de Rodao bij drempel 1,5.

### Codewijziging

`scripts/09_sensitivity_grid.py`: `CELLS` is de volle kruising, en de ETA-teller is
gerepareerd. Die telde overgeslagen cellen mee terwijl die niet vooraan in de
volgorde staan, waardoor de gemelde resterende tijd onzin was. **Raakt geen enkel
resultaat**, alleen de voortgangsmelding.

---

## 2026-09-01 (zesde) — Gevoeligheidsanalyse gedraaid: de drempel doet weinig, het floodpercentiel alles

**Uitkomst van T-10, het antwoord op R4-01.** `results/2026-09-01_sensitivity_grid/`,
2784 runs in 107,5 minuten, 29 cellen. Geen wijziging aan de gepubliceerde
berekening, dit is onderzoek.

### Opzet

Drie assen, zoals de reviewer ze noemt. SRI-drempel 0,25 tot 1,5, floodpercentiel
0,60 tot 0,95, venster 1 tot 12 weken. Een vol 5 maal 5 vlak van drempel maal
percentiel op venster 4, plus het venster als losse lijn door de baseline. De
volledige drieweg-interactie zit er niet in, en dat hoort als inperking in de
tekst.

**De kop is een gepoolde toets over alle 48 locaties samen**, de aggregatie uit
Donges et al. 2016 sectie 2.2 vergelijking 6, en niet een telling van hoeveel
locaties significant zijn. Dat haalt het multiple-testing-probleem weg en laat
niet-toetsbare locaties vanzelf wegvallen. **Dit moet in de methodensectie
beschreven worden**, met de verwijzing erbij.

### Uitkomst

**De SRI-drempel doet vrijwel niets.** Bij floodpercentiel 0,60 blijft de ratio
tussen 1,42 en 1,59 terwijl de drempel van 0,25 naar 1,5 gaat en het aantal
droogtes van 4220 naar 724 zakt. Alle p < 0,0001. Dat is een sterk antwoord op
"somewhat arbitrary".

**Het floodpercentiel doet alles.** Ratio in periode 1, vet is niet significant:

| | thr 0,25 | 0,5 | 0,75 | 1,0 | 1,5 |
|---|---|---|---|---|---|
| fq 0,95 | 1,41 | 1,22 | **1,02** | **0,92** | **0,75** |
| fq 0,90 | 1,52 | 1,35 | 1,16 | **1,04** | **0,78** |
| fq 0,80 | 1,64 | 1,54 | 1,39 | 1,27 | **1,05** |
| fq 0,6915 | 1,58 | 1,59 | 1,49 | 1,39 | 1,28 |
| fq 0,60 | 1,46 | 1,54 | 1,55 | 1,51 | 1,42 |

**38 van de 50 cel-periodes houden stand, 12 niet, en die 12 zitten allemaal in de
strenge hoek rechtsboven.** In de uiterste hoek zakt de ratio tot 0,71: bij een
strenge droogte- én flooddefinitie wordt een droogte **minder** vaak door een flood
gevolgd dan bij toeval. Consistent met
`results/2026-08-23_flood_magnitude_test/`. Aanknopingspunt voor R4-04, maar als
verklaring nog niet getoetst.

**Het venster.** Ratio 3,36 bij één week, 2,19 bij twee, 1,59 bij vier, 1,17 bij
twaalf, overal p < 0,0001. De samenhang concentreert zich in de eerste weken. Deels
meetkundig, want bij een groeiend venster nadert de nullijn vanzelf 1.

**De twee periodes zijn bijna identiek**, zelden meer dan 0,05 verschil in ratio.

### Wat dit voor het manuscript betekent

Dit is geen eenduidig gunstig antwoord en het moet ook niet zo worden opgeschreven.
Op één as is de bevinding robuust, op de andere valt hij weg. De eerlijke lijn: de
samenhang bestaat bij matige tot forse floods en verdwijnt bij de extreemste, en
dat is inhoudelijk het interessantste resultaat van de hele analyse.

**Beperking die mee moet.** De aggregatieve nulhypothese randomiseert elke locatie
onafhankelijk, en onze locaties zijn dat niet: drie punten op de Dnieper, drie op
de Don, Rijn en Maas onder dezelfde weersystemen. Ruimtelijke correlatie maakt de
werkelijke nulvariantie groter, dus **de gepoolde p valt te laag uit.**
Randomiseren op riviersniveau zou het oplossen, dat is niet gedaan.

### Twee dingen die geen fout zijn en waar iemand over zal struikelen

- **De baselineratio is 1,59, waar het referentieraster 1,66 gaf.** Twee
  verschillende nullijnen. Het oude cijfer gebruikte de analytische verwachting,
  dit het gemiddelde van de Monte Carlo-nulverdeling
- **Het aantal events daalt niet monotoon met de drempel.** Magdeburg periode 1
  gaat van 82 naar 83 naar 73 naar 52 naar 15. Een event is een aaneengesloten
  reeks weken, dus een strengere drempel knipt een lang event in tweeën. Het
  aandeel wéken daalt wél overal netjes, 0 afwijkingen van 480 reeksen op beide
  assen. Hetzelfde punt als T-29

---

## 2026-09-01 (laatste) — Quantielreferentie blijft de periode zelf, drempels worden ontkoppeld voor de gevoeligheidsanalyse

**Beslist door Floris**, na de rerun op threshold 0,5. Sluit P-02 en T-02 opnieuw,
nu op cijfers die bij de gekozen threshold horen. Raakt T-02, T-03, T-10, T-29.

### De berekening blijft ongewijzigd

De floodquantielen worden bepaald tegen de **volledige dagelijkse afvoerreeks van
de periode zelf**, dus `quantile_reference="daily"` en `reference_window=None`. Dat
is precies wat de gepubliceerde code doet.

**Effect op de resultaten: geen.** Geen enkel cijfer in Tabel 3 verandert door deze
beslissing.

Waarom dat een keuze is en niet vanzelfsprekend: de rerun op 0,5 haalde het
cijfermatige argument tegen aanpassen weg, 89 van 96 significant tegen 90, en het
symmetrie-argument bleek zelfs vóór aanpassen te pleiten. Wat overblijft is de
inhoudelijke verdediging, en die is gekozen: de 69,1e percentiel van de dagelijkse
verdeling is een herkenbare hydrologische grootheid, het debiet dat op ongeveer 31
procent van de dagen wordt overschreden. De variant zou dat opgeven voor een
relatieve drempel die per constructie 30,9 procent van de weken aanmerkt bij elke
rivier, los van elk fysiek niveau. Voor een studie die 16 rivieren met verschillende
regimes vergelijkt is dat een verlies.

Volledige weging in P-02, cijfers in `results/2026-09-01_reference_grid/`.

### Nieuwe tekstcorrectie die hieruit volgt

De methodensectie zegt "quantiles relative to the entire dataset for each
location". **Dat beschrijft de code niet.** De referentie is de periode, 5479 dagen,
niet de volledige dataset van 10958 dagen. In D-11 stond dat de tekst hier al mee
overeenkwam, en dat was onjuist.

De zin moet dus zeggen dat de quantielen per periode worden bepaald, tegen de
dagelijkse reeks van die periode. Dat valt samen met de eis uit D-13 om te melden
dat de drempels per periode opnieuw worden bepaald en hoeveel ze verschuiven. Zie
T-29.

### Drempels ontkoppelen voor de gevoeligheidsanalyse

`Intensity_calc` koppelt de SRI-drempel en het floodpercentiel via
`threshold_floods = norm.cdf(threshold)`, dus één parameter voor beide kanten. R4-01
vraagt ze als twee aparte parameters. **Besloten: ze worden ontkoppeld.**

Uitvoering nog te doen, zie T-10. Randvoorwaarde: de default moet de gekoppelde
waarde blijven, dus `flood_quantile=None` betekent `norm.cdf(threshold)`, zodat de
gepubliceerde berekening bit voor bit hetzelfde blijft. Dat is met de controlecel te
bewijzen.

---

## 2026-09-01 (vijfde) — Code voor de gevoeligheidsanalyse: drempels ontkoppeld, Monte Carlo versneld, seed per locatie

**Voorwerk voor T-10 en R4-01.** Raakt `src/dtf/pipeline.py`. Eén van de vier
wijzigingen verandert cijfers, en dat is de seed. De andere drie zijn bewezen
identiek.

### De twee drempels zijn losgemaakt

`Intensity_calc` leidde het floodpercentiel af uit de SRI-drempel met
`threshold_floods = norm.cdf(threshold)`. Eén parameter bestuurde dus beide
kanten, en de as die de reviewer vraagt bestond niet. Zie D-11.

- `Intensity_calc(SRI, flood_quantiles, threshold, flood_quantile=None)`. `None`
  betekent `norm.cdf(threshold)`, de gepubliceerde berekening
- `drought_flood_p_value_trigger_ECA(..., flood_quantile=None)` geeft hem door,
  **ook aan de regel die `pct_weeks_flood` berekent.** Zonder dat laatste zou die
  kolom bij een losse flooddrempel de verkeerde drempel rapporteren
- `extract_events(..., event_peak_window=None)`. `period_after_event` deed dubbel
  werk: matching-venster van de toets én venster voor `quantile_max_value`. Zodra
  het venster een as van de gevoeligheidsanalyse wordt betekent één parameter
  anders twee dingen. Raakt de p-waardes niet, `quantile_max_value` zit niet in
  dat pad. Nodig voor T-11
- `mc_null_counts` in de returndict. De volle nulverdeling werd al berekend en
  daarna weggegooid. Nodig om over locaties te poolen, zie de volgende entry

`threshold` slaat na deze wijziging alleen nog op de droogtezijde. Niet hernoemd,
want dat breekt `scripts/07_reference_grid.py`. Staat als waarschuwing in de
docstring.

**Effect op de resultaten: geen.** Alle defaults zijn de gepubliceerde
berekening.

### Monte Carlo gevectoriseerd

`monte_carlo_p_value` telde de treffers met een Python-lus over de droogtes,
binnen de lus over 10000 simulaties. Dat zijn circa een miljoen piepkleine
numpy-aanroepen per run, en uit het profiel bleek dat **62,4 procent van de
looptijd** te zijn. Vervangen door twee `searchsorted` per simulatie.

**De trekking is niet aangeraakt.** Zelfde `rng.choice`, zelfde volgorde, zelfde
verbruik van de stroom. Alleen het tellen is anders opgeschreven.

**Effect op de resultaten: geen, en dat is hard gecontroleerd.** 24 aanroepen van
10000 simulaties, elementsgewijs vergeleken met de oude implementatie: nul
verschillen. Getest over vier locaties maal twee periodes maal drie
parameterinstellingen, inclusief de randen van het raster, drempel 1,5 met
percentiel 0,95 en venster 1, en drempel 0,25 met percentiel 0,60 en venster 12,
en inclusief Cherson dat bijna geen droogtes heeft.

Winst: 4,24 naar 0,14 seconde per aanroep, 29,4 keer. Een run gaat van 11,2 naar
ongeveer 4,5 seconde, en het raster van T-10 van 8,7 naar ongeveer 3,5 uur.

### Seed per locatie, en dit verandert wel cijfers

**Beslist door Floris.** Eén ensemble, met een eigen seedstroom per locatie:
`numpy.random.SeedSequence(42).spawn(48)`, in de volgorde van de notebook-lijst.

Waarom het moest. Met `seed=42` voor elke locatie krijgt elke locatie dezelfde
RNG-stam, en het weekrooster van de kandidaattijdstippen is binnen een periode
overal hetzelfde. Twee locaties met evenveel floods krijgen daardoor **identieke**
surrogaten in alle 10000 simulaties, en bij ongelijke aantallen zwaar
overlappende. Voor de p-waarde per locatie maakt dat niets uit, en in die zin
klopt de sluiting van D-04. Voor de gepoolde toets uit de volgende entry wel:
positief gecorreleerde surrogaten blazen de variantie van de som op en maken de
toets te conservatief.

**Effect op de resultaten, gemeten over alle 48 locaties maal 2 periodes bij
threshold 0,5:**

| | |
|---|---|
| mediaan verschil in `p_mc_trigger` | 0,0000 |
| gemiddeld | 0,0004 |
| maximum | 0,0097 |
| runs die de grens van 0,05 oversteken | **1 van 96** |
| significant, was tegen wordt | 90 tegen **91** van de 96 |
| `p_trigger`, `p_precursor` en alle tellingen | **0 bewogen**, die zijn deterministisch |

De enige die omvalt is Dnipro in periode 1, van 0,0505 naar 0,0466. Dat is geen
fout maar de meetfout van de methode zelf: bij 10000 simulaties is de
standaardfout rond p = 0,05 ongeveer 0,002, en een locatie op 0,0505 is niet van
0,05 te onderscheiden. **Dat hoort in de tekst**, want het is precies het soort
grensgeval waar een reviewer naar vraagt.

D-04 blijft gesloten voor de p-waarde per locatie, maar de onderbouwing daar geldt
niet voor de aggregatie. Zie de aantekening in `docs/open-decisions.md`.

### Verificatie

Twee poorten, in deze volgorde, zodat de effecten niet door elkaar lopen.

**Poort 1.** Alle nieuwe parameters op hun default en de oude seedopzet, dus
`seed=42` overal. 48 locaties maal 2 periodes maal 11 velden tegen de cel
`daily+period` van `results/2026-09-01_reference_grid/`: **0 afwijkingen**, Monte
Carlo op vier decimalen. De ontkoppeling en de versnelling samen veranderen niets.

**Poort 2.** Dezelfde 96 runs met de seed per locatie. Uitkomst hierboven.

---

## 2026-09-01 (vierde) — T-02 en T-03 beslist, en de spiegeling wordt losgelaten

**Beslist door Floris.** Sluit T-02, T-03, D-11 en D-13. Deblokkeert T-10.

| punt | beslissing |
|---|---|
| T-03, referentieperiode | **per periode.** De drempels worden binnen elke periode geijkt, dus `reference_window=None`. Route B uit D-13 |
| T-02, quantielreferentie | **dagelijks.** Het floodquantiel gaat tegen de verzameling dagelijkse runoff-waardes van de periode, dus `quantile_reference="daily"` |

Samen is dat de gepubliceerde berekening. Aan de bestaande cijfers verandert dus
niets, en het raster van T-10 draait in één configuratie in plaats van dat het de
referentiekeuze als extra as moet meenemen.

**Wat T-03 kost, en dat moet in de tekst.** Bij ijking per periode lijken de twee
periodes bijna identiek, 35,9 tegen 35,6 procent droogteweken. Bij een
gemeenschappelijk ijkpunt is periode 2 aanzienlijk droger, 29,0 tegen 40,4, en het
verschil per locatie gaat van mediaan 1,8 naar 13,4 procentpunt. Rostov gaat van
3,7 naar 64,5 procent droogteweken. Met de keuze voor per periode **haalt de
normalisatie een deel van de verandering weg die het artikel juist tegen elkaar
afzet.** Dat is een verdedigbare keuze, maar hij moet als beperking benoemd
worden, niet weggelaten. Zie D-13 en `results/2026-09-01_reference_grid/`.

**De spiegeling tussen droogte- en flooddrempel wordt losgelaten.** De
flooddrempel is voortaan een percentiel dat op eigen gronden wordt gekozen, niet
de spiegeling van de droogtedrempel. Dat sluit aan bij D-11, waar al was
vastgesteld dat er feitelijk geen spiegeling plaatsvindt: de floodzijde lag op 25
tot 28 procent van de weken waar de droogtezijde op 16 zat. Het maakt bovendien de
as mogelijk die R4-01 vraagt.

Gevolg voor de tekst: het woord "mirroring" op pagina 17 verdwijnt, en in plaats
van een correctie achteraf wordt het een expliciete keuze die uitgelegd wordt. De
twee assen staan daarmee op verschillende voet, de SRI-drempel op een gefitte
gestandaardiseerde index en het floodpercentiel op de empirische verdeling van de
dagelijkse runoff, en **die twee zijn niet als "even streng" te lezen.** Zie T-29.

---

## 2026-09-01 (nog later) — Sluiting van P-02 en T-02 ingetrokken, referentievenster toegevoegd aan de code

**Twee dingen: een onderbouwing die niet meer geldt, en de code om hem opnieuw te
meten.** Geen wijziging aan de gepubliceerde berekening. Raakt T-02, T-03, P-02,
D-11, D-13.

### De sluiting van P-02 en T-02 is ingetrokken

De entry hierboven sluit P-02 en T-02 met het argument dat het spiegelen van de
flooddrempel 18 locaties hun significantie kost en in periode 2 nul overhoudt. Dat
cijfer komt uit `results/2026-08-23_quantile_reference_variant/`, en die run staat
vast op `threshold=1`. Dezelfde dag is de threshold op 0,5 gezet. De onderbouwing
hoort dus bij een configuratie die niet meer geldt.

Waarom dat verschil kan uitmaken: bij threshold 1 lag de hoofdbevinding op minder
dan één standaardfout van de nullijn, 34,0 procent geobserveerd tegen 28,6
verwacht, met 10 van de 48 locaties significant. Bij 0,5 is dat 57,3 tegen ongeveer
35, ruim vier standaardfouten, met 45 van de 48. Een strengere flooddrempel wist
het eerste makkelijk uit en het tweede niet per se.

T-02 en P-02 staan weer op `wacht op Floris`. Opnieuw doorgerekend in
`results/2026-09-01_reference_grid/`, samen met T-03 omdat het over dezelfde
referentieverdeling gaat.

### Uitkomst van de rerun

`results/2026-09-01_reference_grid/`, 384 runs, 65 minuten. Vier cellen:
`quantile_reference` maal `reference_scope`, threshold vast op 0,5.

**Controlecel `daily+period` tegen `results/2026-08-23_threshold_comparison/`: 96
runs, nul afwijkingen.** De gepubliceerde berekening is exact gereproduceerd.

**T-02.** Significante runs van de 96, Monte Carlo: threshold 1 gaf 20 huidig tegen
2 voor de spiegelvariant, threshold 0,5 geeft 90 tegen **89**. Drie locaties
verliezen hun significantie, twee winnen er een. Het argument dat de reparatie de
resultaten sloopt geldt alleen bij threshold 1.

En de reparatie doet bij 0,5 wél wat hij belooft, alleen niet volledig. Afwijking
van de nominale 30,85 procent, per locatie: floodzijde van 13,80 naar 0,02 punten,
droogtezijde blijft op 5,38, onbalans tussen de zijdes van 9,17 naar 5,37 punten.
Het symmetrie-argument pleit dus vóór de reparatie, niet ertegen.

**Nieuw en los van deze beslissing: de droogtezijde is bij 0,5 zelf verkeerd
geijkt.** 35,8 procent van de weken waar 30,85 hoort. De SRI-mediaan ligt op -0,06
tot -0,16, dus de verdeling zit links van nul. Bij -1 is het effect weg, dus het is
de band tussen -0,5 en -1 die te vol zit, niet de staart. Bij threshold 1 vielen de
twee fouten tegen elkaar weg. **Oorzaak niet vastgesteld**, zie D-11 voor het
aanknopingspunt. Dit raakt T-01 en moet in T-29.

**T-03.** Bij ijking per periode lijken de twee periodes bijna identiek, 35,9 tegen
35,6 procent droogteweken. Bij een gemeenschappelijk ijkpunt is periode 2
aanzienlijk droger, 29,0 tegen 40,4. Het verschil per locatie gaat van mediaan 1,8
procentpunt naar 13,4, en van 0 naar 20 van de 48 locaties boven 15 punten. Rostov
gaat van 3,7 naar 64,5 procent droogteweken. Route A kost drie locaties hun
significantie, zes in combinatie met P-02.

**Voor de tekst.** Floodweken en floodevents schalen niet mee. De weken gaan van
44,6 naar 30,9 procent, min 30, de events maar van 82,4 naar 72,8, min 11. Een
event is een aaneengesloten reeks weken, dus een strengere drempel maakt events
vooral korter. Die twee getallen moeten in de methodensectie uit elkaar gehouden
worden.

**Niet gedekt: T-10 en R4-01.** Dit raster varieert waartegen de drempels geijkt
worden, niet de drie parameters die de reviewer noemt. En T-10 blijkt een
codewijziging te vragen die er nog niet is: `Intensity_calc` koppelt de SRI-drempel
en het floodpercentiel via `threshold_floods = norm.cdf(threshold)`, dus die twee
zijn niet los te variëren. Daarnaast doet `period_after_event` dubbel werk, het is
ook het venster voor `quantile_max_value` in `extract_events`.

### Code: `reference_window` en een losse fitreferentie

In `src/dtf/pipeline.py`:

- `SRI_calculate(runoff, reference=None)`. De gammafit per kalenderweek kan nu op
  een andere reeks dan de reeks die gestandaardiseerd wordt. `None` is fitten op
  `runoff` zelf, en dat is de gepubliceerde berekening
- `drought_flood_p_value_trigger_ECA(..., reference_window=None)`. Ijkt beide
  drempels op een opgegeven venster, dus zowel de gammafit van de SRI als de
  quantielreferentie van de flooddrempel. `None` is de periode zelf, en dat is de
  gepubliceerde berekening. Nodig voor route A in D-13, die bestond nog niet
- de functie geeft nu ook `pct_weeks_flood`, `pct_weeks_drought` en `n_weeks`
  terug. Zelfde berekening als `scripts/06_threshold_selectivity.py`, hier gratis
  omdat de drempellogica toch al is toegepast. Nodig voor T-29 en als sanity check.
  **Let op:** dezelfde berekening staat nu op twee plekken, en dat wringt met de
  afspraak over één definitie per functie. `06` kan later deze velden gaan gebruiken
- `_empty_as_datetime64` als guard in `get_matching_pairs_eca`. Bij nul events
  levert xarray een lege float64-array, en die is niet met een datetime64 te
  vergelijken. De precursor-richting viel daarop om. **Dit is de enige wijziging die
  bestaand gedrag raakt, en dat gedrag was een crash.** Voor niet-lege arrays kan er
  per definitie niets veranderen, de guard grijpt alleen bij `size == 0` in.
  Aangetroffen bij Cherson in periode 1 met een gemeenschappelijke referentie, waar
  nul droogtes overblijven. **Bij nul droogtes wordt de p-waarde 1,0, en dat betekent
  niets te toetsen en niet "geen samenhang".** Dat moet in de tekst apart worden
  toegelicht, zie D-12

**Effect op de resultaten: geen.** De defaults zijn de gepubliceerde berekening.
Nagerekend op vier locaties maal twee periodes bij threshold 0,5, verspreid over
Donau, Po, Seine en Maas: droogte-aantallen, floodaantallen, matches en beide
p-waardes exact gelijk aan `results/2026-08-23_threshold_comparison/`, Monte Carlo
op vier decimalen. De cel `daily` plus `period` in het nieuwe raster draait dezelfde
controle over alle 48 locaties.

**Omgeving.** Deze run draait op Python 3.12 met numpy 2.5.2, pandas 3.0.5, xarray
2026.7.0 en scipy 1.18.1. Dat is een nieuwere set dan in augustus, en de
gereproduceerde cijfers zijn identiek, inclusief de Monte Carlo-uitkomsten. Blijft
staan tot de omgeving echt gepind is, zie T-44.

---

## 2026-09-01 (later) — Threshold wordt 0,5 voor beide onderdelen

**Beslist door Floris.** Herroept de eerdere beslissing van dezelfde dag
hieronder. Sluit D-01, D-14, P-01 en P-02. Taken T-01, T-02, T-53.

Beide onderdelen van het raamwerk draaien voortaan op `threshold=0.5`, dus
droogte bij SRI < -0,5 en flood boven de 69,1e quantile.

**Wat er verandert.**

| onderdeel | was | wordt | gevolg |
|---|---|---|---|
| ECA, sectie 2.4.1 en 3.1, Tabel 3 | 1 | 0,5 | **alle cijfers in Tabel 3 veranderen** |
| copula, sectie 2.4.2 en 3.2, Appendix D | 0,5 | 0,5 | ongewijzigd, stond al goed |

Alleen de ECA verandert. De copula draaide al op 0,5.

**Effect op Tabel 3.** Het aantal locaties met p < 0,05 gaat van 10 naar 45 van
de 48, in beide periodes. Cijfers liggen klaar in
`results/2026-08-23_threshold_comparison/`. Dit raakt de abstract, de conclusie
en elke uitspraak over ruimtelijke verschillen.

**Waarom.** De methodensectie op pagina 17 beschrijft 0,5 en de 69e quantile, en
de copula draaide daar al op. Met deze keuze komen tekst en beide onderdelen op
één lijn te liggen, in plaats van dat er twee verschillende droogtedefinities
naast elkaar staan.

**Wat naar de reviewers gaat.** In de nieuwe versie wordt vermeld dat het eerste
onderdeel, de ECA, in de R1-versie op 1 draaide terwijl de methodensectie 0,5
beschreef, en dat beide onderdelen nu op 0,5 staan. Dat hoort bij het antwoord op
R4-01, waar de reviewer de drempels citeert zoals ze in de tekst stonden.

**Let op bij het opschrijven.** Bij 0,5 ligt ongeveer 44 procent van de weken
boven de flooddrempel en 35 procent onder de droogtedrempel. Dat is fors, en de
gevoeligheidsanalyse van R4-01 moet de hoogte van de drempel expliciet
behandelen. Zie taak T-10.

---

## 2026-09-01 (herroepen) — Threshold blijft 1 voor de ECA

**HERROEPEN dezelfde dag, zie de entry hierboven.** Blijft staan omdat de
onderbouwing bruikbaar is voor de gevoeligheidsanalyse: de SPI-classificatie legt
de grens voor moderate drought op -1,0, en dat argument geldt nog steeds als
motivering om 1 als variant mee te nemen.

De ECA blijft draaien op `threshold=1`, dus droogte bij SRI < -1 en flood boven
de 84,1e quantile. Dat is wat de gepubliceerde Tabel 3 heeft geproduceerd, dus
aan de cijfers verandert niets.

**Waarom.** De standaardclassificatie van de SPI, waarop de SRI is gemodelleerd,
legt de grens voor moderate drought op -1,0. Waardes tussen 0 en -0,99 gelden
daar als mild of near-normal. De drempel selecteert dus wat in de literatuur als
droogte telt. Dat is tevens het antwoord op R4-01, waar de reviewer de drempels
"somewhat arbitrary" noemt.

**Overwogen alternatief.** Met `threshold=0.5` gaat het aantal significante
locaties van 10 naar 45 van de 48, zie
`results/2026-08-23_threshold_comparison/`. Bewust niet gekozen: bij 0,5 zijn er
ongeveer 83 droogtes in 783 weken, gemiddeld één per negen à tien weken, en dat
is geen extremenregime meer. De conservatieve drempel is gekozen, niet de
drempel met het gunstigste resultaat. Dat wordt zo in de tekst opgeschreven.

**Effect op de resultaten: geen.** De code draaide al op 1.

**Wat hier wel uit volgt.** Zes tekstwijzigingen en één nieuwe openstaande
beslissing over de copula, zie taak T-29, T-30 en het nieuwe D-14.

---

## 2026-09-01 — Off-by-one en vaste seed blijven zoals ze zijn

**Beslist door Floris.** Sluit D-02 en D-04, taken T-04 en T-05.

**Off-by-one.** `second_begin` blijft 5480, dus periode 2 loopt van 2 januari
2010 tot en met 31 december 2024, 5478 dagen tegen 5479 in periode 1. Index 5479,
1 januari 2010, valt buiten beide periodes.

Effect nagerekend op vier locaties met threshold 0,5: met begin 5479 of 5480
exact dezelfde droogte- en floodaantallen en dezelfde p-waardes tot op vier
decimalen. De extra dag valt in de eerste weekbin en verandert daar niets. Geen
reden om te herberekenen.

**Vaste seed.** `seed=42` blijft voor alle 48 locaties gelijk.

**Wat hier wel uit volgt.** De methodensectie beweert dat de reeks in twee delen
van gelijke lengte is gesplitst en dat periode 2 in januari 2010 begint. Beide
kloppen niet. En het manuscript noemt het aantal Monte Carlo-simulaties en de
seed nergens. Drie feitelijke correcties, uitgewerkt in taak T-56.

---

## 2026-09-01 — Twee tekstcorrecties besloten

**Beslist door Floris.** Taken T-56 en T-57. Geen effect op de cijfers.

**Startjaar.** De abstract en de introductie noemen 1994 als startjaar, de
dataset begint op 1 januari 1995 en de methodensectie zegt dat ook correct.
Bevestigd dat de data bij 1995 begint, dus de tekst wordt aangepast naar 1995 en
er wordt geen extra jaar opgehaald. Twee plekken: het manuscript zelf en het
apart ingevulde abstract-veld in Editorial Manager.

**Aantal simulaties.** Het manuscript noemt nergens hoeveel Monte
Carlo-randomisaties er zijn gedaan. Wordt toegevoegd: 10.000 per locatie en
periode, met een vaste seed.
