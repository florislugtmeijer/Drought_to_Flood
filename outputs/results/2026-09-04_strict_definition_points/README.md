# Strikte definities: puntschattingen en diagnoses

Gevoeligheidsvariant, 4 september 2026. Droogte bij SRI < -1 in plaats van -0,5,
floodniveau gespiegeld naar norm.cdf(1) = 0,8413. Bevat de referentie op 0,5 in
dezelfde run met dezelfde seeds. Geen bestaande code aangepast.

- `summary.csv`, `curves.csv`: per cel en variant de puntschatting op vier afleesniveaus
- `week_overlap.csv`: hoe vaak een week tegelijk droogte en flood is, per variant
- `post_drought_sri.csv`: de toestand van de rivier in de vier weken na afloop van een
  droogte, per variant (script 30)

Kern: bij strikt is het venster na een droogte droger dan een willekeurig venster,
bij 0,5 natter. Dat komt doordat het einde van een strenge droogte de rivier nog in
milde droogte achterlaat. De X-grenzen voor mild en zwaar van pagina 22 zijn
ongewijzigd, waardoor bij strikt de milde curve met de onafhankelijkheidslijn
samenvalt. Het vergelijkende rapport staat in `results/2026-09-04_strict_definition_report/`.
