---
name: dtf-code
description: Werkafspraken voor de code van het Drought-to-Flood Europe onderzoek. Gebruik bij elke wijziging in src/dtf/, scripts/, config/ of data/, bij het overzetten van Colab-code naar modules, bij het herberekenen van resultaten, en bij het verwerken van reviewer-feedback die de code raakt.
---

# Code-afspraken Drought-to-Flood Europe

Dit is onderzoekscode achter een manuscript dat in review is. De maatstaf is niet
elegantie, het is herleidbaarheid: bij elk getal in het artikel moet aanwijsbaar
zijn welke code met welke parameters het heeft gemaakt.

## Harde regels

**Eén definitie per functie.** De Colab-bron had 47 definities voor 33 functies,
waarvan 14 met onverenigbare varianten. Dat is precies wat we oplossen. Een
tweede definitie van een bestaande functie is een fout, geen variant. Moet er een
alternatieve berekening naast bestaan, geef die een eigen naam die het verschil
benoemt.

**Parameters komen uit `config/`, nooit uit de code.** Alle waardes uit
`config/analysis.yaml` en `config/locations.yaml` worden ingelezen en
doorgegeven. Een getal als `0.5`, `0.9` of `5479` hoort niet in een
functiebody en niet als default in een signature. Wie een parameter wil
overschrijven doet dat via config of een expliciet argument.

**Geen Colab-paden.** Geen `/content/`, geen `/content/drive/MyDrive/`. Paden
komen uit config, met de repo-root als anker.

**Data verifiëren voor gebruik.** `data/manifest.yaml` bevat naam, grootte,
SHA256 en herkomst van elk databestand. De loader controleert de checksum en
faalt hard bij een afwijking. Bij een onverwacht resultaat weet je dan meteen of
het de code of de data is.

## Methodologie wijzigen

Elke wijziging die de uitkomsten kan veranderen krijgt een regel in
`CHANGELOG-methodology.md`, met:

- wat er is veranderd, in één zin
- waarom, en als het uit review komt het nummer van het reviewerpunt
- welk effect het had op de resultaten, met getallen

Geen wijziging aan de methodologie zonder dat Floris ermee heeft ingestemd. Bij
twijfel of iets methodologie is of alleen vorm: het is methodologie.

## Resultaten

Output gaat naar `results/<datum>_<korte-omschrijving>/` met daarin een
`manifest.yaml`:

```yaml
run_date: 2026-08-23
git_commit: <hash>
config: {...}          # de volledige gebruikte parameters
inputs:
  definitive_file_6_04_25.nc: <sha256>
python: 3.12.x
packages: {...}        # uit uv.lock
```

Resultaten uit een vorige run worden nooit overschreven. Een herberekening is een
nieuwe map, zodat vergelijken mogelijk blijft.

## Bekende openstaande punten

**Off-by-one in de periodesplitsing.** `data.isel(valid_time=slice(begin, end))`
is exclusief aan het eind. Met `first_begin=0, first_end=5479,
second_begin=5480, second_end=10958` betekent dat: periode 1 is index 0 tot en
met 5478 (5479 dagen), periode 2 is 5480 tot en met 10957 (5478 dagen), en index
5479 valt in geen van beide. Ongelijke periodes en een weggevallen dag. Nog niet
gecorrigeerd, want dat verandert de gepubliceerde resultaten. Niet stilzwijgend
aanpassen.

**Welke duplicaat is canoniek.** Uitgezocht, zie
`docs/function-provenance.md` voor de volledige onderbouwing. Kort: negen van de
veertien functies verschilden alleen in docstrings, comments en debug-prints. Cel
49 is een geconsolideerde opgeschoonde kopie, geen vereenvoudigde
herimplementatie. De drie echte keuzes zijn beslecht met bewijs uit het notebook:
`drought_flood_p_value_trigger_ECA` uit cel 50 (bevestigd door Floris, matching
hoort vanaf de start van de droogte), `monte_carlo_p_value` uit cel 49,
`fit_copula` uit cel 62. Die laatste twee wachten nog op bevestiging.

**Openstaande beslissingen staan in `docs/open-decisions.md`.** Lees dat bestand
voordat je aan de analyse of de tekst werkt. Nu open: de threshold van 0,5 tegen
1 (D-01, raakt alle event-aantallen en p-waardes), de off-by-one in de
periodesplitsing (D-02), de dagelijkse randomisatie bij weekly observaties
(D-03), de vaste seed over locaties (D-04).

Los een openstaande beslissing nooit zelf op door een waarde te kiezen. Reken
beide varianten door, leg ze naast elkaar, en laat Floris beslissen. Een
beslissing die valt gaat naar `CHANGELOG-methodology.md` en uit
`open-decisions.md`.

## Omgeving

`uv` met Python 3.12. Alles gepind in `uv.lock`. `vinecopulas` is een
niche-package met weinig gebruikers, dus die versie staat vast, anders is dit
over een jaar niet meer te draaien.

## Sanity checks, standaard

Bij elke run op nieuwe of gewijzigde data, voor je naar de uitkomsten kijkt:
uitschieters, NaN's en infinities, dubbele tijdstappen, gaten in de reeks,
locaties die op hetzelfde gridpunt uitkomen, en of het aantal tijdstappen klopt
met de verwachte periode. Meld wat je tegenkomt voordat je conclusies trekt.

Zie ook de skill `dtf-manuscript` voor de tekstkant.
