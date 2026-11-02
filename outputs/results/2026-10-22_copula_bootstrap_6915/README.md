# Bootstrap van de transitiekansen, met floodniveau 0,6915 in het rooster

Gemaakt door `scripts/22_bootstrap_transition_ci.py` met
`OUT=results/2026-10-22_copula_bootstrap_6915 EXTRA_Q=0.6915`, 22 oktober 2026,
84,9 minuten, vastgepinde omgeving (`uv run --frozen`). Zelfde opzet als de run
van 3 september (`results/2026-09-02_copula_bootstrap/`): B = 2000, iid en
circulaire blokbootstrap, familie-herselectie per replicatie, seeds per
locatie-periode uit SeedSequence(42).

Het enige verschil is de extra kolom `y_q6915` in `transition_ci.csv`, de
waarden bij precies het floodniveau van het manuscript.

## Controle tegen de run van 3 september

- `transition_ci.csv`: 10.640 rijen, op alle 101 roosterpunten identiek
  (grootste verschil 0,0, zelfde patroon van ontbrekende waarden). De run van
  3 september is daarmee exact gereproduceerd
- `bootstrap_diagnostics.csv`: familiekeuze, stabiliteit, aantal families en
  mislukte replicaties identiek. Vier samenvattende kolommen verschillen een
  fractie (`median_bias`, `median_width_minor`, `median_width_diff`,
  `supt_over_196`), omdat ze een mediaan of maximum over alle floodniveaus nemen
  en er nu één niveau bij is. Voor die vier blijft de run van 3 september de
  referentie

## Bij 0,6915 (iid)

- copula-deel: interval boven nul in 13 cellen, onder nul in 9, van 190
- marginaal deel: boven nul in 44, onder nul in 14
- zwaar min mild: boven nul in 0, onder nul in 2
