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
| status | **voorgesteld, voor nu blijft het 1** |
| raakt | alle event-aantallen, alle p-waardes, Tabel 3, abstract, conclusie |

Floris: "thresholds hadden inderdaad op 0.5 moeten staan", en later dezelfde dag
"voor nu blijven we op de threshold van 1 zitten".

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
| status | **voorgesteld, niet uitvoeren** |
| raakt | alle event-aantallen, alle p-waardes, Tabel 3 |

Floris: "dan moeten we denk ik ook het quantiel aanpassen naar een quantiel dat
hoort bij de z score van 1".

Het voorstel raakt iets echts, alleen niet waar het leek te zitten. De code
koppelt de twee drempels al via `threshold_floods = norm.cdf(threshold)`, dus er
is geen aparte quantielparameter om te veranderen.

Wat niet klopt is de spiegeling. Gemeten aandeel weken boven de flooddrempel is
25 tot 28 procent, tegen ongeveer 16 procent onder de droogtedrempel. De oorzaak
is dat het weekmaximum als quantiel van de ruwe dagelijkse verdeling wordt
uitgedrukt, en een weekmaximum ligt daar structureel hoog in.

De aanpassing zou zijn: weekmaxima tegen hun eigen verdeling. Dan komt de
floodkant op 15,9 procent, exact `norm.cdf(-1)`, en spiegelen de drempels wel.

Volledige uitwerking met de gemeten cijfers staat in D-11 in
`docs/open-decisions.md`.

### Waarom wel aanpassen

- Het manuscript zegt nu letterlijk dat de flooddrempel de droogtedrempel
  spiegelt. Dat is feitelijk niet zo: 25 tot 28 procent van de weken tegen
  ongeveer 16 procent. Met de aanpassing wordt de tekst waar zonder dat je hem
  hoeft te herschrijven.
- Symmetrie is makkelijker uit te leggen. Eén parameter, twee drempels, aan
  beide kanten dezelfde zeldzaamheid.
- Het maakt locaties onderling beter vergelijkbaar, want de eventfrequentie ligt
  dan per constructie vast in plaats van mee te bewegen met hoe schoksgewijs een
  rivier reageert.

### Waarom niet aanpassen

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
   tot 28 procent van de weken aanmerkt tegen ongeveer 16 procent aan de
   droogtekant. Dat getal hoort in de tekst of in een appendix, niet weggelaten.

Punt 1 en 2 zijn hoe dan ook nodig, ook als het voorstel wel wordt uitgevoerd,
want dan moet er staan waarom er nu wél gespiegeld wordt.

### Effect op de resultaten

Wordt hier aangevuld zodra de run over alle 48 locaties en beide periodes klaar
is. Script: `scripts/03_quantile_reference_variant.py`, uitvoer in
`results/2026-08-23_quantile_reference_variant/`.

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
