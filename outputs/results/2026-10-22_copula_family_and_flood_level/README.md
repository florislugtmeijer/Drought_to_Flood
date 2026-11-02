# Copulakeuze met de nummer twee, en transitiekansen bij 0,6915

Gemaakt door `scripts/40_copula_family_and_flood_level.py`, 22 oktober 2026, 0,9
minuut. Puntschattingen van script 22 exact nagebouwd (grootste afwijking op het
rooster 5e-07, de afronding van de bootstrap), met 0,6915 aan het rooster
toegevoegd. Zie `check.txt`.

## D-16, hoe hard staat de familiekeuze (190 cellen)

- AIC-verschil met de nummer twee: mediaan 0,37; onder 2 in 166 cellen, onder 1
  in 138
- maximaal verschil tussen de curves van winnaar en nummer twee, over alle
  floodquantielen:
  - milde curve: mediaan 0,022, p90 0,087, groter dan 0,10 in 13 cellen
  - zware curve: mediaan 0,117, p90 0,331, groter dan 0,10 in 104 cellen
- de milde curve is dus nauwelijks gevoelig voor de familiekeuze, de zware wel:
  daar is de curve grotendeels extrapolatie in de staart van de copula

## N-1, bij floodniveau 0,6915

- mediaan gat conditioneel min unconditioneel +0,055, positief in 138 van 190
  (gelijk aan script 28, changelog 2026-10-21 derde)
- mediaan marginaal deel +0,058, mediaan copula-deel -0,010
- zware curve niet gedefinieerd in 13 cellen

Intervallen bij 0,6915 staan hier niet in: de bootstrap rekent op het rooster
van 0,01.

## Kolommen van cells.csv

`family`, `aic` de gekozen familie; `runner_up`, `aic_runner_up`, `delta_aic` de
nummer twee; `max_abs_diff_minor/major` het grootste verschil tussen hun curves;
`diff_*_at_q` dat verschil bij 0,6915; `*_at_q` de puntwaarden bij 0,6915 van de
milde en zware curve, de unconditionele curve, de onafhankelijkheidslijn
1 - F_Y, het gat, het marginale deel, het copula-deel en zwaar min mild.
