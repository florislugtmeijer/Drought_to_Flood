# Productierun ECA Monte Carlo onder nul C′, met B′ en A als grenzen

Besluit D-21 van 21 oktober 2026, zie `CHANGELOG-methodology.md` entry
2026-10-21 en `docs/open-decisions.md`. Gemaakt door
`scripts/36_run_eca_null_production.py`, 10.000 simulaties per cel en nul,
threshold 0,5, de 48 locaties en beide periodes.

**Baseline.** De cijfers onder de gepubliceerde nul A staan onveranderd in
`results/2026-09-02_sensitivity_grid_endfix/` (2000 simulaties). Deze run
rekent A daarnaast opnieuw mee op 10.000 simulaties met exact dezelfde events
als B′ en C′, zodat elke verschuiving binnen één bestand te herleiden is tot
de nul en niet tot de keten.

**Nullen.** A = starts op alle weken (gepubliceerd). B′ = gestratificeerd: het
waargenomen aantal starts op droogteweken uniform over de droogteweken, de
rest over de niet-droogteweken. C′ = B′ plus de startregel (week ervoor in de
waargenomen floodreeks geen flood), de nul van de toets per het besluit.
D′ staat apart in `results/2026-09-05_eca_null_dprime/`.

**Let op.** De diagnose van 4 september (2000 simulaties, scratchpad, gewist)
is hier herbouwd volgens de beschrijving in D-21; de staartregel van A
(laatste 4 weken geen kandidaat) geldt in deze run voor alle drie de nullen.
Kleine afwijkingen van de diagnosecijfers zijn mogelijk, de cijfers uit deze
map zijn leidend.

`production_smoke.csv` is de rekentijdmeting (2 locaties, 500 simulaties) en
telt niet mee.
