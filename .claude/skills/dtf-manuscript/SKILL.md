---
name: dtf-manuscript
description: Werkafspraken voor de tekst van het Drought-to-Flood Europe manuscript. Gebruik bij elke wijziging in manuscript/ of review/, bij het formuleren van antwoorden aan reviewers, bij het bijwerken van cijfers, figuren of tabellen in de tekst, en bij het koppelen van beweringen aan de code die ze onderbouwt.
---

# Manuscript-afspraken Drought-to-Flood Europe

Wetenschappelijk proza voor een tijdschrift, met reviewers aan de andere kant.
Twee dingen tegelijk: de tekst moet kloppen, en elke kwantitatieve bewering moet
terug te voeren zijn op code die hem oplevert.

## Tekst en code bij elkaar houden

`manuscript/claims.yaml` is de brug. Elke kwantitatieve bewering in het artikel
krijgt een regel:

```yaml
- id: c-012
  claim: "In 31 of the 48 locations the ECA p-value drops below 0.05 in the second period."
  section: Results, paragraaf 3
  source_script: scripts/01_eca.py
  source_result: results/2026-08-23_eca/eca_second_period.csv
  verified: 2026-08-23
```

Twee gebruiksrichtingen. Verandert er een berekening, dan zie je via
`source_result` welke passages in de tekst mee moeten. Verandert er een getal in
de tekst, dan is `verified` de plek waar je aantoont dat het nog klopt. Een
bewering zonder regel in `claims.yaml` is een bewering die bij de volgende
herberekening stil verkeerd wordt.

Zet bij het toevoegen van een claim het getal er letterlijk in zoals het in de
tekst staat, niet een omschrijving. Dan is een mismatch met de resultaten
machinaal te vinden.

## Terminologie, consequent aanhouden

- **drought-to-flood** met streepjes, kleine letters, ook als bijvoeglijk gebruik
- **event coincidence analysis**, afgekort **ECA**, bij eerste gebruik uitschrijven
- **SRI** voor de standardised runoff index, bij eerste gebruik uitschrijven
- **discharge** waar het over de GloFAS-variabele gaat, **runoff** waar het over
  de afgeleide reeksen gaat. Niet door elkaar.
- rivier- en plaatsnamen in het Engels waar een Engelse naam bestaat: Rhine,
  Danube, Meuse, Vistula. In `config/locations.yaml` staan een paar Nederlandse
  namen (Straatsburg, Warchau, Turijn, Krementsjoek), die horen in de tekst niet
  thuis.

## Reviewer-feedback

Feedback komt in `review/round-<n>.md`, per punt genummerd `R1-01`, `R1-02` en zo
verder. Per punt vastleggen:

- het punt, letterlijk geciteerd
- classificatie: tekst, code, of beide
- wat de wijziging inhoudt
- status: open, in behandeling, gedaan, of afgewezen met reden
- verwijzing naar de commit of het bestand waar het is verwerkt

Het openstaande werk dat uit die feedback volgt staat als taak in
`docs/todo.md`. Lees die werklijst aan het begin van een sessie en werk hem aan
het eind bij. `review/round-<n>.md` blijft de plek voor het punt zelf, het citaat,
de classificatie en het eigen standpunt.

Uit die bestanden schrijf je het response-to-reviewers document, niet omgekeerd.
Dat scheelt aan het eind een reconstructie.

Raakt een punt de methodologie, dan gaat het ook naar
`CHANGELOG-methodology.md`. Zie de code-skill voor die kant.

Een punt afwijzen is een legitieme uitkomst, maar wel met een onderbouwing die
in het response-document kan staan. Formuleer die meteen, niet later.

## Toon van de tekst

Wetenschappelijk Engels, geen overstatement. Concreet:

- geen "significantly" waar geen toets onder ligt
- geen "proves", wel "indicates" of "is consistent with"
- resultaten in de verleden tijd, interpretatie in de tegenwoordige
- getallen met een consistent aantal decimalen per grootheid, vastgelegd zodra we
  het eerste keer kiezen
- p-waardes als `p < 0.05` of met twee decimalen, niet allebei in één artikel

## Figuren en tabellen

Figuren worden gegenereerd uit `results/`, nooit met de hand bijgewerkt. Staat er
een figuur in de tekst die niet uit een script komt, dan is dat een openstaand
punt en hoort het benoemd te worden.

Verwijzingen in de tekst als "Figure 3" en "Table 2", en de bronbestanden in
`manuscript/` volgen diezelfde nummering, zodat het naast elkaar te leggen is.

## Vertrouwelijkheid

Manuscript, reviewer-feedback en het response-document zijn niet openbaar zolang
het artikel in review is. Voordat er iets naar een publieke plek gaat, eerst
nagaan of de repo op privé staat. Bij twijfel niet pushen.

Co-auteurs en het tijdschrift hebben mogelijk afspraken over wat wanneer
openbaar mag. Dat is niets om zelf in te vullen, dat is een vraag aan Floris.

## Openstaand

Welke `.docx` de actuele manuscriptversie is, staat nog niet vast. Kandidaten
zijn `2. DTF_Europe_research_paper_manuscript.docx` (16 maart) en
`DTF_Europe_reasearch_paper_manuscript_22_03_26.pdf.pdf.docx` (22 maart), plus
losse `References.docx` en `Tables - Europe - DTF - Research Paper.docx`. Niet
zelf kiezen, vragen.

Zie ook de skill `dtf-code` voor de codekant.
