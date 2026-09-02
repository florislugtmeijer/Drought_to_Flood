# Werklijst revisie HYDROL79380R1

**Bijgewerkt: 1 september 2026, na de beslissing over de threshold (T-01).** Deadline hersubmissie **17 september 2026**, dat
is 16 dagen. Er ligt een concept-uitstelverzoek klaar, zie T-52. Dit is de enige lijst waar het werk op staat. De onderbouwing staat
elders, hier staat wat er moet gebeuren, wie het doet en waar het op wacht.

Bronbestanden waar dit uit komt:

| bron | inhoud |
|---|---|
| `review/round-2.md` | reviewerpunten AE, R1, R4 en de formele eisen ED |
| `docs/open-decisions.md` | wat uit de code of de data komt, D-nummers |
| `docs/proposed-changes.md` | wat Floris zelf voorstelt, P-nummers |
| `docs/function-provenance.md` | wat nog niet is overgezet uit de notebook |
| `.claude/skills/dtf-code`, `dtf-manuscript` | werkafspraken, en de bestanden die die eisen |

## Hoe deze lijst wordt bijgehouden

Bij elke sessie waarin aan dit project wordt gewerkt: eerst deze lijst lezen, aan
het eind bijwerken. Een taak die klaar is verhuist naar het laatste blok met de
datum erbij, hij wordt niet weggehaald.

Statuswaardes: `open`, `loopt`, `wacht op Floris`, `geblokkeerd`, `gedaan`,
`vervallen`. Bij `geblokkeerd` staat erbij door welke taak.

De lijst voegt niets toe aan de bestaande nummering. T-nummers zijn taken, de
D-, P-, R-, AE- en ED-nummers blijven de bron. Eén taak kan meerdere bronpunten
afdekken, en één bronpunt kan over meerdere taken lopen.

Elke taak begint met een regel **herkomst**. Daar staat in woorden van wie het
punt komt, niet alleen een code. Zie de legenda hieronder.

Nieuwe bevindingen gaan eerst naar `open-decisions.md` of `proposed-changes.md`,
en pas daarna hier als taak. Deze lijst is geen plek om iets voor het eerst op te
schrijven.

## Waar een taak vandaan komt

Elke taak heeft een regel **herkomst**. Vier soorten, en het verschil is
belangrijk: bij de eerste twee kijkt straks iemand anders mee of je het hebt
gedaan, bij de laatste twee niet.

| soort | betekenis | codes |
|---|---|---|
| **Reviewer** | een van de twee reviewers vraagt dit. Moet beantwoord worden in de Revision Notes | `R1-xx` = **Reviewer #1**, `R4-xx` = **Reviewer #4** |
| **Editor** | de associate editor of een formele eis uit de beslissingsbrief | `AE-xx` = associate editor, `ED-xx` = formele eis |
| **Eigen bevinding** | door ons gevonden in de code of de data, niet gevraagd door iemand | `D-xx` in `docs/open-decisions.md` |
| **Voorstel Floris** | door Floris zelf voorgesteld | `P-xx` in `docs/proposed-changes.md` |
| **Werkafspraak** | volgt uit de skills, maakt het werk controleerbaar | geen nummer |

Let op de nummering van de reviewers. Het tijdschrift noemt ze **Reviewer #1** en
**Reviewer #4**, er is geen #2 of #3. `R1` slaat dus op de reviewer en niet op
ronde 1. De ronde staat in de bestandsnaam, `review/round-2.md`.

## Wie vraagt wat

### Reviewer #1, zeven punten, algemeen oordeel positief

> "This article is in good shape and requires only some improvements"

De rode draad: veel statistiek, weinig hydrologische interpretatie. Vrijwel
alles is tekstwerk.

| punt | wat | taak |
|---|---|---|
| R1-01 | abstract blijft vaag over de kernbevinding | T-20 |
| R1-02 | sectie Spatial dimension inkorten | T-21 |
| R1-03 | overgang naar de eigen studie scheiden | T-22 |
| R1-04 | definities naar sectie 2.3 | T-23 |
| R1-05 | keuze van de variabelenparen onderbouwen | T-24 |
| R1-06 | Tabel 3 introduceren in 3.1 | T-25 |
| R1-07 | figuuruitleg in 3.2 uitbreiden | T-26 |
| R1-08 | discussie en conclusie te dun, appendices te zwaar | T-27, T-17 |
| R1-09 | Appendix D, figuurtitels te klein | T-16 |

### Reviewer #4, zes punten, en de editor tilt deze boven de rest uit

> "several substantial shortcomings that undermine the robustness and
> interpretability of the results"

Dit is het zware blok. Vier van de zes vragen nieuw rekenwerk.

| punt | wat | taak | rekenwerk |
|---|---|---|---|
| R4-01 | geen gevoeligheidsanalyse op de drempels | T-10 | ja, zwaarste punt |
| R4-02 | geen validatie tegen meetreeksen | T-12 | ja, externe databron nodig |
| R4-03 | copulakeuze en betrouwbaarheidsintervallen niet gerapporteerd | T-11 | ja, bootstrap bestaat nog niet |
| R4-04 | verlaagde transitiekans niet verklaard | T-13 | deels gedaan |
| R4-05 | lokale factoren niet gekwantificeerd | T-14 | hangt van de gekozen omvang af |
| R4-06 | p-waardes in Tabel 3 afronden | T-15 | nee |

### Associate editor

| punt | wat | taak |
|---|---|---|
| AE-01 | de punten van Reviewer #4 zijn fundamenteel, die gaan voor | weging over T-10 tot T-14 |
| AE-02 | fysische interpretatie en kernbevindingen versterken | T-28, bundelt R1-01, R1-08, R4-04 |

### Formele eisen uit de beslissingsbrief

| punt | wat | taak |
|---|---|---|
| ED-01 | regelnummers in het manuscript | T-32 |
| ED-02 | Revision Notes met regelverwijzingen | T-33 |
| ED-03 | gemarkeerde versie meesturen | T-34 |
| ED-04 | afwijkende meningen onderbouwen | T-35 |
| ED-05 | Word-bronbestanden, geen PDF | T-31 |
| ED-06 | figuren en tabellen als losse bestanden | T-36 |
| ED-07 | deadline 17 september | T-37, T-52 |

### Niet van een reviewer

Deze staan op de lijst omdat wij ze hebben gevonden of omdat Floris ze voorstelt.
Ze zijn niet gevraagd, maar T-29 en T-30 zijn wel correcties van fouten in de
tekst die een reviewer bij de volgende ronde kan vinden.

| taak | herkomst |
|---|---|
| T-02, T-03, T-04, T-05 | eigen bevindingen D-11, D-13, D-02, D-04 en voorstel P-02 |
| T-18, T-19, T-30 | eigen bevindingen D-09, D-12 |
| T-29 | correctie van de methodensectie, uit D-01, D-11, D-13 |
| T-40 tot T-46 | werkafspraken uit de skills |
| T-47 tot T-51 | administratie en repo |


---

## A. Beslissingen die het rekenwerk blokkeren

Zolang deze open staan is elke herberekening voorlopig. Alle vijf zijn van
Floris. Dit is het kritieke pad.

### T-01. Threshold definitief vastleggen op 1 of 0,5
- herkomst: **Reviewer #4** (R4-01) · eigen bevinding D-01 · voorstel Floris P-01
- wie: Floris, mogelijk met de co-auteurs
- status: **gedaan, 1 september 2026. Threshold gaat naar 0,5 voor beide
  onderdelen.** Een eerdere beslissing diezelfde dag om op 1 te blijven is
  herroepen. Zie `CHANGELOG-methodology.md`
- **gevolg: Tabel 3 moet volledig herrekend, 10 naar 45 significante locaties van
  de 48.** Cijfers liggen al in `results/2026-08-23_threshold_comparison/`, maar
  moeten nog in de tekst en de tabel landen. Zie T-54
- cijfers liggen klaar in `results/2026-08-23_threshold_comparison/`: 10 tegen 45
  van de 48 locaties significant
- blokkeert: T-10, en elk getal in de tekst
- prioriteit: hoog

### T-02. Quantielreferentie van de flooddrempel
- herkomst: voorstel Floris P-02 · eigen bevinding D-11 · **niet door een reviewer gevraagd**
- wie: Floris
- status: **gedaan, 1 september 2026, na de rerun op 0,5. De berekening blijft
  ongewijzigd.** De floodquantielen worden bepaald tegen de volledige dagelijkse
  afvoerreeks van de periode zelf, dus `quantile_reference="daily"` en
  `reference_window=None`. Geen enkel cijfer in Tabel 3 verandert hierdoor
- gekozen op de inhoudelijke verdediging, niet op de cijfers. De 69,1e percentiel
  van de dagelijkse verdeling is een herkenbare hydrologische grootheid, het debiet
  dat op ongeveer 31 procent van de dagen wordt overschreden. De spiegelvariant
  zou dat opgeven voor een drempel die per constructie 30,9 procent van de weken
  aanmerkt bij elke rivier, los van elk fysiek niveau
- **nieuwe tekstcorrectie die hieruit volgt.** De methodensectie zegt "quantiles
  relative to the entire dataset for each location", en dat beschrijft de code
  niet. De referentie is de periode, 5479 dagen, niet de volledige 10958. In D-11
  stond dat de tekst hier al mee overeenkwam, en dat was onjuist. Zie T-29
- eerdere status, voor de historie: op 1 september eerst gesloten op cijfers uit
  `results/2026-08-23_quantile_reference_variant/`, dat is een run met
  `threshold=1`. Die sluiting is ingetrokken omdat T-01 de threshold op 0,5 zette
- **het cijfer "18 locaties verliezen significantie, periode 2 houdt er nul over"
  geldt alleen bij threshold 1.** Bij threshold 1 was de hoofdbevinding marginaal,
  34,0 procent geobserveerd tegen 28,6 verwacht, minder dan één standaardfout. Bij
  0,5 is dat 57,3 tegen ongeveer 35, ruim vier standaardfouten. Een strengere
  flooddrempel doet daar iets heel anders
- **opnieuw doorgerekend, 1 september 2026, `results/2026-09-01_reference_grid/`.**
  Twee van de drie argumenten kantelen:
  1. het cijfermatige argument is weg. 89 van 96 runs significant tegen 90 nu,
     drie locaties verliezen, twee winnen
  2. het symmetrie-argument draait om en pleit nu vóór aanpassen. De onbalans
     tussen flood- en droogtezijde gaat van 9,17 naar 5,37 procentpunt
  3. de inhoudelijke verdediging staat nog, dus de absolute flooddrempel als
     herkenbare hydrologische grootheid
- **blijft staan, los van deze beslissing:** de droogtezijde is bij 0,5 zelf
  verkeerd geijkt, 35,8 procent waar 30,85 hoort, en de SRI-mediaan ligt op -0,06
  tot -0,16. Bij threshold 1 vielen die fouten tegen elkaar weg. Oorzaak niet
  vastgesteld, zie D-11. Raakt T-01 en T-29
- wel verplicht: de tekst corrigeren, want er is geen mirroring-effect. Zie T-29

### T-03. Referentieperiode voor de drempels, gemeenschappelijk of per periode
- herkomst: eigen bevinding D-13 · **niet door een reviewer gevraagd**
- wie: Floris
- status: **route B, per periode, volgt uit de beslissing bij T-02 op 1 september
  2026.** Daar is gekozen voor de dagelijkse reeks van de periode zelf als
  referentie, en dezelfde `reference_window` bestuurt ook de gammafit van de SRI.
  Er verandert dus niets. **Let op: de vraag is aan Floris gesteld in termen van de
  floodquantielen.** Als je de SRI-zijde apart wil wegen staat dat nog open, en dan
  moet er een variant gedraaid worden die de twee zijdes los zet
- **route B is niet gratis, en dit is nu verplicht.** D-13 stelt als voorwaarde dat
  de methodensectie meldt dat de drempels per periode opnieuw worden bepaald, met
  hoeveel ze verschuiven. Zonder die toelichting leest de lezer de
  tweeperiodenvergelijking anders dan hij bedoeld is. De cijfers liggen klaar,
  zie hieronder. Naar T-29
- **uitkomst.** Bij ijking per periode lijken de twee periodes bijna identiek, 35,9
  tegen 35,6 procent droogteweken. Bij een gemeenschappelijk ijkpunt is periode 2
  aanzienlijk droger, 29,0 tegen 40,4. Het verschil per locatie gaat van mediaan
  1,8 procentpunt naar 13,4, en van 0 naar 20 van de 48 locaties boven 15 punten.
  Rostov gaat van 3,7 naar 64,5 procent droogteweken
- **kosten van route A:** drie locaties verliezen hun significantie, zes bij de
  variant van P-02, nul winnen er een. Het zijn de gereguleerde rivieren in periode
  1, Krementsjoek en de drie Don-locaties
- de 84e percentiel schuift mediaan 8,6 procent tussen de periodes, bij 32 van 48
  locaties meer dan tien procent
- let op: deze as raakt **beide** drempels, want route A in D-13 is één ijkpunt per
  locatie voor beide periodes en dat geldt ook voor de gammafit van de SRI. De
  droogte-aantallen bewegen dus mee, waar de as van T-02 alleen de floodzijde
  raakt
- blokkeert: T-10, en de uitspraken waarin de twee periodes tegen elkaar worden
  afgezet

### T-04. Off-by-one in de periodesplitsing
- herkomst: eigen bevinding D-02 · **niet door een reviewer gevraagd**
- wie: Floris
- status: **gedaan, 1 september 2026. Niet corrigeren.** Het effect is nagerekend
  en nul: op vier locaties exact dezelfde droogte- en floodaantallen en dezelfde
  p-waardes tot vier decimalen, met begin 5479 of 5480. De extra dag valt in de
  eerste weekbin en verandert daar niets
- **wat wel moet: twee feitelijke correcties in de methodensectie**, want de tekst
  klopt niet. Zie T-56

### T-05. Vaste seed over alle 48 locaties
- herkomst: eigen bevinding D-04 · **niet door een reviewer gevraagd**
- wie: Floris
- status: **gedaan, 1 september 2026. Niet aanpassen.** De seed blijft 42 voor alle
  locaties
- **restant: rapporteren.** Het manuscript noemt het aantal simulaties en de seed
  nergens. Appendix A verwijst naar de Monte Carlo maar geeft geen `n` en geen
  seed. Eén regel toevoegen is standaard voor reproduceerbaarheid. Zie T-56

---

## B. Rekenwerk en code

### T-10. Gevoeligheidsanalyse over de drie parameters
- herkomst: **Reviewer #4** (R4-01) · associate editor tilt dit boven de rest uit (AE-01)
- status: **gedaan, 1 september 2026.** Cijfers, figuur en verantwoording in
  `results/2026-09-01_sensitivity_grid/`. Changelog-entry staat er
- opzet: **volledig gekruist, 5 maal 5 maal 5 is 125 cellen, 12000 runs.** In twee
  delen gedraaid, eerst het vlak bij venster 4 plus de vensterlijn, daarna de rest
- **de kop van het antwoord is een gepoolde toets over alle 48 locaties samen**,
  de aggregatie uit Donges et al. 2016 sectie 2.2 vergelijking 6, en niet een
  telling van significante locaties. Haalt het multiple-testing-probleem weg en
  laat niet-toetsbare locaties vanzelf wegvallen
- **uitkomst, en die is gemengd:**
  - de SRI-drempel doet vrijwel niets. Ratio blijft tussen 1,42 en 1,59 terwijl de
    drempel van 0,25 naar 1,5 gaat en het aantal droogtes van 4220 naar 724 zakt
  - het floodpercentiel doet alles, en het venster versterkt dat. **193 van de 250
    cel-periodes houden stand.** Niet-significant per venster, van 50: 7 / 6 / 12 /
    15 / 17. Bij elk venster liggen ze allemaal in de hoek met een hoog
    floodpercentiel
  - **de uiterste hoek herstelt bij geen enkel venster.** Bij drempel 1,5 en
    percentiel 0,95 blijft de ratio tussen 0,62 en 0,85, nergens significant. Dat
    een droogte minder vaak door een extreme flood wordt gevolgd dan bij toeval is
    dus geen artefact van de vensterkeuze. Steviger materiaal voor T-13 dan gedacht
  - het venster: ratio 3,36 bij één week tot 1,17 bij twaalf, overal p < 0,0001.
    **Niet tussen vensters vergelijken**, de nullijn gaat van 0,113 naar 0,737
  - de twee periodes zijn bijna identiek, zelden meer dan 0,05 verschil
- codewijzigingen die hiervoor nodig waren staan in `CHANGELOG-methodology.md`:
  drempels ontkoppeld, Monte Carlo gevectoriseerd en 29x sneller, seed per locatie.
  Beide verificatiepoorten geslaagd
- **beperking die mee moet in de tekst:** de gepoolde nulhypothese randomiseert elke
  locatie onafhankelijk, en dat zijn onze locaties niet. De gepoolde p valt daardoor
  te laag uit. Randomiseren op riviersniveau zou het oplossen, dat is niet gedaan
- wat hieruit volgt: **T-58** voor de tekst, en T-17 kan nu uit
  `per_location_table.csv`

### T-11. Copulakeuze en betrouwbaarheidsintervallen
- herkomst: **Reviewer #4** (R4-03)
- status: open
- twee dingen: per locatie en variabelenpaar rapporteren welke copula AIC koos,
  en betrouwbaarheidsintervallen bij de transitiekansen
- de bootstrap of vergelijkbare methode bestaat nog niet, dus dit is nieuw werk
- prioriteit: hoog

### T-12. Validatie tegen meetreeksen
- herkomst: **Reviewer #4** (R4-02)
- status: open
- eerst uitzoeken wat er beschikbaar is en voor welke locaties, dan pas
  vergelijken. GRDC of nationale diensten, die databron zit nu niet in het project
- realistisch: een deelverzameling locaties, niet alle 48. Wat niet gedekt wordt
  moet in de tekst als beperking staan
- prioriteit: hoog, en dit is het punt met de grootste kans dat het niet volledig
  binnen de deadline past

### T-13. Fysische interpretatie van de verlaagde transitiekans
- herkomst: **Reviewer #4** (R4-04) · ook **Reviewer #1** (R1-08) en associate editor (AE-02)
- status: loopt
- de magnitude-test en de seizoenscontrole zijn hier het begin van het antwoord:
  bij de grootste floods is er geen samenhang, dus bij hoge floodquantielen is er
  niets om op te conditioneren
- nog nodig: ofwel ancillary data die de oorzaak meet, bodemvocht of
  infiltratiecapaciteit, ofwel de claim expliciet als associatie neerzetten
- de drie beperkingen uit `results/2026-08-23_flood_magnitude_test/README.md`
  moeten mee in de tekst, niet weggelaten

### T-14. Lokale factoren kwantificeren of de claim terugbrengen
- herkomst: **Reviewer #4** (R4-05)
- wie: Floris kiest de omvang
- status: wacht op Floris
- twee heel verschillende hoeveelheden werk: factoren in de analyse opnemen, of
  in de tekst terugbrengen tot wat de data dragen
- materiaal dat er al ligt: de SRI-scan over 48 locaties en het reguleringspatroon
  op Dnieper en Tagus, zie T-19

### T-15. Afronding van de p-waardes in Tabel 3
- herkomst: **Reviewer #4** (R4-06)
- status: open
- drie conventies botsen: de reviewer vraagt drie significante cijfers, de
  manuscript-afspraak zegt `p < 0.05` of twee decimalen, de huidige tabel doet
  drie decimalen via `safe_format`
- eerst één conventie kiezen die door het hele artikel geldt, dan in het script
  dat de tabel maakt zetten, niet met de hand in de tekst

### T-16. Appendix D, figuurtitels en kopjes
- herkomst: **Reviewer #1** (R1-09)
- status: open
- lettergrootte omhoog, kopjes per rivier en riviersegment, in de
  figuurgeneratie. Vraagt T-46, want de figuurcompositie is nog niet overgezet

### T-17. Nieuwe tabel met de fysische resultaten per rivier
- herkomst: **Reviewer #1** (R1-08, tweede deel)
- status: geblokkeerd door T-10, want de inhoud volgt uit de definitieve run
- moet uit `results/` gegenereerd worden, niet met de hand

### T-18. Maximale afstand op de gridpunt-lookup
- herkomst: eigen bevinding, restant van D-09 · **niet door een reviewer gevraagd**
- status: open
- `find_nearest_grid_point` heeft geen bovengrens. Bij een grid van 1/12 graad
  hoort een treffer binnen ongeveer 0,05 graad te vallen, en een grotere afwijking
  hoort hard te falen. Op zichzelf verandert dit geen resultaten in de
  gepubliceerde dataset, het voorkomt een stille fout

### T-19. Dnieper en Tagus, regulering of modelartefact
- herkomst: eigen bevinding D-12 · levert materiaal voor **Reviewer #4** (R4-02, R4-05)
- status: open
- vier locaties halen 2,9 tot 6,6 procent droogteweken tegen 15,9 verwacht, alle
  drie de Dnieper-punten plus Vila Velha de Rodao. Beide rivieren hebben een
  zware stuwmeercascade
- nog vast te stellen: of dit regulering in de werkelijkheid is of de manier
  waarop EFAS/LISFLOOD die modelleert. Dat onderscheid bepaalt hoe je het
  opschrijft
- de Tagus springt er ook in D-13 uit, plus 60 tot 120 procent op alle drie de
  locaties. Die twee bevindingen horen samen bekeken te worden

---

## C. Tekst

Alles in dit blok is geblokkeerd door T-31 zolang niet vast is welk bestand het
actuele manuscript is.

### T-20. Abstract concreet maken
- herkomst: **Reviewer #1** (R1-01) · associate editor (AE-02)
- status: open
- benoemen hoe mean severity en drought peak verschillen in hun effect op de
  floodkans, met richting en grootte in plaats van "in different ways"
- wordt een kwantitatieve claim, dus een regel in `claims.yaml`, zie T-41

### T-21. Sectie "Spatial dimension of drought-to-flood events" inkorten
- herkomst: **Reviewer #1** (R1-02), regel 115, pagina 9
- status: open
- let op de wisselwerking met T-27: wat hier wegvalt moet bruikbaar blijven voor
  de discussie

### T-22. Overgang naar de eigen studie scheiden van de literatuurkop
- herkomst: **Reviewer #1** (R1-03), regel 156, pagina 11
- status: open

### T-23. Definities uit de introductie naar sectie 2.3
- herkomst: **Reviewer #1** (R1-04), regels 186 tot 201, pagina 12 en 13
- status: open
- nagaan of de introductie zonder die definities leesbaar blijft en of 2.3 niet
  gaat dubbelen

### T-24. Keuze van de variabelenparen onderbouwen
- herkomst: **Reviewer #1** (R1-05), regels 314 en 315, pagina 20
- status: open
- de parenselectie ligt in de code vast, dus de onderbouwing moet daarmee kloppen

### T-25. Tabel 3 introduceren aan het begin van 3.1
- herkomst: **Reviewer #1** (R1-06)
- status: open

### T-26. Figuuruitleg in 3.2 uitbreiden
- herkomst: **Reviewer #1** (R1-07)
- status: open
- twee vragen worden letterlijk gesteld en moeten letterlijk beantwoord: wat de
  lijn van de unconditional transition probability betekent, en waar het
  gearceerde vlak voor staat. Ook in de captions

### T-27. Discussie en conclusie uitbreiden en contextualiseren
- herkomst: **Reviewer #1** (R1-08, eerste en derde deel) · associate editor (AE-02)
- status: open
- eigen resultaten afzetten tegen de literatuur uit de introductie, en de balans
  tussen appendices en hoofdtekst herstellen
- overlapt met T-13 en T-14

### T-28. Fysische lijn door het hele artikel
- herkomst: associate editor (AE-02) · bundelt R1-01, R1-08 en R4-04
- status: open
- geen losse tekstingreep maar de rode draad die beide reviewers missen: veel
  statistiek, weinig hydrologie. Bewaken bij T-20, T-26, T-27 en T-13

### T-29. Methodensectie op pagina 17 corrigeren
- herkomst: eigen bevindingen D-01, D-11, D-13 · voorstellen P-01, P-02 · **niet door een reviewer gevraagd, wel een feitelijke correctie**
- status: open
- **niet optioneel.** T-01 tot T-03 zijn nu alle drie beslist, en de punten
  hieronder staan vast. Tien dingen:
  1. de 69e quantile en Z-score 0,5 op pagina 17 **kloppen nu wel**, na de
     beslissing bij T-01. Wel een onderbouwing toevoegen waarom juist die grens,
     want R4-01 noemt de keuze "somewhat arbitrary"
  2. het woord "mirroring" eruit. Bij 0,5 selecteert de flooddrempel ongeveer 44
     procent van de weken tegen ongeveer 35 procent aan de droogtekant, terwijl
     symmetrie 30,9 aan beide kanten zou geven
  3. de feitelijke selectiviteit van beide drempels rapporteren, in de tekst of
     een appendix. Gemeten over alle 48 locaties en beide periodes, bij threshold
     0,5: **44,6 procent** van de weken boven de flooddrempel (bereik 33,3 tot
     55,7) tegen **35,8 procent** onder de droogtedrempel (19,8 tot 41,7), waar
     symmetrie 30,9 aan beide kanten zou geven. Verhouding 1,25. Bron:
     `results/2026-09-01_threshold_selectivity/`
  4. expliciet vermelden dat de drempels per periode opnieuw worden bepaald, met
     hoeveel ze verschuiven. **Nu verplicht**, want T-03 is op route B beslist en
     dat is de voorwaarde die D-13 daaraan stelt. Cijfers: bij ijking per periode
     lijken de periodes bijna identiek, 35,9 tegen 35,6 procent droogteweken, maar
     bij een gemeenschappelijk ijkpunt is periode 2 aanzienlijk droger, 29,0 tegen
     40,4. Het verschil per locatie gaat van mediaan 1,8 procentpunt naar 13,4, en
     van 0 naar 20 van de 48 locaties boven 15 punten. Rostov van 3,7 naar 64,5.
     Bron: `results/2026-09-01_reference_grid/`
  5. **"quantiles relative to the entire dataset for each location" corrigeren.**
     Die zin beschrijft de code niet. De referentie is de dagelijkse reeks van de
     periode, 5479 dagen, niet de volledige 10958. Nieuw op 1 september 2026, bij
     de beslissing over T-02. In D-11 stond dat de tekst hier al mee overeenkwam,
     en dat was onjuist
  6. **de droogtezijde is bij 0,5 zelf verkeerd geijkt**, 35,8 procent waar 30,85
     hoort. De SRI-mediaan ligt op -0,06 tot -0,16, dus de verdeling zit links van
     nul. Bij -1 is het effect weg, dus het is de band tussen -0,5 en -1 die te vol
     zit en niet de staart. Bij threshold 1 vielen de twee fouten tegen elkaar weg.
     **Oorzaak niet vastgesteld**, en er mag dus geen verklaring in de tekst zonder
     dat het eerst is nagerekend. Zie D-11
  7. **weken en events niet door elkaar halen.** De floodweken gaan bij de
     spiegelvariant van 44,6 naar 30,9 procent, min 30, maar de floodevents maar
     van 82,4 naar 72,8, min 11. Een event is een aaneengesloten reeks weken, dus
     een strengere drempel maakt events vooral korter. Wie over selectiviteit
     schrijft moet die twee getallen onderscheiden
  8. het bijschrift van **Figuur 3** aanpassen, dat noemt nu "Runoff> 69th
     quantile" en "SRI values (< -0.5)"
  9. de **discussie** aanpassen, daar staat "the selected thresholds
     (SRI < -0.5; runoff > 69th quantile)"
  10. vermelden dat de ECA in de R1-versie op 1 draaide en nu op 0,5, zodat beide
     onderdelen gelijk staan. Hoort bij het antwoord op R4-01
- de bron voor de SPI-classificatie moet uit de referentielijst van het
  manuscript komen, nog vast te stellen
- prioriteit: hoog, dit is een correctie en geen keuze

### T-30. De zes cellen op 1,0000 voor de Dnieper toelichten
- herkomst: eigen bevinding D-12 · voorwaarde 4 bij P-01 · **niet door een reviewer gevraagd**
- status: open
- die betekenen "te weinig droogte-events om te toetsen", niet "geen samenhang".
  Zoals het er nu staat leest een lezer het verkeerd

---

## D. Formele eisen voor de hersubmissie

### T-58. Gevoeligheidsanalyse in de tekst verwerken
- herkomst: volgt uit T-10 · antwoord op **Reviewer #4** (R4-01) en de weging van de
  associate editor (AE-01)
- status: **concepttekst ligt klaar**, Engels, in
  `results/2026-09-01_sensitivity_grid/draft_text_en.md`. Drie stukken: methoden,
  resultaten en beperkingen. Nog niet in het manuscript geplaatst
- geblokkeerd door T-31 zoals heel blok C, want sectienummers en het figuurnummer
  kunnen pas als vaststaat welke `.docx` geldt
- **wat er moet gebeuren:**
  1. de drie stukken in de juiste secties plaatsen en de nummers invullen
  2. de figuren opnemen. `figures/sensitivity_heatmap.png` is het vlak bij venster
     4 met p-waardes, `figures/sensitivity_by_window.png` is de volle kruising in
     tien panelen. Captions voor allebei in `figures/caption_en.md`, volledig en
     compact. **Nog te kiezen welke in de hoofdtekst komt en welke in de appendix**
  3. de beperking over ruimtelijke afhankelijkheid landt in de
     beperkingensectie, niet in het bijschrift. **Die mag niet wegvallen**, de
     gepoolde p-waardes zijn ondergrenzen
  4. de aggregatiemethode moet in de methodensectie met de verwijzing naar
     **Donges et al. 2016, sectie 2.2, vergelijking 6**. Nakijken of die referentie
     al in de literatuurlijst staat
  5. afstemmen met T-29, want die corrigeert dezelfde methodensectie
- **let op de omslag bij hoge floodquantielen.** Die staat nu als waarneming en
  niet als verklaring. Uitputting van het stroomgebied is plausibel maar niet
  gemeten. Sluit aan op T-13 en R4-04, en die twee moeten hetzelfde zeggen
- afhankelijk van T-15: het aantal decimalen in de p-waardes staat nu op drie
  significante cijfers zoals R4-06 vraagt, en dat botst met de manuscript-afspraak
- prioriteit: hoog, dit is het antwoord op het zwaarste reviewerpunt

### T-31. Vaststellen welke .docx het actuele manuscript is
- herkomst: formele eis editor (ED-05) · eigen bevinding D-07
- wie: alleen Floris weet dit
- status: wacht op Floris
- kandidaten in Downloads: `2. DTF_Europe_research_paper_manuscript.docx` van 16
  maart en `DTF_Europe_reasearch_paper_manuscript_22_03_26.pdf.pdf.docx` van 22
  maart, plus losse `References.docx` en
  `Tables - Europe - DTF - Research Paper.docx`
- blokkeert: heel blok C. **Dit is het goedkoopste blokkerende punt op de lijst**
- prioriteit: hoogste

### T-32. Regelnummers in het manuscript
- herkomst: formele eis editor (ED-01)
- status: open
- de PDF heeft ze, de Word-bron moet ze straks ook hebben

### T-33. Revision Notes schrijven
- herkomst: formele eis editor (ED-02)
- status: geblokkeerd, volgt uit de rest
- per punt hoe en waar het is verwerkt, met regelnummers. Wordt geschreven uit
  `review/round-2.md`, niet omgekeerd

### T-34. Gemarkeerde versie van het manuscript
- herkomst: formele eis editor (ED-03)
- status: geblokkeerd door blok C
- uploadvolgorde is voorgeschreven: Revision Notes, Revision changes marked,
  Manuscript

### T-35. Eigen standpunt per reviewerpunt invullen
- herkomst: formele eis editor (ED-04)
- wie: Floris
- status: open, geen enkel punt is ingevuld
- alle zeventien punten in `review/round-2.md` hebben een lege regel "eigen
  standpunt". Elke afwijkende mening heeft een onderbouwing nodig die in de
  Revision Notes kan staan
- prioriteit: hoog, en dit is voorwerk voor bijna elke andere taak

### T-36. Figuren en tabellen als losse bestanden aanleveren
- herkomst: formele eis editor (ED-06)
- status: open

### T-52. Uitstel vragen aan de editor
- herkomst: formele eis editor (ED-07)
- wie: Floris verstuurt, na afstemming met de co-auteurs
- status: concept klaar, niet verstuurd
- concept staat in `review/extension-request-draft.md`, met 12 november 2026 als
  voorgestelde datum, ongeveer acht weken uitstel. Geen toezeggingen over welke
  punten wel of niet worden overgenomen, dat blijft voor de Revision Notes
- nog te controleren voor verzending: of het tijdschrift uitstelverzoeken via
  Editorial Manager of via de editorial office wil hebben, en of de co-auteurs
  achter die termijn staan
- prioriteit: hoogste. Zolang hier geen antwoord op is blijft 17 september de
  geldende datum, en dan verandert de omvang van T-10 tot T-12
- doe T-48 hiervoor of hiernaast, want bijlagen bij de reviews kunnen de gevraagde
  termijn beïnvloeden

### T-37. Planning tegen de deadline
- herkomst: formele eis editor (ED-07)
- status: open
- 17 september, en na de deadline kan de editor het als een nieuw artikel
  behandelen. T-10, T-11 en T-12 zijn samen ruim meer werk dan 16 dagen. Er moet
  een keuze komen over wat volledig wordt gedaan en wat als beperking in de tekst
  komt. Dat is een gesprek met de co-auteurs, niet iets om per taak op te lossen
- prioriteit: hoogste, dit bepaalt de omvang van al het andere
- wordt anders als T-52 uitstel oplevert. Tot die tijd geldt 17 september

---

## E. Repo en werkafspraken

Bestanden die de werkafspraken eisen en die nog niet bestaan. Los van de
reviewers, maar ze maken het reviewerwerk wel controleerbaar.

### T-40. `CHANGELOG-methodology.md` aanmaken
- herkomst: werkafspraak uit beide skills · ondersteunt **Reviewer #4** (R4-01, R4-02, R4-03)
- status: open
- bestaat nog niet, terwijl elke wijziging die de uitkomsten raakt daar een regel
  hoort te krijgen. Zonder dit bestand is straks niet na te vertellen wat er
  tussen R1 en R2 is veranderd, en dat is precies wat de Revision Notes vragen
- prioriteit: hoog, en het is een half uur werk

### T-41. `manuscript/claims.yaml` aanmaken en vullen
- herkomst: werkafspraak uit dtf-manuscript
- status: open
- elke kwantitatieve bewering in het artikel krijgt een regel met script,
  resultaatbestand en verificatiedatum. Wordt onmisbaar zodra T-10 de cijfers
  verandert

### T-42. `config/analysis.yaml` en `config/locations.yaml`
- herkomst: werkafspraak uit dtf-code
- status: open
- `config/` bestaat niet. De parameters zitten nu in de code en in scriptargumenten

### T-43. `data/manifest.yaml` en checksumcontrole in de loader
- herkomst: werkafspraak uit dtf-code
- status: open
- naam, grootte, SHA256 en herkomst per databestand, met een harde fout bij
  afwijking. Relevant omdat er twee .nc-bestanden in omloop zijn geweest en die
  verwarring de reproduceerbaarheidscheck heeft gekost

### T-44. Omgeving pinnen
- herkomst: werkafspraak uit dtf-code · nodig voor T-11 (R4-03)
- status: open
- `pyproject.toml` en `uv.lock` ontbreken. `vinecopulas` is niche, die versie moet
  vast, anders is dit over een jaar niet meer te draaien. Nodig voor T-11

### T-45. `manifest.yaml` toevoegen aan de bestaande resultaatmappen
- herkomst: werkafspraak uit dtf-code
- status: open
- alle vijf mappen in `results/` missen hem. Achteraf reconstrueren kan nu nog,
  over een maand niet meer
- `results/2026-08-23_sri_diagnostic/` mist ook een README

### T-46. Copula-kant en figuurcompositie overzetten naar `src/dtf/`
- herkomst: intern, uit `docs/function-provenance.md` · blokkeert T-11 (R4-03) en T-16 (R1-09)
- status: open
- `fit_copula`, `copula_func_drought_peak`, `copula_func_mean_drought_severity`
  en de figuren zitten nog in de notebook. De ECA-kant is compleet
- blokkeert T-11 en T-16
- ~~let op: `fit_copula` uit cel 62 als canonieke versie wacht nog op bevestiging
  van Floris~~ **vervallen 1 september 2026.** Cel 62 hoorde bij de afgedankte
  `LAATSTE_VERSIE`-notebook van 104 cellen. In de gepubliceerde notebook, 64
  cellen, staat `fit_copula` één keer in cel 25, net als beide `copula_func_*`.
  Er valt niets te bevestigen, deze taak is niet geblokkeerd
- wel nog te dedupliceren: `create_page` en `process_img` staan twee keer, cel 27
  en 31. `docs/function-provenance.md` wijst cel 31 aan

### T-47. `review/round-1.md` ontbreekt
- herkomst: administratief, gesignaleerd in `review/round-2.md`
- status: open
- zonder ronde 1 is niet te zien welke punten van deze ronde herhalingen zijn, en
  dat is wel iets wat een reviewer meeweegt

### T-48. Nagaan of er bijlagen bij de reviews zitten
- herkomst: uit de beslissingsbrief · **kan de hele lijst veranderen**
- status: open
- de brief waarschuwt dat reviewers materiaal als attachment kunnen hebben
  aangeleverd dat niet in de brief zit. Te controleren op Editorial Manager
- prioriteit: hoog, want als er bijlagen zijn verandert de lijst hierboven

### T-49. Repo op privé zetten
- herkomst: eigen bevinding D-05 · **niet door een reviewer gevraagd**
- wie: Floris
- status: open
- `florislugtmeijer/Drougt_to_flood` staat publiek terwijl het manuscript in
  review is. Advies: privé tot acceptatie, want publiek maken kan later met één
  klik en de andere richting niet

### T-50. Repo-naam corrigeren
- herkomst: eigen bevinding D-06 · **niet door een reviewer gevraagd**
- status: open, cosmetisch
- `Drougt_to_flood` mist de h. Kan straks in een data-availability statement staan

### T-51. Niet-gecommit werk vastleggen
- herkomst: administratief
- status: open
- `scripts/04_flood_magnitude_test.py` en `scripts/05_season_control.py` staan
  untracked, en de wijzigingen in `open-decisions.md` en `proposed-changes.md`
  zijn niet gecommit. De resultaten waar in de documentatie naar wordt verwezen
  zijn dus deels niet herleidbaar tot code in de historie

### T-56. Feitelijke correcties in de methodensectie, periodes en Monte Carlo
- herkomst: gevolg van T-04 en T-05 · **niet door een reviewer gevraagd**
- status: open, klein werk
- **de periodes.** De tekst zegt nu "split the time series into two parts with the
  same duration" en "two parts of equal length", en "Period 2 lasts from January
  2010". Geen van drieën klopt precies: periode 1 is 5479 dagen, periode 2 is 5478,
  en periode 2 begint op 2 januari 2010. Voorgestelde tekst:

  > We calculate weekly averages of the daily river run-off values and split the
  > time series into two parts of near-equal length. Splitting the record this way
  > makes it possible to observe changes in the dependency structure between
  > drought and flood characteristics over time. Period 1 covers 1 January 1995 to
  > 31 December 2009 (5479 days); Period 2 covers 2 January 2010 to 31 December
  > 2024 (5478 days). The one-day difference between the two periods does not
  > affect the results.

  Die laatste zin kan erbij omdat het is nagerekend, zie T-04
- **de Monte Carlo.** Besloten 1 september 2026: aantal simulaties toevoegen aan
  de tekst. Voorgestelde plek is sectie 2.4.1 op pagina 20, direct achter:

  > "We calculate the test statistics and p-values based on the assumption of a
  > Poisson process as well as using a Monte Carlo simulation. More details can be
  > found in Appendix A."

  Voorgestelde toevoeging:

  > The Monte Carlo test uses 10,000 randomisations per location and period, with
  > a fixed random seed so that the results are exactly reproducible.

  Of in Appendix A, als daar de methode wordt uitgeschreven
- **nog te controleren: bestaat Appendix A?** De tekst verwijst ernaar op pagina
  20, maar in `manuscript/HYDROL79380_R1.pdf` staat geen Appendix A. Appendix B en
  E worden wel genoemd, en R1-09 gaat over Appendix D, dus de appendices bestaan
  en zitten waarschijnlijk in een apart bestand. Nagaan of Appendix A er echt is,
  want een verwijzing naar een appendix die niet bestaat valt een reviewer op
- prioriteit: laag qua werk, maar het zijn onjuistheden die blijven staan als je
  ze niet meeneemt

### T-57. Startjaar 1994 corrigeren naar 1995
- herkomst: eigen bevinding · **niet door een reviewer gevraagd**
- status: **besloten 1 september 2026: aanpassen naar 1995.** De data begint
  bevestigd op 1 januari 1995, dus de tekst is fout, niet de dataset
- twee plekken, allebei dezelfde zin:

  | waar | wat er staat |
  |---|---|
  | abstract in het manuscript, pagina 6 | "The analysis is based on daily river runoff data from **1994** to 2024" |
  | abstract in Editorial Manager, pagina 1 van de submissie-PDF | zelfde zin |

  Beide worden `from 1995 to 2024`.
- **let op de tweede.** Die staat niet in het Word-bestand maar in het
  abstract-veld van Editorial Manager, dat apart is ingevuld bij de submissie. Als
  je alleen de Word-versie aanpast blijft de oude tekst in het systeem staan en
  komt hij zo weer in de proef terecht
- de bestandsnaam `8_maart_european_river_runoff_1994_2024.nc` zegt ook 1994. Puur
  een naam, de inhoud begint op 1995. Niet hernoemen zonder de paden in de
  scripts mee te nemen

### T-54. Tabel 3 en de tekst herrekenen op threshold 0,5
- herkomst: gevolg van de beslissing bij T-01 · raakt **Reviewer #1** (R1-01, R1-06) en de abstract
- status: open
- de cijfers bestaan al in `results/2026-08-23_threshold_comparison/`, filter op
  `threshold=0.5`. Wat nog moet: Tabel 3 opnieuw opmaken, Figuur 4 met de
  significante locaties opnieuw genereren, en elke passage die aantallen of
  p-waardes noemt nalopen
- raakt de kernbevinding: van 10 naar 45 van de 48 significant. De abstract en de
  conclusie beschrijven straks een andere uitkomst dan de R1-versie
- ook T-30 wordt anders: bij 0,5 heeft de Dnieper 28 droogtes in plaats van 5, dus
  de zes cellen op 1,0000 verdwijnen waarschijnlijk
- prioriteit: hoogste van blok B

### T-53. Copuladrempel gelijktrekken met de ECA of het verschil verantwoorden
- herkomst: eigen bevinding D-14 · **niet door een reviewer gevraagd, maar R4-01 gaat er wel over**
- wie: Floris
- status: **gedaan, 1 september 2026. Route C: beide op 0,5.** De copula stond al
  op 0,5 en verandert niet, de ECA gaat mee. Zie T-54 voor het werk dat daaruit
  volgt
- let op bij het opschrijven: het **eerste** onderdeel (ECA, secties 2.4.1 en 3.1)
  draaide op 1, het **tweede** (copula, secties 2.4.2 en 3.2) stond al op 0,5. Niet
  omdraaien in de Revision Notes

---

## F. Gedaan en vervallen

Blijft staan met de reden, want dit is waar de tijd tot nu toe in is gegaan en
een aantal punten kan bij een nieuwe blik anders lijken dan ze zijn.

| wat | uitkomst | datum |
|---|---|---|
| Reproduceerbaarheid van Tabel 3 | exact gereproduceerd met de gepubliceerde notebook plus `8_maart_..._1994_2024.nc`, Monte Carlo op vier decimalen gelijk | 23 aug 2026 |
| D-03 dagelijkse randomisatie | vervallen, de gepubliceerde versie randomiseert op het weekly raster | 23 aug 2026 |
| D-08 matching-anker | vervallen, beide zijden van de toets matchen vanaf `end_time` | 23 aug 2026 |
| D-09 Visegrád-coördinaat | vervallen, de gepubliceerde dataset heeft het punt goed. Restant leeft door als T-18 | 23 aug 2026 |
| D-10 Tabel 3 niet reproduceerbaar | vervallen, zie de eerste regel | 23 aug 2026 |
| P-03 matching vanaf einde droogte | vervallen, was al goed in de gepubliceerde code | 23 aug 2026 |
| Threshold 0,5 doorgerekend | 45 van 48 significant tegen 10, cijfers liggen klaar voor T-01 en T-10 | 23 aug 2026 |
| SRI-scan over 48 locaties | mediaan 16,0 procent tegen 15,9 verwacht, vier afwijkende locaties, materiaal voor T-19 | 23 aug 2026 |
| Variant quantielreferentie doorgerekend | 18 locaties verliezen significantie, periode 2 houdt er nul over. **Geldt alleen bij threshold 1**, en T-01 heeft de threshold op 0,5 gezet. Vervangen door het raster van 1 september, zie T-02 | 23 aug 2026 |
| Flood-magnitude test | samenhang zit in de kleinere floods, bij de grootste 20 procent exact nul, input voor T-13 | 23 aug 2026 |
| Seizoenscontrole | seizoensverklaring uitgesloten, verloop blijft staan, chi-kwadraat wordt sterker | 24 aug 2026 |
| Regelnummers uit het manuscript | in kaart in `manuscript/README.md`, R1-punten gelokaliseerd | 24 aug 2026 |
| Alternatief "eerst quantielen, dan weekmaxima" | wiskundig identiek aan de huidige berekening, niets te draaien | 24 aug 2026 |
| Referentieraster op 0,5, T-02 en T-03 | 384 runs, controlecel exact gelijk aan de gepubliceerde berekening. T-02: 89 tegen 90 significant, het cijfermatige bezwaar valt weg. T-03: de per-periode ijking verbergt een verschuiving van mediaan 13,4 procentpunt. Beslissingen liggen bij Floris | 1 sep 2026 |
| Droogtezijde bij 0,5 verkeerd geijkt | 35,8 procent waar 30,85 hoort, SRI-mediaan op -0,06 tot -0,16. Oorzaak niet vastgesteld. Nieuw in D-11, moet naar T-29 | 1 sep 2026 |
| Lege-array crash in `get_matching_pairs_eca` | precursor-richting viel om bij nul droogte-events, gedicht met een guard. Raakt geen enkele bestaande uitkomst | 1 sep 2026 |
| T-10 blijkt een codewijziging te vragen | SRI-drempel en floodpercentiel zitten vast aan één parameter, dus R4-01 is niet te beantwoorden zonder ze te ontkoppelen. Nieuw, staat bij T-10 | 1 sep 2026 |
| **T-10 gevoeligheidsanalyse gedraaid** | 12000 runs, 125 cellen, volledig gekruist. De SRI-drempel doet vrijwel niets bij elk venster, het floodpercentiel doet alles. 193 van 250 cel-periodes houden stand, de rest zit in de hoek met hoge floodpercentielen. Gepoolde toets volgens Donges 2016. Concepttekst en twee figuren liggen klaar, zie T-58 | 1 en 2 sep 2026 |
| Monte Carlo 29x versneld | telling gevectoriseerd, trekking onaangeroerd, bit-identiek bewezen over 24 aanroepen van 10000 simulaties. Run van 11,2 naar 4,5 seconde | 1 sep 2026 |
| Seed per locatie ingevoerd | nodig voor de gepoolde toets, want één vaste seed gaf identieke surrogaten. Effect op `p_mc_trigger`: mediaan 0,0000, maximum 0,0097, één van de 96 runs steekt de 0,05 over. D-04 blijft gesloten voor losse locaties | 1 sep 2026 |
| Afhankelijkhedenkaart van de twee modellen | 31 functies, 44 aanroepen en 20 gegevensstromen uit de bron gelezen met `ast`. Gedeelde kern is zeven functies, waarvan `transform_to_quantiles` en `Intensity_calc` door de twee modellen met verschillende argumenten worden aangeroepen. Script, figuur en caption in `results/2026-09-02_function_dependency_map/` | 2 sep 2026 |

---

## G. Voorstel voor de aanpak

**Dit is een voorstel, geen besluit.** Het staat hier zodat er iets ligt om op te
reageren. Wat er per punt gebeurt beslis jij, en bij de zwaardere punten hoort dat
met de co-auteurs. Waar hieronder "voorstel" staat is dat mijn inschatting op
basis van de brief en van wat er in `results/` ligt.

Uitgangspunt: **niet alles hoeft overgenomen te worden.** De brief zegt het zelf,
ED-04, "should you disagree with any part of the reviews, please explain why".
Een onderbouwde afwijzing is een legitieme uitkomst. Wat niet werkt is een punt
stil laten liggen of half doen zonder het te benoemen, want dan komt het in ronde
drie terug met minder goodwill.

### Drie manieren om een punt af te doen

Niet twee, drie. De middelste is waar het meeste werk in deze ronde thuishoort.

**Overnemen.** Doen wat er gevraagd wordt.

**Kleiner uitvoeren dan gevraagd, en dat zeggen.** Een reviewer vraagt een
resultaat, niet een specifieke uitvoering. Validatie tegen meetreeksen voor acht
locaties met de reden waarom het acht zijn, is een antwoord. Validatie voor alle
48 is niet haalbaar en dat is ook niet wat het punt hard maakt. Dit is de
categorie waar je tijd wint zonder een punt te weigeren.

**Afwijzen met onderbouwing.** Drie ingrediënten, anders houdt het geen stand:
erkennen wat de zorg is, uitleggen waarom de gevraagde ingreep hier niet de
juiste is, en aangeven waar in de tekst de beperking nu wel staat. Dat laatste is
het deel dat meestal wordt vergeten en het is het deel dat het verschil maakt.

### Wat de ruimte om af te wijzen beperkt

Twee dingen uit de brief.

De associate editor schrijft in AE-01 dat de punten van Reviewer #4 "fundamental
to the reliability and interpretation of the results" zijn en "substantial
additional investigation" vragen. Dat is een weging van de editor, niet van de
reviewer. Een frontale afwijzing van R4-01, R4-02 of R4-03 gaat daarmee tegen de
editor in, en dat is een zwakke positie in een tweede ronde.

R4-05 en R4-04 liggen anders. Daar vraagt de reviewer om iets erbij, lokale
factoren kwantificeren en ancillary data, en niet om iets repareren. Verkleinen
of terugbrengen tot wat de data dragen is daar goed verdedigbaar.

### Voorstel per punt

Inschatting van omvang in grove categorieën: **uren**, **dagen**, **week of
meer**. Dat is een schatting, geen planning.

| punt | voorstel | omvang | grond |
|---|---|---|---|
| R1-03, R1-04, R1-06 | overnemen | uren elk | verplaatsen en een inleidende alinea, er is geen argument om dit niet te doen |
| R1-07 | overnemen | uren | twee letterlijke vragen, letterlijk beantwoorden in tekst en captions |
| R1-09 | overnemen | uren, na T-46 | lettergrootte en kopjes, in de figuurgeneratie |
| R4-06 | overnemen, maar één conventie kiezen | uren | de reviewer vraagt drie significante cijfers, wij hebben een andere afspraak. Kies er één en houd hem overal aan, dat is ook een antwoord |
| R1-01 | overnemen | dagen | vraagt wel dat de kernbevinding vaststaat, dus na T-10 |
| R1-02 | overnemen, met aandacht voor R1-08 | dagen | inkorten kan, maar wat je weghaalt heb je bij R1-08 nodig om je resultaten tegen de literatuur af te zetten. Doe die twee in één beweging |
| R1-05 | overnemen | dagen | de parenkeuze ligt in de code vast, dus dit is opschrijven wat er al is, niet iets nieuws bedenken |
| R1-08 | overnemen | dagen | de nieuwe tabel per rivier volgt uit `results/`, de contextualisering is schrijfwerk |
| AE-02 | overnemen als rode draad | verweven | geen los punt, bewaken bij R1-01, R1-07, R1-08 en R4-04 |
| R4-01 | overnemen | week of meer | dit is het punt dat je niet kunt weigeren, en het meeste ligt al klaar. Alleen de venstergrootte is nog echt open |
| R4-03 | eerste helft overnemen, tweede helft verkleinen | week of meer | de tabel met de gekozen copula per locatie en paar is goedkoop en overtuigend. De betrouwbaarheidsintervallen vragen een bootstrap die er niet is. Overweeg die voor een deelverzameling locaties, met de reden erbij |
| R4-02 | verkleinen | week of meer | validatie voor een gemotiveerde deelverzameling in plaats van alle 48. Neem er expliciet gereguleerde locaties in mee, want dat is precies waar de reviewer op wijst. Wat niet gedekt is gaat als beperking in de tekst |
| R4-04 | gedeeltelijk overnemen, mechanisme niet hard maken | dagen | er ligt al een empirisch antwoord: bij de grootste floods is er geen samenhang, dus bij hoge quantielen is er niets om op te conditioneren. Bodemvocht toevoegen is een nieuwe analyse. Voorstel: het empirische deel geven, expliciet zeggen dat het associatie is, en de drie beperkingen uit de magnitude-README meenemen |
| R4-05 | terugbrengen in de tekst | dagen | de eerlijke lijn: wij noemen lokale factoren als mogelijke verklaring en kwantificeren ze niet, dus die claim moet zwakker. Wat je wel hebt, het reguleringspatroon op Dnieper en Tagus, is één gekwantificeerd voorbeeld en dat is meer dan de tekst nu doet |
| ED-01 t/m ED-07 | overnemen | uren tot dagen | vormeisen, geen discussie mogelijk |

### Wat er hoe dan ook moet, los van elk besluit

T-29, de methodensectie op pagina 17. De tekst beschrijft nu een andere drempel
dan de code gebruikt, en het woord "mirroring" is feitelijk onjuist. Dat is geen
reviewerpunt en geen keuze, en het is ook het soort ding dat een reviewer met twee
regels code weerlegt. Dit staat los van T-01 tot T-03: hoe die ook vallen, de
tekst moet kloppen met wat er gerekend is.

Twee gunstige kanten. De correctie wordt onderdeel van het antwoord op R4-01 in
plaats van een losse bekentenis: je rapporteert de gevoeligheidsanalyse, je legt
uit welke drempel je aanhoudt en waarom, en de SPI-classificatie met de grens op
-1,0 is daar een inhoudelijk argument tegen het woord "arbitrary". En je kunt
melden dat bij 0,5 het aantal significante locaties naar 45 van 48 gaat, wat laat
zien dat je de conservatieve drempel hebt gekozen en niet de gunstigste.

### Voorstel voor de volgorde

**Deze week, ongeacht wat er verder besloten wordt.** Dit is werk dat je niet
terugdraait en dat niets blokkeert:

1. T-52 versturen, T-48 nakijken. Bijlagen kunnen de omvang veranderen, en tot er
   antwoord is geldt 17 september
2. T-31, welke .docx canoniek is. Blokkeert al het tekstwerk en kost jou een
   kwartier
3. T-35, jouw standpunt per punt. Dat is de invoer voor deze hele tabel en voor
   de Revision Notes
4. T-40 en T-45, de methodologie-changelog en de manifests. Samen een ochtend, en
   zonder die twee is straks niet na te vertellen wat er tussen R1 en R2 is
   veranderd
5. T-49, repo op privé

**Daarna, zodra T-01 tot T-03 gevallen zijn:** één run-serie voor T-10, met de
gerepareerde punten er meteen in. Niet in losse runs, want dan is niet meer te
zeggen welk effect waar vandaan komt.

**Parallel:** T-12 opstarten, want dat is het enige punt dat van iets buiten het
project afhangt. Als de meetreeksen er niet tijdig zijn, weet je dat liever in
week één dan in week zes.

**Als laatste:** de tekst. Blok C wacht op de cijfers uit T-10 en op T-31, en
tekst herschrijven op cijfers die nog veranderen is werk dat je twee keer doet.

### Wat ik van jou nodig heb om dit concreet te maken

- T-01 tot T-03, de drie drempelbesluiten. Zonder die kan T-10 niet
- per punt of het overnemen, verkleinen of afwijzen wordt, T-35
- bij R4-02 en R4-03: hoeveel locaties je acceptabel vindt voor een gedeeltelijk
  antwoord
- bij R4-05: kwantificeren of de claim terugbrengen
- of de co-auteurs meelezen op de afwijzingen voordat ze in de Revision Notes
  staan
