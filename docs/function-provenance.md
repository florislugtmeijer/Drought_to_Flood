# Welke functievariant is canoniek

Bron: `notebooks/drought_to_flood_europe_r1_published.ipynb`, de versie waarmee
Tabel 3 is gereproduceerd. 64 cellen, 28 code, 34 functiedefinities voor 28
unieke functies.

Dit is een stuk schoner dan de afgedankte `LAATSTE_VERSIE`-tak, die 47
definities voor 33 functies had met veertien onverenigbare varianten. Hier zijn
vier functies dubbel en is de keuze in alle vier de gevallen eenduidig.

| functie | cellen | canoniek | waarom |
|---|---|---|---|
| `SRI_calculate` | 12, twee keer in dezelfde cel | **de tweede** | Bij twee definities in één cel wint de laatste bij uitvoeren. De tweede pooled week 53 met week 52 en eist minstens 5 waardes voor de gamma-fit, met clipping op de CDF. Dat is de versie die de resultaten heeft gemaakt en de betere van de twee. |
| `create_page` | 27, 31 | **31** | De tweede is A4-liggend met 3 paren per pagina en een `period_key`-argument in plaats van hardgecodeerde periodetitels. Cel 31 staat na 27, dus die wint. |
| `process_img` | 27, 31 | **31** | Alleen dpi verschilt, 200 tegen 300. |
| `analyze_location_data` | 39, 47, 49, 51 | **geen van vier** | Dit zijn de Colab "Task / Subtask" cellen achteraan, waar een assistent de functie stap voor stap opbouwt. Ze worden nergens gebruikt voor Tabel 3. Bij het overzetten naar `src/dtf/` gaan ze niet mee. |

## Het echte werk zat elders

De canonieke variant hier vaststellen was eenvoudig. De moeilijkheid zat in het
vinden van de juiste notebook, niet in het kiezen tussen functies binnen die
notebook. Zie `docs/reproducibility-check.md`.

## Wat in de port is aangepast

`src/dtf/pipeline.py` is een getrouwe port. Twee wijzigingen, beide gemarkeerd
met `PORT:` in de code, en beide zonder effect op de uitkomsten:

1. `transform_to_quantiles` gebruikt `np.searchsorted` op de gesorteerde
   referentie in plaats van `np.vectorize` met een Python-lus. Zelfde definitie
   van het empirische quantiel, orde van grootte sneller.
2. `Intensity_calc` krijgt een `Dataset` in plaats van een `DataArray` waar
   variabelen als coördinaat aan werden gehangen. Zelfde getallen, leesbaarder.

De verificatie tegen Tabel 3 is met deze port gedaan, dus beide wijzigingen zijn
aantoonbaar gedragsneutraal.

## Nog niet overgezet

De copula-kant (`fit_copula`, `copula_func_drought_peak`,
`copula_func_mean_drought_severity`) en de figuurcompositie zitten nog niet in
`src/dtf/`. Die hebben `vinecopulas` nodig. De ECA-kant, die Tabel 3 oplevert,
is compleet.
