# Heeft de gedeelde code de gepubliceerde resultaten gemaakt?

Vraag van Floris, 23 augustus 2026.

**Antwoord: ja, geverifieerd.** Met de juiste combinatie:

| | |
|---|---|
| code | `notebooks/drought_to_flood_europe_r1_published.ipynb` |
| data | `8_maart_european_river_runoff_1994_2024.nc`, 48 punten, 10958 dagen |
| parameters | `threshold=1`, `period_after_event=4`, `time_scale="1W"`, 10000 simulaties, `seed=42` |

## Het bewijs

Een getrouwe port van deze notebook staat in `src/dtf/pipeline.py`. Uitkomsten
naast Tabel 3, eerste periode:

| locatie | Poisson berekend | afgerond op 3 | Tabel 3 | Monte Carlo berekend | Tabel 3 |
|---|---|---|---|---|---|
| Aschach an der Donau | 0,0046 | 0,005 | 0,0050 | **0,0057** | **0,0057** |
| Visegrád | 0,0517 | 0,052 | 0,0520 | **0,0757** | **0,0757** |
| Donji Milanovac | 0,3980 | 0,398 | 0,3980 | **0,4477** | **0,4477** |
| Krementsjoek | 1,0000 | 1,000 | 1,0000 | **1,0000** | **1,0000** |

De Monte Carlo p-waardes zijn exact gelijk, op vier decimalen, bij dezelfde seed
en hetzelfde aantal simulaties. Dat is geen toeval en geen benadering.

De Poisson-waardes wijken in de vierde decimaal af omdat Tabel 3 op drie
decimalen is afgerond. Dat komt uit `safe_format` in de bron, die
`f"{float(value):.3f}"` doet. 0,0046 wordt 0,005, en zo staat het in de tabel.

## Correctie op een eerdere conclusie in deze repo

De eerste analyse ging over
`notebooks/legacy/drought_to_flood_europe_colab_2026-08-23.ipynb`, de
`LAATSTE_VERSIE`-export. Dat is niet de versie achter het artikel. De bevindingen
die daaruit kwamen gelden dus niet voor de gepubliceerde pipeline:

| eerdere bevinding | status in de juiste versie |
|---|---|
| Monte Carlo telt observed vanaf de start van de droogte en de nulverdeling vanaf het einde (D-08) | **niet aanwezig.** Beide gebruiken `end_time`, en de vergelijking is `pd.Timedelta(0) < diff <= delta` aan beide kanten |
| Randomisatie op dagelijks raster bij weekly observaties (D-03) | **niet aanwezig.** `candidate_times` is de weekly geresampleerde `valid_time`, dus de simulatie ligt op hetzelfde raster als de observaties |
| Visegrád op de verkeerde plek, lookup pakt Łączany (D-09) | **niet aanwezig.** Deze dataset heeft Visegrád op 47,7922 / 18,9060, en dat is de Donau bij Visegrád in Hongarije |
| Tabel 3 niet reproduceerbaar (D-10) | **weerlegd.** Zie hierboven |

De `LAATSTE_VERSIE`-export blijft in `notebooks/legacy/` staan als afgedankte
zijtak. Hij is nuttig als waarschuwing, niet als bron.

Twee verschillen in de locatielijst verklaren waarom de vorige combinatie niet
kon kloppen: de gepubliceerde versie heeft Meuse upstream als Dun-sur-Meuse en
Oder downstream als Kostrzyn nad Odra, waar de afgedankte versie
Charleville-Mézières en Glogow heeft.

## Wat wel blijft staan

**D-01, de threshold.** De code draait op `threshold=1`, wat de 84e quantile en
SRI < -1 geeft. Het manuscript beschrijft op pagina 17 een Z-score van 0,5 en de
69e quantile. Dat is nog steeds een discrepantie tussen de beschreven methode en
de uitgevoerde berekening, en Floris heeft aangegeven dat 0,5 de bedoeling was.

**D-02, de off-by-one.** `first_end=5479` en `second_begin=5480` laten index 5479
buiten beide periodes vallen. Met deze dataset is dat 1 januari 2010. Periode 1
loopt van 1995-01-01 tot en met 2009-12-31 (5479 dagen), periode 2 van
2010-01-02 tot en met 2024-12-31 (5478 dagen). Het manuscript noemt de periodes
1995-2009 en 2010-2024, dus de bedoeling was twee blokken van 15 jaar.

**De lookup zonder maximale afstand.** `find_nearest_grid_point` heeft geen
bovengrens. Nu gaat het goed omdat de dataset de exacte config-coördinaten
bevat, dus de afstand is nul. Maar de fout die in de afgedankte tak optrad kon
alleen ongemerkt gebeuren doordat die grens er niet is. Waard om er een te zetten
voordat er nieuwe data bijkomt.
