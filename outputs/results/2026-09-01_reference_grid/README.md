# Referentieraster voor T-02 en T-03, threshold 0,5

| | |
|---|---|
| gedraaid | 1 september 2026, 65,0 minuten |
| script | `scripts/07_reference_grid.py` |
| rapport | `scripts/08_reference_grid_report.py`, alle cijfers hieronder komen daaruit |
| vast | `threshold=0.5`, `period_after_event=4`, `1W`, 10000 sims, `seed=42` |
| assen | `quantile_reference` maal `reference_scope` |
| runs | 384, alle geslaagd |
| manifest | `manifest.yaml`, met commit, checksum en pakketversies |

Onderzoek, geen wijziging. De defaults in `src/dtf/pipeline.py` blijven `daily` en
`reference_window=None`, dus de gepubliceerde berekening.

## Waarom deze run bestaat

`results/2026-08-23_quantile_reference_variant/` staat vast op `threshold=1`, en
T-01 heeft de threshold op 0,5 gezet. De cijfers waarop T-02 op 1 september was
gesloten horen dus bij een configuratie die niet meer geldt. T-03 gaat mee omdat
het over dezelfde referentieverdeling gaat.

**Vervangt de threshold-1 variant als grondslag voor T-02.** Die run blijft staan
als vergelijking.

## De twee assen

| as | waardes | hoort bij | raakt |
|---|---|---|---|
| `quantile_reference` | `daily`, `weekly_max` | T-02, P-02, D-11 | alleen de floodzijde |
| `reference_scope` | `period`, `full` | T-03, D-13 | beide zijdes |

`daily` is het weekmaximum als quantiel van de ruwe dagelijkse verdeling, de
gepubliceerde berekening. `weekly_max` is het weekmaximum tegen zijn eigen
verdeling, het voorstel van P-02. `period` ijkt binnen de periode, `full` over de
volle 30 jaar.

## Sanity checks

- 384 regels, geen ontbrekende cel, locatie of periode, geen duplicaten
- **controlecel `daily+period` tegen `results/2026-08-23_threshold_comparison/`
  bij threshold 0,5: 96 runs, nul afwijkingen.** Droogtes, floods, matches en beide
  p-waardes gelijk, Monte Carlo op vier decimalen. De code die dit raster draait
  reproduceert de gepubliceerde berekening exact
- droogte-aantallen wijken bij 0 van de 96 af tussen `daily` en `weekly_max`,
  binnen beide scopes. Die as lekt dus niet naar de droogtezijde
- `weekly_max+period` geeft bij alle 96 runs exact 30,9 procent floodweken, met
  spreiding nul. Dat is de constructie en niet een uitkomst
- twee runs met nul droogte-events, beide Cherson in periode 1 bij `scope=full`.
  Dat is de reden dat er een guard in `get_matching_pairs_eca` is gekomen, zie de
  changelog. Hun p-waarde van 1,0 betekent **niets te toetsen**, niet
  "geen samenhang". Zie D-12
- omgeving nieuwer dan de augustusruns, numpy 2.5.2 en pandas 3.0.5, en de
  gereproduceerde cijfers zijn identiek

## Hoofdtabel, gemiddelde per locatie

| cel | periode | droogtes | floods | matches | toeval | ratio | MC < 0,05 |
|---|---|---|---|---|---|---|---|
| daily+period | 1 | 82,7 | 82,4 | 49,6 | 29,9 | 1,66 | **45/48** |
| daily+period | 2 | 82,4 | 84,9 | 49,7 | 30,6 | 1,62 | **45/48** |
| weekly_max+period | 1 | 82,7 | 72,8 | 42,6 | 27,2 | 1,57 | 44/48 |
| weekly_max+period | 2 | 82,4 | 74,4 | 41,9 | 27,5 | 1,53 | 45/48 |
| daily+full | 1 | 74,5 | 84,6 | 45,2 | 27,8 | 1,63 | 42/48 |
| daily+full | 2 | 82,6 | 82,2 | 50,3 | 29,9 | 1,68 | 45/48 |
| weekly_max+full | 1 | 74,5 | 76,4 | 39,2 | 25,4 | 1,54 | 39/48 |
| weekly_max+full | 2 | 82,6 | 71,3 | 41,9 | 26,6 | 1,57 | 45/48 |

`toeval` is de nullijn van de toets, het aantal droogtes maal de kans dat er bij
onafhankelijkheid binnen vier weken minstens één flood valt. `ratio` is matches
gedeeld door die verwachting.

De tabel zonder de drie Dnieper-locaties staat in de uitvoer van het
rapportscript. Die locaties hebben te weinig droogte-events om te toetsen, zie
D-12, en ze drukken de gemiddeldes.

## T-02: het beeld kantelt tegenover threshold 1

Significante runs, Monte Carlo, van de 96:

| | huidige berekening | spiegelvariant |
|---|---|---|
| threshold 1 | 20 | **2** |
| threshold 0,5 | 90 | **89** |

Bij threshold 1 kostte het spiegelen 18 locaties hun significantie en hield
periode 2 er nul over. Bij 0,5 verliezen er drie en winnen er twee. Mediane
verschuiving in p: plus 0,0001.

Wie het raakt: Nikolaevskaya 0,0014 naar 0,0515, Kochetovskaya 0,0271 naar 0,0949,
Magdeburg 0,0000 naar 0,1283. Erbij komen Dnipro 0,0505 naar 0,0000 en
Rostov 0,0540 naar 0,0380.

**Het cijfermatige argument tegen P-02 bestaat bij 0,5 niet.**

### Waarom het bij 1 anders uitpakte

Bij threshold 1 lag de hoofdbevinding op minder dan één standaardfout van de
nullijn, 34,0 procent geobserveerd tegen 28,6 verwacht. Bij 0,5 op ruim vier, 57,3
tegen ongeveer 35. Een strengere flooddrempel wist het eerste makkelijk uit en het
tweede niet.

### Weken tegen events

De floodweken gaan van 44,6 naar 30,9 procent, min 30 procent. De floodevents maar
van 82,4 naar 72,8, **min 11 procent**. Een event is een aaneengesloten reeks weken
boven de drempel, dus een strengere drempel maakt events vooral korter in plaats
van dat hij ze wegneemt.

Dat is belangrijk voor de tekst: wie over selectiviteit schrijft moet weken en
events uit elkaar houden, anders leest een reviewer het als hetzelfde getal.

Elasticiteit van matches op floods, log op log: mediaan 1,23 bij threshold 0,5
tegen 1,46 bij threshold 1.

## T-02: symmetrie, en dit pleit vóór P-02

Gemeten per locatie over 96 runs, afwijking van de nominale 30,85 procent:

| | floodweken | droogteweken | onbalans tussen de zijdes |
|---|---|---|---|
| huidige berekening | 13,80 punten te hoog | 5,38 punten te hoog | 9,17 punten |
| spiegelvariant | **0,02 punten** | 5,38 punten te hoog | **5,37 punten** |

De variant repareert de floodzijde exact en **halveert** de onbalans bijna. Hij
levert dus niet de volledige symmetrie die P-02 belooft, maar hij komt er wel
dichter bij dan de huidige berekening. Ratio per locatie: afwijking van 1 gaat van
0,263 naar 0,150.

**Wat er overblijft is een tweede, los probleem.** De droogtezijde staat op 35,8
procent waar 30,85 hoort, en dat verandert niet door P-02 wel of niet uit te
voeren. Gemeten op drie locaties in periode 1: de SRI-mediaan ligt op -0,06 tot
-0,16, dus de verdeling zit links van nul. Bij -1 is het effect weg, 14,8 tegen
nominaal 15,87, dus de onderste staart is niet dikker maar de band tussen -0,5 en
-1 is voller. Bij threshold 1 vielen die twee fouten tegen elkaar weg, en daarom
leek die kant daar goed geijkt.

**Oorzaak niet vastgesteld.** Aanknopingspunt: de gammafit gebeurt per
kalenderweek en heeft 14,8 waardes per fit, met de locatieparameter op nul vast.
Vermoeden, niet gemeten: een MLE-gammafit op zo weinig punten wordt door de hoge
waardes omhoog getrokken, waardoor de gefitte mediaan boven de steekproefmediaan
komt en de SRI systematisch negatief uitvalt. Te toetsen tegen een empirische
variant of een grotere fitsteekproef. Dat is nieuw werk en het staat er niet.

## T-03: de per-periode ijking verbergt precies wat er veranderd is

Aandeel weken per periode, `daily`:

| scope | periode | droogteweken | floodweken |
|---|---|---|---|
| period | 1 | 35,9% | 44,3% |
| period | 2 | 35,6% | 45,0% |
| full | 1 | 29,0% | 48,3% |
| full | 2 | 40,4% | 40,9% |

Bij ijking per periode lijken de twee periodes bijna identiek. Bij een
gemeenschappelijk ijkpunt blijkt periode 2 aanzienlijk droger.

Verschil tussen de periodes per locatie, in procentpunten droogteweken:

| scope | mediaan verschil | boven 15 punten | grootste |
|---|---|---|---|
| period | 1,8 | 0 van 48 | 13,3 bij Dnipro |
| full | **13,4** | **20 van 48** | **60,8 bij Rostov** |

De Don is het duidelijkst: Rostov gaat van 3,7 procent droogteweken in periode 1
naar 64,5 in periode 2, Kochetovskaya van 4,8 naar 62,1, Nikolaevskaya van 6,1
naar 60,8. Cherson op de Dnieper van 0,0 naar 39,4.

**Dat is het argument van D-13 in cijfers.** Het artikel zet de twee periodes
tegen elkaar af. De per-periode normalisatie haalt precies de verandering weg die
je wil zien.

### Wat route A kost

| | verliest significantie | wint |
|---|---|---|
| daily+full | 3 | 0 |
| weekly_max+full | 6 | 0 |

Wie het raakt zijn de gereguleerde rivieren in periode 1: Krementsjoek, en de drie
Don-locaties. Bij `weekly_max+full` komen Vernon, Pora Wesfalica en Bremen erbij.

Dat is te lezen als een verlies of als een winst, en dat is een keuze en geen
rekenkundig punt. Die locaties tellen nu mee als bewijs voor droogte-flood
samenhang terwijl hun droogtedefinitie meebeweegt met het afvoerregime van de
periode zelf. Bij een gemeenschappelijk ijkpunt heeft Cherson in periode 1 nul
droogtes, en dat is een feit over de rivier en niet een tekortkoming van de toets.

## Wat hier niet in zit

**Dit is geen antwoord op T-10 en op R4-01.** Die vragen gevoeligheid op de
SRI-drempel, het floodpercentiel en de venstergrootte. Dit raster varieert waar de
drempels tegen geijkt worden, een vierde as die geen reviewer heeft gevraagd. Twee
dingen die T-10 blokkeren en die hier zijn vastgesteld:

- `Intensity_calc` koppelt de SRI-drempel en het floodpercentiel via
  `threshold_floods = norm.cdf(threshold)`. Ze zijn niet los te variëren zonder
  codewijziging
- `period_after_event` doet dubbel werk. Naast het matching-venster bepaalt het in
  `extract_events` ook het venster voor `quantile_max_value`. Voor de p-waardes
  maakt dat niets uit, voor de copula-kant wel

## Bestanden

- `grid_results.csv`, 384 regels. Kolommen: `quantile_reference, reference_scope,
  period, river, village, river_location, drought_count, flood_count,
  match_count_trigger, match_count_precursor, observed_matches_mc, p_trigger,
  p_precursor, p_mc_trigger, pct_weeks_flood, pct_weeks_drought, n_weeks`
- `manifest.yaml`
- `run.log`
- `grid_results_afgebroken_run.csv` en `reference_grid_afgebroken_run.log`, de
  eerste poging. Die liep bij run 198 vast op de lege-array bug in
  `get_matching_pairs_eca`. Bewaard omdat de eerste 197 runs geldig zijn en omdat
  de crash zelf een bevinding is
