# Betrouwbaarheidsintervallen bij de transitiekansen, met toetsen en copulakeuze

Het volledige verslag staat in **`report.md`** in deze map. Dit is het antwoord op
beide helften van reviewerpunt R4-03, berekend op de gerepareerde eventdefinities
van 2 september en met de vier besluiten van Floris erin.

Kern: 2000 bootstrap-replicaties per cel waarin de hele keten opnieuw wordt gedaan,
inclusief de copulakeuze. Daarnaast per cel vier onafhankelijkheidstoetsen uit
`../2026-09-02_dependence_tests/`. Twaalf cellen tonen over minstens drie toetsen
echte severity-afhankelijkheid: positief bij Po, Ebro, Tagus en Danube, negatief
bij Vistula en Weser. Het marginale deel, natter venster na droogte, is de breedste
bevinding. De copulakeuze zelf is zelden hard, mediaan 37 procent herhaalkeuze over
de replicaties.

Figuren in `figures/`: ci_example, ci_decomposition, ci_per_river,
dependence_overview.
