# Welke functievariant is canoniek

De Colab-bron bevat 47 functiedefinities voor 33 unieke functies. Dit document
legt per dubbele functie vast welke variant canoniek is en op grond waarvan.
Celnummers verwijzen naar
`notebooks/legacy/drought_to_flood_europe_colab_2026-08-23.ipynb`.

Status: gedeeltelijk bevestigd.

- `drought_flood_p_value_trigger_ECA` cel 50: dit is de variant die gedraaid
  heeft, maar de matching-logica erin is **fout**. Floris, 23 augustus 2026:
  matching hoort vanaf het **einde** van de droogte te gaan. Zie D-08 in
  `docs/open-decisions.md`.
- `monte_carlo_p_value` cel 49 en `fit_copula` cel 62: voorstel, wacht nog op
  bevestiging.
- De overige negen functies verschillen alleen in vorm, daar valt niets te
  beslissen.

## Conclusie vooraf

De ambiguïteit is veel kleiner dan de ruwe vergelijking suggereerde. Van de
veertien functies met verschillende varianten blijken er negen alleen te
verschillen in docstrings, comments, whitespace en debug-prints. Cel 49 is geen
vereenvoudigde herimplementatie, zoals eerst gedacht, maar een geconsolideerde
opgeschoonde kopie van de actieve functies.

Er blijven drie echte methodologische keuzes over, en die zijn alle drie met
bewijs uit het notebook beslecht.

## Functioneel identiek, veilig samen te voegen

Verschil zit uitsluitend in docstrings, comments, formattering of weggehaalde
`print`-regels. Canoniek is de versie met docstring, want die documenteert
zichzelf.

| functie | varianten | canoniek | verschil |
|---|---|---|---|
| `SRI_calculate` | 34, 49 | **34** | nul regels code-verschil |
| `transform_to_quantiles` | 42, 49 | **42** | nul regels code-verschil |
| `extract_events` | 37, 49 | **37** | alleen witruimte |
| `eca_p_value` | 40, 49 | **40** | `stats.binom.pmf` versus `binom.pmf`, zelfde functie via andere import, plus een `print` |
| `get_matching_pairs_eca` | 40, 49 | **40** | comment, plus losse imports na de `return` |
| `get_matching_pairs_drought_trigger` | 39, 49 | **39** | alleen een comment |
| `river_runoff_time_location_mean` | 13, 21, 35, 49, 94 | **35** | 13 en 21 zijn identiek aan elkaar en ouder, 94 wijkt 2 tekens af, 49 mist een `print` |
| `river_runoff_time_location_maximum` | 33, 49 | **33** | alleen de docstring |
| `process_img`, `safe_format` | 63/65, 54/55/103 | willekeurig | byte-identiek |

## Echte verschillen, met bewijs beslecht

### `drought_flood_p_value_trigger_ECA`: cel 50

Twee varianten met een wezenlijk methodologisch verschil:

- **cel 49** matcht een flood aan het **einde** van de droogte:
  `flood.start_time > drought.end_time` en `<= drought.end_time + delta`
- **cel 50** matcht een flood aan het **begin** van de droogte:
  `0 <= flood.start_time - drought.start_time <= delta`

Dat is niet cosmetisch, het definieert wat een drought-to-flood event is.

**Bewijs dat cel 50 de resultaten maakte:** cel 49 retourneert twee waarden, cel
50 retourneert er negen. Alle drie de aanroepen in het notebook (cel 54, 55 en
103) pakken negen waarden uit. Cel 49's variant kan dus nooit gebruikt zijn, die
zou een `ValueError` geven bij het uitpakken. Cel 49 is dode code.

**Floris, 23 augustus 2026: matching hoort vanaf het einde van de droogte.**

Cel 50 is dus wel de variant die gedraaid heeft, maar de matching die de
Monte Carlo p-waarde voedt is fout. Uitgewerkt in D-08 in
`docs/open-decisions.md`.

### `monte_carlo_p_value`: cel 49

Duidelijke evolutie in vier stappen. Cel 48 en 49 zijn functioneel identiek, 49
is 48 zonder debug-output.

| cel | randomisatie | matching | tijdvenster |
|---|---|---|---|
| 46 | wekelijks raster | `np.any`, één flood mag meerdere droughts matchen | gereconstrueerd uit `start_date` en `n_weeks` |
| 47 | dagelijks raster | greedy, één flood per drought | idem, afgekapt op `time_max - delta` |
| 48 | dagelijks raster | greedy | echte `data['valid_time'][begin:end]` |
| 49 | dagelijks raster | greedy | idem als 48 |

Canoniek: **49**, als eindstand van de reeks. De aanroep in cel 50 gebruikt de
signature met `data, begin, end`, wat alleen bij 48 en 49 past. Dat bevestigt het.

Twee punten die een reviewer zou kunnen opbrengen, geen van beide opgelost:

1. De observaties zijn weekly geresampled, maar de gesimuleerde flood-tijden
   worden op een **dagelijks** raster getrokken (`freq="D"`). Observed en
   simulated matches komen daarmee uit verschillend gerasterde reeksen, wat de
   nulverdeling kan vertekenen.
2. `seed=42` staat vast voor alle 48 locaties, dus elke locatie krijgt dezelfde
   pseudo-random reeks. Niet fout, maar het maakt de locaties niet onafhankelijk
   in hun ruis.

### `fit_copula`: cel 62

Drie varianten. Cel 69 en 70 staan in de sectie die de auteur zelf
`Extra code - Prullenbak` heeft genoemd, cel 62 staat in de actieve sectie
`Calculating de copulas`.

Het verschil is niet klein: cel 62 sampelt onvoorwaardelijk uit de copula
(`random(cop, par, n)` met `n=100000`), cel 69 sampelt conditioneel
(`randomconditional(cop, ui2, par, n, un=2)` met `n=10000`). Cel 70 heeft een
kortere signature zonder `quantiles_weekly_max`.

Canoniek: **62**. Alleen die versie heeft `river`, `village` en `river_location`
in de signature, wat nodig is voor de figuurtitels in de pagina-compositie.

## Geen duplicaat, maar een gemiste parametrisering

`create_page`, cellen 63 en 65: het enige verschil is de titeltekst,
`First period` versus `Second period`. Dat zijn geen concurrerende versies maar
twee hardgecodeerde varianten van dezelfde functie. Wordt één functie met de
periode als argument.

## Discrepantie in de parameters

De parametercel zet `threshold=0.5`, maar alle drie de daadwerkelijke aanroepen
van `drought_flood_p_value_trigger_ECA` in cel 54, 55 en 103 geven expliciet
`threshold=1` mee. De gepubliceerde resultaten zijn dus met `threshold=1`
berekend, niet met 0,5.

`period_after_event=4` in de aanroepen klopt wel met de parametercel.

**Floris op 23 augustus 2026: 0,5 was de bedoeling, 1 is wat er is gedraaid.**
Met 0,5 liggen de drempels minder extreem, dus komen er meer events uit
`extract_events`, aan zowel de droogte- als de floodkant.

Of we naar 0,5 gaan of bewust bij 1 blijven is nog niet beslist. Dit staat als
**D-01** in `docs/open-decisions.md`, en de beslissing valt pas als beide
varianten zijn doorgerekend en naast elkaar liggen.

Tot die beslissing valt: `config/analysis.yaml` krijgt beide waardes, met 1
gemarkeerd als "wat de bestaande resultaten maakte" en 0,5 als "bedoelde waarde,
nog niet doorgerekend". Geen van beide wordt stilzwijgend de default.
