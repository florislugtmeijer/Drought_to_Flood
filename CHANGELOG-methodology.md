# Methodologische wijzigingen

Elke wijziging die de uitkomsten kan veranderen, met de reden en het effect.
Bron voor de Revision Notes. Nieuwste bovenaan.

Beslissingen die nog open staan: `docs/open-decisions.md`. Voorstellen van
Floris: `docs/proposed-changes.md`. Werk dat eruit volgt: `docs/todo.md`.

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
