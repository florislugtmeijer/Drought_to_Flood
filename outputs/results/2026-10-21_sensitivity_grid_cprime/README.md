# Gevoeligheidsraster ECA onder nul C′, met B′ en A als grenzen

Vervolg op het D-21-besluit van 21 oktober 2026 en de productierun in
`results/2026-10-21_eca_null_production/`. Gemaakt door
`scripts/37_sensitivity_grid_cprime.py`: 5 SRI-drempels (0,25 / 0,5 / 0,75 /
1,0 / 1,5) × 5 floodpercentielen (0,60 / 0,6915 / 0,80 / 0,90 / 0,95) × 48
locaties × 2 periodes, venster 4 weken, 10.000 simulaties per cel en nul.

De flood- en droogtezijde zijn ontkoppeld (flood_quantile apart van de
SRI-drempel), zoals in het raster van 1 september. De cel (0,5, 0,6915) is de
hoofdconfiguratie; die hoort de productierun te reproduceren op de seed na.
Nullen en zelfcontroles identiek aan script 36, zie de README van de
productiemap. Cellen waar een laag niet past of waar geen events zijn, staan
erin met een melding in de kolom `selfcheck`.

Dient T-62 (effectrapport locatiespecifieke claims), R4-01 (de
drempelonderbouwing) en de gevoeligheidsrapportage bij het D-21-besluit.
Vergelijkingsmateriaal onder de gepubliceerde nul A:
`results/2026-09-02_sensitivity_grid_endfix/`.

`grid_smoke.csv` is de rekentijdmeting (1 locatie, 500 simulaties) en telt
niet mee.

**Controle hoofdcel, 21 oktober 2026.** De cel (0,5 / 0,6915) reproduceert de
productierun bij 94 van de 96 runs exact in events en matches; mediaan
|pC′-verschil| 0,0001, maximum 0,0094 (seedruis). Twee runs wijken één
floodstart af (Elbe Wittenberge en Ebro Haro, beide periode 2): het raster
gebruikt de afgeronde drempel 0,6915 waar de productierun norm.cdf(0,5) =
0,6914625 gebruikt, en bij deze twee ligt één weekquantiel daartussen. Effect
op de p-waardes hooguit 0,001. Zelfcontroles: 2395 van de 2400 cellen ok, 5
niet toetsbaar (geen events bij de strengste drempels).
