# Voorgestelde aanpassingen

Voorstellen van Floris zelf, apart bijgehouden van `docs/open-decisions.md`.
Dat bestand bevat bevindingen die uit de code of de data komen. Dit bestand
bevat wat Floris wil veranderen.

**Niets hieronder wordt uitgevoerd zonder dat Floris het per voorstel
vrijgeeft.** Ook niet als het klein lijkt, ook niet als het samenvalt met iets
anders waar wel aan gewerkt wordt. De reden om ze op te schrijven is juist om ze
te kunnen parkeren.

Status: `voorgesteld` niet uitvoeren, `vrijgegeven` mag gedaan worden,
`gedaan` verhuist naar `CHANGELOG-methodology.md`, `vervallen` met reden erbij.

Bij elk voorstel staan drie dingen: **waarom wel**, **waarom niet**, en bij niet
de **verdediging** waarmee de huidige keuze methodologisch houdbaar is, mits je
het in de tekst goed toelicht. Die laatste is geen goedpraten. Als de huidige
keuze niet te verdedigen is, staat dat er ook.

---

## P-01 Threshold van 1 naar 0,5

| | |
|---|---|
| voorgesteld | 23 augustus 2026 |
| status | **gedaan, 1 september 2026: threshold gaat naar 0,5 voor beide onderdelen** |
| raakt | alle event-aantallen, alle p-waardes, Tabel 3, abstract, conclusie |

Floris: "thresholds hadden inderdaad op 0.5 moeten staan", en later dezelfde dag
"voor nu blijven we op de threshold van 1 zitten".

**Beslist op 1 september 2026: threshold gaat naar 0,5, voor beide onderdelen.**
Een eerdere beslissing diezelfde dag om op 1 te blijven is herroepen. Zie
`CHANGELOG-methodology.md`. Alleen de ECA verandert, de copula stond al op 0,5.
Tabel 3 gaat van 10 naar 45 significante locaties van de 48.

Al doorgerekend, zie `results/2026-08-23_threshold_comparison/`. Het aantal
significante locaties gaat van 10 naar 45 van de 48. Dat is een andere
hoofdbevinding, geen nuanceverschuiving.

Voor nu blijft de code op 1. De cijfers voor 0,5 liggen klaar voor het moment dat
dit alsnog omgaat, of voor de gevoeligheidsanalyse van R4-01.

Let op: het manuscript beschrijft op pagina 17 een Z-score van 0,5. Zolang de
code op 1 blijft, moet die tekst mee naar 84e quantile en Z-score 1. Dat is geen
keuze maar een correctie. Zie D-01.

### Waarom wel naar 0,5

- Het is wat het manuscript nu beschrijft. Naar 0,5 gaan maakt tekst en code
  gelijk zonder de methodensectie te herschrijven.
- Het detecteert veel meer samenhang: 45 van 48 locaties significant tegen 10.
  De hoofdbewering van het artikel, dat droogtes vaker door floods worden
  gevolgd dan onder onafhankelijkheid, wordt daarmee veel breder gedragen.
- Bij threshold 1 zijn er op de Dnieper maar 5 droogte-events in 15 jaar. Zes
  van de 48 cellen in Tabel 3 staan op 1,0000, wat feitelijk "te weinig data"
  betekent maar leest als "geen samenhang". Bij 0,5 zijn er 28 droogtes en is er
  wel iets te zeggen.

### Waarom niet naar 0,5

- Bij 0,5 zijn er ongeveer 83 droogtes in 783 weken, dus gemiddeld één per negen
  à tien weken, en even zoveel floods. Dat is geen extremenregime maar gewone
  variabiliteit. De woorden droogte en flood gaan dan minder dekken wat ze
  aanduiden.
- Een uitkomst waarin 45 van 48 locaties significant is, zegt minder dan een
  uitkomst die ruimtelijk differentieert. Als alles overal samenhangt, valt er
  over lokale factoren weinig meer te zeggen, en juist daar vragen R1-08 en
  R4-05 om.
- Het verandert alle cijfers in een revisieronde. Dat moet uitgelegd worden aan
  editor en reviewers, en het is een zwakkere positie dan een gemotiveerde keuze
  die je vanaf het begin verdedigt.

### Verdediging als we op 1 blijven

> **Achterhaald.** Deze onderbouwing hoorde bij de beslissing om op 1 te blijven,
> die op 1 september 2026 is herroepen. Blijft staan omdat het argument bruikbaar
> is om threshold 1 als variant in de gevoeligheidsanalyse van R4-01 te
> motiveren. Voorwaarde 1 hieronder, over de 84e quantile, geldt niet meer: bij
> 0,5 klopt de 69e quantile in de tekst gewoon.

Deze is sterk, en ze rust op een bestaande conventie.

De standaardclassificatie van de SPI, waarop de SRI is gemodelleerd, legt de
grens voor **moderate drought** op -1,0. Waardes tussen 0 en -0,99 heten daar
mild of near-normal. Een drempel van SRI < -1 selecteert dus wat in de
literatuur als droogte geldt, en SRI < -0,5 selecteert grotendeels weken die per
conventie niet als droogte tellen.

Dat is geen detail dat je met een voetnoot afdoet: het is precies het antwoord
op R4-01, waar de reviewer schrijft dat de drempels "somewhat arbitrary" zijn.
Ze zijn niet arbitrair als je ze aan de gangbare classificatie ophangt. Dat is
een inhoudelijk argument, niet een verdediging van de status quo.

**Voorwaarden om dit te kunnen volhouden.** Alle vier moeten, anders houdt het
argument geen stand:

1. De methodensectie op pagina 17 aanpassen naar de 84e quantile en een Z-score
   van 1, met een expliciete verwijzing naar de SPI-classificatie als
   onderbouwing van juist die grens.
2. De gevoeligheidsanalyse van R4-01 met 0,5 erin, zodat aantoonbaar is dat de
   keuze bewust is en dat het effect bekend en gerapporteerd is. De cijfers
   liggen al klaar.
3. Eerlijk melden dat bij 0,5 het aantal significante locaties naar 45 van 48
   gaat. Dat weglaten is niet houdbaar, en het versterkt de eigen keuze juist:
   je laat zien dat je de conservatieve drempel hebt gekozen, niet de drempel
   die het mooiste resultaat geeft.
4. De zes cellen op 1,0000 voor de Dnieper apart toelichten. Die betekenen niet
   "geen samenhang" maar "te weinig droogte-events om iets te toetsen", en de
   reden daarvoor staat in D-12.

**Nog te controleren.** De exacte bron voor de SPI-classificatie moet uit de
referentielijst van het manuscript komen, niet uit mijn hoofd. De grens van -1,0
voor moderate drought is standaard, maar welke publicatie jullie ervoor citeren
moet je zelf vaststellen.

---

## P-02 Flooddrempel consistent maken met de Z-score

| | |
|---|---|
| voorgesteld | 23 augustus 2026 |
| status | **heropend 1 september 2026, wacht op Floris** |
| laatste update | 1 september 2026: de onderbouwing van de beslissing bleek op threshold 1 te staan |
| raakt | alle event-aantallen, alle p-waardes, Tabel 3 |

**Heropend op 1 september 2026.** De beslissing van diezelfde dag om de berekening
ongewijzigd te laten stond op de variant-run van 23 augustus, en die staat vast op
`threshold=1`. T-01 heeft de threshold later diezelfde dag op 0,5 gezet. Alle
cijfers in dit stuk over het effect van P-02 zijn dus threshold-1 cijfers, en dat
staat er hieronder per blok bij. Opnieuw doorgerekend op 0,5 in
`results/2026-09-01_reference_grid/`.

Wat er van de oude beslissing overeind blijft: de tekst moet gecorrigeerd worden,
want er is geen sprake van een mirroring-effect.

### Doorgerekend op 0,5, en twee van de drie argumenten kantelen

Bron: `results/2026-09-01_reference_grid/`, 384 runs, controlecel over alle 96 runs
exact gelijk aan de gepubliceerde berekening.

| argument | zoals het op 1 september lag | na doorrekenen op 0,5 |
|---|---|---|
| aanpassen sloopt de resultaten | 18 locaties verliezen significantie, periode 2 houdt er nul over | **weg.** 89 van 96 significant tegen 90 nu, drie verliezen, twee winnen |
| spiegelen levert geen symmetrie | niet gemeten bij 0,5 | **draait om, pleit vóór aanpassen.** De onbalans tussen de twee zijdes gaat van 9,17 naar 5,37 procentpunt |
| absolute flooddrempel is hydrologisch te verdedigen | stond | **staat nog, ongewijzigd** |

Wat er dus over is als reden om de berekening te laten staan: de inhoudelijke
verdediging hieronder, plus dat aanpassen alle cijfers verandert met 16 dagen tot
de deadline. Het cijfermatige argument en het symmetrie-argument zijn geen steun
meer, en het tweede is zelfs een tegenargument geworden.

Volledige uitwerking, inclusief waarom het bij threshold 1 anders uitpakte en
waarom floodweken en floodevents niet meeschalen, staat in de README van die map en
in D-11. Gemeten bij threshold 0,5: ongeveer 44 procent van de weken
ligt boven de flooddrempel tegen ongeveer 35 procent onder de droogtedrempel,
waar symmetrie 30,9 procent aan beide kanten zou geven. Bij threshold 1 was die
verhouding 1,63, bij 0,5 is hij 1,27, dus kleiner maar niet weg.

Wat wél vaststaat, los van hoe deze beslissing valt: het woord "mirroring" moet
uit de methodensectie en de feitelijke selectiviteit van de flooddrempel moet
gerapporteerd worden. Zie de voorwaarden onderaan.

Floris: "dan moeten we denk ik ook het quantiel aanpassen naar een quantiel dat
hoort bij de z score van 1".

Het voorstel raakt iets echts, alleen niet waar het leek te zitten. De code
koppelt de twee drempels al via `threshold_floods = norm.cdf(threshold)`, dus er
is geen aparte quantielparameter om te veranderen.

Wat niet klopt is de spiegeling. Gemeten over alle 48 locaties en beide periodes,
bij de huidige threshold 0,5: **44,6 procent** van de weken boven de flooddrempel
tegen **35,8 procent** onder de droogtedrempel, waar 30,9 aan beide kanten hoort.
Bij threshold 1 was dat 26,2 tegen 15,1 procent. De oorzaak is dat het
weekmaximum als quantiel van de ruwe dagelijkse verdeling wordt uitgedrukt, en een
weekmaximum ligt daar structureel hoog in.

De aanpassing zou zijn: weekmaxima tegen hun eigen verdeling. Die repareert de
floodzijde exact, van 13,80 procentpunten te hoog naar 0,02, en halveert de
onbalans tussen de zijdes bijna, van 9,17 naar 5,37 punten. Volledige symmetrie
levert het niet op, want de droogtezijde blijft op 35,8 staan waar 30,9 hoort.
Dat is een tweede, los probleem dat P-02 niet oplost.

Volledige uitwerking met de gemeten cijfers staat in D-11 in
`docs/open-decisions.md`.

### Waarom wel aanpassen

- Het manuscript zegt nu letterlijk dat de flooddrempel de droogtedrempel
  spiegelt. Dat is feitelijk niet zo: bij threshold 0,5 ligt 44,6 procent van de
  weken boven de flooddrempel tegen 35,8 procent onder de droogtedrempel, waar
  30,9 aan beide kanten hoort. Met de aanpassing wordt de tekst waar zonder dat je hem
  hoeft te herschrijven.
- Symmetrie is makkelijker uit te leggen. Eén parameter, twee drempels, aan
  beide kanten dezelfde zeldzaamheid.
- Het maakt locaties onderling beter vergelijkbaar, want de eventfrequentie ligt
  dan per constructie vast in plaats van mee te bewegen met hoe schoksgewijs een
  rivier reageert.

### Redenering van Floris, 24 augustus 2026

Floris: bij het bepalen van de p-waarde toetsen we niet op basis van twee events
die even vaak voorkomen. Omdat er meer floods zijn, corrigeert de toets ook voor
het feit dat er meer floods zijn. De correctie hoort dus in de tekst, met een
duidelijke uitleg voor de lezer hoe de flood-events bepaald zijn.

**Dat is juist.** De nullijn is `1 - (1 - 4/W)^n_floods`, en die schaalt mee met
het aantal floods. Meer floods geeft een hogere toevalsverwachting, en de
p-waarde meet alleen het overschot daarboven. Empirisch bevestigd in de
variant-run: 25 procent minder floods gaf 22 procent lagere toevalsverwachting.

Gevolg voor de weging van dit voorstel: de asymmetrie in eventfrequentie
**vertekent de toets niet**. P-02 is dus geen statistisch probleem maar een
definitie- en presentatiekwestie. Dat verschuift het zwaartepunt naar het
aanpassen van de tekst, en maakt het argument om de berekening te laten staan
sterker.

### Getoetst alternatief: eerst quantielen, dan weekmaxima

Floris stelde voor om de flood-waardes als quantiel van de hele set
runoff-waardes te bepalen vóórdat naar weekwaardes wordt overgestapt.

**Dat is wiskundig identiek aan de huidige berekening.** De quantieltransformatie
is monotoon stijgend, dus `max(q(x))` en `q(max(x))` geven hetzelfde. Getoetst op
Aschach, eerste periode: maximaal absoluut verschil 0,00 en in beide gevallen
221 weken boven de drempel. Niets te draaien.

**Maar naast die vraag zit wel een echt verschil**, en dat is over welke periode
de referentieverdeling loopt. Nu is dat alleen de periode zelf, 5479 dagen, niet
de volledige 30 jaar. De 84e percentiel verschuift daardoor mediaan 8,6 procent
tussen de periodes, en bij 32 van de 48 locaties meer dan tien procent. Op de Don
ruim 30 procent omlaag, op de Tagus tot 120 procent omhoog. Uitgewerkt als D-13
in `docs/open-decisions.md`.

### Waarom niet aanpassen

**Alle cijfers in dit blok zijn gemeten bij threshold 1.** Bij threshold 1 zat de
hoofdbevinding op minder dan één standaardfout van de nullijn, bij 0,5 op ruim
vier. Een strengere flooddrempel doet in die twee gevallen niet hetzelfde.

- Het verandert alle cijfers, en de eerste uitkomsten wijzen erop dat het de
  ándere kant op gaat dan threshold 0,5: strengere flooddrempel, minder floods,
  minder matches. Aschach verliest zijn significantie, van 0,0057 naar 0,0870.
  Als dat patroon breed doorzet, wordt de hoofdbevinding van het artikel zwakker
  in plaats van sterker.
- De huidige berekening is niet fout. Alleen het woord "mirroring" is fout.

### Verdediging als we het laten staan

Deze is inhoudelijk het interessantst, want de asymmetrie is te verdedigen als
een keuze in plaats van als een slordigheid.

Droogte en flood zijn hydrologisch niet hetzelfde soort gebeurtenis, en dat
rechtvaardigt verschillende referentiekaders:

- Een **droogte** is een tekort ten opzichte van wat voor die tijd van het jaar
  normaal is. Een lage augustusafvoer op de Rhône is geen droogte, dat is
  augustus. Daarom hoort daar een seizoensgestandaardiseerde maat bij, en dat is
  precies wat de SRI doet met zijn gamma-fit per kalenderweek.
- Een **flood** is het overschrijden van een absoluut afvoerniveau. Water treedt
  buiten zijn oevers bij een bepaald debiet, niet bij een bepaalde afwijking van
  het seizoensgemiddelde. Daarom hoort daar een absolute maat bij, en die is de
  flow duration curve van de volledige dagelijkse reeks.

In die lezing is de 84e percentiel van de dagelijkse verdeling geen mislukte
spiegeling maar een herkenbare hydrologische grootheid: het debiet dat 16 procent
van de dagen wordt overschreden. Dat een weekmaximum die grens in 26 procent van
de weken haalt is geen fout, dat is de logische consequentie van een maximum
over zeven dagen nemen, en het is een gevolg dat je kunt uitrekenen en
opschrijven.

De aanpassing zou dat juist opgeven. Weekmaxima tegen hun eigen verdeling
leveren per definitie 16 procent floodweken op, bij elke rivier, ongeacht het
afvoerregime. Dat maakt de drempel relatief en hangt hem los van elk fysiek
niveau. Voor een artikel dat 16 rivieren met heel verschillende regimes
vergelijkt is dat een verlies, niet een winst.

**Voorwaarden om dit te kunnen volhouden.** Drie, en de eerste is niet
optioneel:

1. Het woord "mirroring" moet uit de methodensectie. Zoals het er nu staat is de
   claim onwaar en kan een reviewer die met twee regels code weerleggen.
2. Ervoor in de plaats de asymmetrie expliciet benoemen en motiveren:
   seizoensrelatieve droogte tegen absolute floodgrens, met de reden waarom dat
   twee verschillende dingen zijn.
3. De feitelijke selectiviteit rapporteren, dus dat de flooddrempel ongeveer 25
   44,6 procent van de weken aanmerkt tegen 35,8 procent aan de droogtekant, bij
   de huidige threshold 0,5. Dat getal hoort in de tekst of in een appendix, niet weggelaten.

Punt 1 en 2 zijn hoe dan ook nodig, ook als het voorstel wel wordt uitgevoerd,
want dan moet er staan waarom er nu wél gespiegeld wordt.

### Effect op de resultaten, gemeten bij threshold 1

**Verouderd als onderbouwing.** Doorgerekend over alle 48 locaties en beide
periodes, maar met `threshold=1`. Volledige uitwerking in
`results/2026-08-23_quantile_reference_variant/README.md`. De run op 0,5 staat in
`results/2026-09-01_reference_grid/`.

> **Deze tabel is bij `threshold=1` gemeten en geldt niet meer als grondslag.**
> Sinds T-01 draait alles op 0,5. Bij 0,5 kantelt het beeld volledig: significante
> runs van de 96 gaan van 90 naar 89 in plaats van van 20 naar 2. Drie locaties
> verliezen, twee winnen, mediane verschuiving in p is +0,0001. Zie
> `results/2026-09-01_reference_grid/`. De tabel blijft staan als vergelijking.

| | eerste periode | | tweede periode | |
|---|---|---|---|---|
| | nu | variant | nu | variant |
| floods per locatie | 66,3 | 49,8 | 71,5 | 52,6 |
| matches per locatie | 19,9 | 12,8 | 20,4 | 12,5 |
| **significant, Monte Carlo** | **10 / 48** | **2 / 48** | **10 / 48** | **0 / 48** |
| significant, Poisson | 13 / 48 | 2 / 48 | 14 / 48 | 0 / 48 |

Achttien locaties verliezen hun significantie, nul winnen er een. De droogtekant
blijft gelijk.

~~**Dit weegt zwaar tegen het voorstel.** In de tweede periode blijft er geen
enkele significante locatie over.~~ **Vervallen op 1 september 2026.** Dat gold
bij threshold 1. Bij 0,5 bestaat het cijfermatige argument tegen het voorstel
niet: 90 naar 89 significante runs. Wat overblijft is het methodologische
argument, de flow duration curve als absolute floodgrens tegenover de
seizoensrelatieve droogtemaat.

Het verandert niets aan de eis dat "mirroring" uit de methodensectie moet en dat
de feitelijke selectiviteit gerapporteerd wordt. Die twee blijven, welke kant
deze beslissing ook op valt.

**Waarom de p-waarde omhoog gaat terwijl er minder floods zijn.** Een p-waarde
kijkt niet naar het aantal matches maar naar het overschot boven wat het toeval
al oplevert. Een strengere drempel verlaagt beide, dus dat de matches dalen zegt
op zichzelf niets. Gemiddeld per locatie:

| | nu | variant | verandering |
|---|---|---|---|
| floods | 66,3 | 49,8 | −25% |
| matches geobserveerd | 19,9 | 12,8 | −36% |
| matches verwacht bij toeval | 16,2 | 12,6 | −22% |
| **overschot boven toeval** | **3,7** | **0,1** | **−97%** |
| ratio geobserveerd / verwacht | 1,13 | 0,94 | |

Eerste periode. De geobserveerde matches dalen harder dan de toevalsverwachting,
dus het overschot verdampt. In de tweede periode gaat de ratio naar 0,93, dus
droogtes worden dan iets minder vaak door een flood gevolgd dan het toeval
voorspelt.

"Verwacht bij toeval" is hier analytisch berekend met dezelfde binomiale formule
die de code voor de Poisson-tak gebruikt: `1 - (1 - 4/784)^floods` maal het
aantal droogtes. De Monte Carlo komt via randomisatie op dezelfde nulverwachting
uit, langs een andere route.

**Getoetst, en het is een bevinding.** De floods die de strengere drempel
weggooit blijken juist de floods te zijn die relatief vaak na een droogte kwamen.
Over 6617 flood-events, uitgesplitst naar grootte:

| groottebin | kans op voorafgaande droogte | toeval | ratio |
|---|---|---|---|
| kleinste 20% | 0,313 | 0,249 | 1,26 |
| 20-40% | 0,302 | 0,248 | 1,22 |
| 40-60% | 0,316 | 0,248 | 1,27 |
| 60-80% | 0,277 | 0,248 | 1,12 |
| grootste 20% | 0,247 | 0,248 | **1,00** |

Bij de grootste floods is het effect exact nul. Twee onafhankelijke maten voor
grootte geven hetzelfde, en het patroon zit in beide periodes. Volledige
uitwerking met de beperkingen in
`results/2026-08-23_flood_magnitude_test/README.md`.

Voor P-02 betekent dit dat het signaalverlies geen statistisch artefact is: de
strengere drempel verwijdert precies de groep waar de samenhang in zit. Dat weegt
mee als inhoudelijk argument en niet alleen als ongelukkige uitkomst.

**Seizoensverklaring uitgesloten**, zie `results/2026-08-24_season_control/`. Met
groottebins binnen locatie én seizoen en een seizoensspecifieke empirische nullijn
blijft het verloop staan: 1,17 / 1,23 / 1,12 / 1,01 / 0,94. Het verschil tussen
klein en groot wordt zelfs sterker, chi-kwadraat 24,8 tegen 17,6. Het confound
bleek er ook nauwelijks te zijn: droogtes eindigen vrijwel gelijkmatig over het
jaar en de floodgrootte verschilt per seizoen nauwelijks.

Wel een correctie op de cijfers hierboven: de empirische nullijn is 0,265 tot
0,271, waar de binomiale formule op 0,248 uitkwam. De ratio's zijn dus iets lager
dan de tabel hierboven suggereert, 1,17 tot 1,23 in plaats van 1,22 tot 1,27.
Richting en significantie blijven.

Drie beperkingen die je moet meenemen: het is een uitspraak op Europese schaal en
niet per rivier (57 van 95 locatie-periodes tonen het individueel) of per seizoen
(alleen winter en najaar geven een schoon verloop), bij de grootste floods is er
geen samenhang maar ook geen negatieve samenhang, en het blijft een associatie.
Om het mechanisme hard te maken is een variabele nodig die de veronderstelde
oorzaak meet, bodemvocht of infiltratiecapaciteit. Dat is precies wat R4-04
bedoelt met "ideally supported by ancillary data". Een
lezing die dat verklaart staat in de README bij de resultaten: de strengere
drempel houdt alleen de grote seizoensfloods over, en die hangen minder met een
voorafgaande droogte samen dan de matig verhoogde afvoerweken. Als dat klopt is
het materiaal voor R4-04. Nog te toetsen, niet aan te nemen.

---

## P-03 Matching vanaf het einde van de droogte

| | |
|---|---|
| voorgesteld | 23 augustus 2026 |
| status | **vervallen, was al goed** |
| raakt | niets |

Floris: "het moet vanaf het einde van een droogte, niet vanaf de start".

Terecht als eis, maar de gepubliceerde versie doet dit al. Zowel de observed
telling als de nulverdeling in de Monte Carlo gebruiken `end_time`, met dezelfde
vergelijking aan beide kanten. Het probleem dat dit voorstel wilde oplossen zat
in de afgedankte `LAATSTE_VERSIE`-tak, niet in de gepubliceerde code.

Zie `docs/reproducibility-check.md`.
