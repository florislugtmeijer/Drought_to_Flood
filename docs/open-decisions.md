# Openstaande beslissingen

**Bijgewerkt 23 augustus 2026 na verificatie.** Verscheidene punten hieronder
kwamen uit de verkeerde notebook-versie en zijn vervallen. Zie
`docs/reproducibility-check.md`. Vervallen: D-03, D-08, D-09, D-10.
Nog echt open: D-01, D-02, D-04, D-05, D-06, D-07.

**Aangevuld 2 september 2026.** Uit de review van de copula-kant, T-11, komen
D-15 tot en met D-20. Vier bevindingen uit diezelfde review zijn al besloten en
staan in `CHANGELOG-methodology.md`: de ontbrekende stap F_Y, het floodvenster, de
duur in `mean_drought_severity` en de keuze voor parametrische marginalen.

**Aangevuld 4 september 2026.** D-21 uit de hertest van de ECA-nulhypothese, op
vraag van Floris. De implementatie is trouw, de nul laat floods vallen waar de
definities ze vrijwel uitsluiten. Rekenwerk in de scratchpad, nog niet in `results/`.

Beslissingen die de resultaten of de tekst van het artikel raken en die nog
genomen moeten worden. Niets hiervan wordt stilzwijgend opgelost. Bij elke
beslissing: wie beslist, en wat er verandert als het zo of zo valt.

Gesloten beslissingen verhuizen naar `CHANGELOG-methodology.md` met de
onderbouwing en het effect op de cijfers.

Aanpassingen die Floris zelf voorstelt staan niet hier maar in
`docs/proposed-changes.md`. Dit bestand gaat over wat uit de code en de data
komt, dat bestand over wat Floris wil veranderen. Waar ze elkaar raken staat een
verwijzing.

---

## D-01 Threshold: 0,5 of 1

**Status: GESLOTEN 1 september 2026. Threshold gaat naar 0,5 voor beide
onderdelen.** Zie `CHANGELOG-methodology.md` en taak T-01. Alleen de ECA
verandert, de copula stond al op 0,5. Een eerdere beslissing diezelfde dag om op
1 te blijven is herroepen. Onderstaande analyse blijft staan als onderbouwing.

**Uitkomst: het aantal significante locaties gaat van 10 naar 45 van de 48.**
Zie `results/2026-08-23_threshold_comparison/README.md`. Dit is geen
nuanceverschuiving maar een andere hoofdbevinding, en het raakt de abstract, de
conclusie en Tabel 3. Beslis dit niet los van R4-01.
**Prioriteit: hoog. Dit blokkeert R4-01 en raakt elk getal in het artikel.**

### Het manuscript zegt 0,5, de code draaide 1

Reviewer #4 citeert de methode van het manuscript letterlijk:

> "The authors define drought using SRI < -0.5 and flood using runoff above the
> 69th percentile, with a 4-week coincidence interval."

Dat is precies `threshold=0.5`, want in de code is de flooddrempel
`norm.cdf(threshold)`:

| | flood-drempel | percentiel | droogte-drempel |
|---|---|---|---|
| `threshold=0.5` | 0,6915 | 69,1 | SRI < -0,5 |
| `threshold=1` | 0,8413 | 84,1 | SRI < -1,0 |

Het manuscript beschrijft dus de 69e percentiel en SRI < -0,5, terwijl alle
aanroepen in de code `threshold=1` meegeven, wat de 84e percentiel en SRI < -1
oplevert. De gepubliceerde cijfers horen niet bij de beschreven methode.

Bevestigd in het manuscript zelf, pagina 17 van `manuscript/HYDROL79380_R1.pdf`:

> "In this study, a flood is defined when run-off exceeds the 69th quantile,
> mirroring the drought threshold (the 69th quantile corresponds to a Z-score of
> 0.5)."

Het manuscript noemt de Z-score van 0,5 dus letterlijk. Dat is geen parafrase van
de reviewer en geen leesfout van onze kant. **Sinds de beslissing van 1 september
klopt deze passage weer met de code.**

Het coincidence-venster van 4 weken klopt wel, dat is `period_after_event=4` in
zowel de parametercel als de aanroepen.

### Wat dit betekent voor het werk

Twee dingen vallen samen, en dat is gunstig.

Eén: de discrepantie moet hoe dan ook rechtgetrokken worden. Ofwel de resultaten
worden herberekend met 0,5, ofwel de methodensectie wordt aangepast naar 1. Het
tweede is onaantrekkelijk zolang R4-01 op tafel ligt, want dan verander je de
beschreven methode terwijl een reviewer juist vraagt of die keuze verdedigbaar is.

Twee: R4-01 vraagt om een gevoeligheidsanalyse over de SRI-drempel, het
floodpercentiel en de venstergrootte. Beide thresholds doorrekenen is daar geen
extra werk naast, dat is een deel van het antwoord. De discrepantie wordt daarmee
onderdeel van de oplossing in plaats van een los probleem.

### Wat het verschil doet

Met 0,5 liggen beide drempels minder extreem, dus komen er meer flood-events en
meer droogte-events uit `extract_events`. Meer events aan beide kanten betekent
meer kandidaat-paren, en daarmee andere match-aantallen en andere p-waardes.

Welke richting de p-waardes op gaan is niet vooraf te zeggen: de observed matches
stijgen, maar de nulverdeling in de Monte Carlo schuift mee.

### Wat er nodig is om te beslissen

De gevoeligheidsanalyse uit R4-01, met 0,5 en 1 er beide in. Per variant en per
locatie: aantal droogtes, aantal floods, aantal drought-to-flood events, en de
p-waarde. Dan beslis je op cijfers in plaats van op een aanname.

Let op bij het opschrijven: als 0,5 de bedoelde waarde was en de resultaten
veranderen, dan verandert ook wat er in de abstract en de conclusie staat. Dat
raakt R1-01, waar juist gevraagd wordt de kernbevinding concreter te maken.

---

## D-02 Off-by-one in de periodesplitsing

**Status: GESLOTEN 1 september 2026. Niet corrigeren.** Effect nagerekend op vier
locaties bij threshold 0,5: identieke event-aantallen en identieke p-waardes tot
vier decimalen. Wel drie feitelijke tekstcorrecties, zie taak T-56.

`data.isel(valid_time=slice(begin, end))` is exclusief aan het eind. Met
`first_begin=0, first_end=5479, second_begin=5480, second_end=10958`:

- periode 1: index 0 tot en met 5478, dus 5479 dagen
- periode 2: index 5480 tot en met 10957, dus 5478 dagen
- index 5479 zit in geen van beide periodes

Twee gevolgen: de periodes zijn ongelijk lang, en er valt één dag tussenuit.

Corrigeren betekent de resultaten herberekenen. Laten staan betekent dat het
verschil in de methodensectie verantwoord moet worden, of dat een reviewer het
vindt. Het effect is vermoedelijk klein bij 5479 dagen, maar "vermoedelijk klein"
is geen antwoord dat je aan een reviewer geeft zonder het te hebben nagerekend.

---

## D-03 Dagelijkse randomisatie bij weekly observaties

**VERVALLEN.** De gepubliceerde versie randomiseert op het weekly raster, gelijk aan de observaties. Dit was een artefact van de afgedankte `LAATSTE_VERSIE`-tak.

**Status: open. Beslissing vraagt inhoudelijk oordeel, mogelijk met een co-auteur.**

`monte_carlo_p_value` trekt gesimuleerde flood-tijden uit
`pd.date_range(time_min, time_max, freq="D")`, dus op een dagelijks raster. De
observaties zijn weekly geresampled. Observed en simulated matches komen daarmee
uit verschillend gerasterde reeksen.

Waarom dat kan schuren: een gerandomiseerde flood op een willekeurige dag heeft
een andere kans om binnen het venster van 4 weken na een droogtestart te vallen
dan een flood die op weekrasters ligt, zoals de echte events. Als dat de
nulverdeling systematisch verschuift, verschuiven de p-waardes mee.

Of het effect groot is, is niet vastgesteld. Te testen door de simulatie ook op
`freq="W"` te draaien en de p-waardes te vergelijken.

---

## D-04 Vaste seed over alle locaties

**Status: GESLOTEN 1 september 2026. Seed blijft 42.** Restant: het aantal
simulaties en de seed worden in de tekst vermeld, zie taak T-56.

`seed=42` staat vast voor alle 48 locaties. Elke locatie krijgt daarmee dezelfde
pseudo-random reeks. Niet fout, en het is goed voor reproduceerbaarheid, maar het
maakt de ruis over locaties niet onafhankelijk. Als er ergens in het artikel iets
wordt gezegd over het aantal locaties met een significant resultaat, is dat het
punt waar dit uit kan maken.

---

## D-05 Repo publiek of privé

**Status: open. Beslist door Floris.**

`florislugtmeijer/Drougt_to_flood` staat nu publiek terwijl het manuscript in
review is. Er is nog niets gecommit en niets gepusht. Advies: privé tot
acceptatie, want later publiek maken kan met één klik en de andere richting niet,
wat publiek stond kan gecached zijn.

---

## D-06 Repo-naam

**Status: open, cosmetisch.**

`Drougt_to_flood` mist de h in Drought. Hernoemen kan via Settings, GitHub laat
de oude URL doorverwijzen. Voor een repo die bij een publicatie hoort en straks
in een data-availability statement kan staan, is de spelling niet helemaal
onbelangrijk.

---

## D-07 Welke .docx is het actuele manuscript

**Status: open. Alleen Floris weet dit.**

Kandidaten in Downloads: `2. DTF_Europe_research_paper_manuscript.docx`
(16 maart, 27 MB) en `DTF_Europe_reasearch_paper_manuscript_22_03_26.pdf.pdf.docx`
(22 maart, 27 MB), plus losse `References.docx` en
`Tables - Europe - DTF - Research Paper.docx`.

---

## D-08 Matching-anker: de Monte Carlo p-waarde is niet valide

**VERVALLEN.** De gepubliceerde versie matcht aan beide zijden van de toets vanaf `end_time`. Dit was een artefact van de afgedankte `LAATSTE_VERSIE`-tak.

**Status: geen keuze, dit is een fout die gerepareerd moet worden.**
**Prioriteit: hoogste. Raakt alle Monte Carlo p-waardes in het artikel.**

Floris heeft op 23 augustus 2026 vastgesteld dat een drought-to-flood event
gematcht hoort te worden vanaf het **einde** van de droogte, niet vanaf de start.
Een eerdere bevestiging in dit repo zei het omgekeerde en is ingetrokken.

Het manuscript zegt hetzelfde, pagina 19, in de variabelentabel bij Maximum
Runoff Peak:

> "The highest runoff value observed within four weeks after a drought ends, used
> to evaluate the intensity of a flood that directly follows a drought."

Nog te controleren: vergelijking (1) op pagina 17 definieert de conditie formeel,
maar de notatie komt onleesbaar uit de tekstextractie. Die moet met het oog tegen
de code gelegd worden.

### Wat er in de code gebeurt

In `drought_flood_p_value_trigger_ECA` (cel 50) staan drie tellingen naast
elkaar. Ze gebruiken niet dezelfde regel.

| wat | matching-anker | wordt gebruikt voor |
|---|---|---|
| `drought_flood_count` via `get_matching_pairs_drought_trigger` | einde droogte, correct | **niets, wordt weggegooid** |
| `drought_flood_count_new`, handmatige lus | start droogte, fout | `observed_matches` van de Monte Carlo |
| de lus binnen `monte_carlo_p_value` | einde droogte, correct | de nulverdeling |

De kern van het probleem staat in de laatste twee regels. De **observed** statistiek
wordt geteld vanaf de start van de droogte, de **gesimuleerde** verdeling waar hij
tegen wordt afgezet vanaf het einde. Twee verschillende regels aan weerszijden
van dezelfde toets. De p-waarde vergelijkt daarmee twee grootheden die niet
dezelfde grootheid zijn, en is dus niet geldig, los van welk anker het juiste is.

### Waarom start-matching inhoudelijk fout is

Het venster is `[drought.start_time, drought.start_time + 4 weken]`. Dat venster
overlapt de droogte zelf. Bij een droogte die langer dan vier weken duurt ligt
het venster volledig binnen de droogteperiode. De telling pakt dan floods die
**tijdens** de droogte optreden en mist juist de floods die erna komen. Dat is het
tegenovergestelde van een drought-to-flood transitie.

### De reparatie is klein

De juiste functie staat al in het notebook. `get_matching_pairs_drought_trigger`
(cel 39) implementeert exact de bedoelde regel:
`flood.start_time > drought.end_time` en `<= drought.end_time + delta`.

Twee dingen mankeren eraan in cel 50:

1. Hij wordt aangeroepen als
   `get_matching_pairs_drought_trigger(flood_events, drought_events, period_after_event)`,
   terwijl de signature `(drought_events, flood_events, time_between_events)` is.
   De argumenten staan omgekeerd, dus de functie meet de omgekeerde richting.
2. De uitkomst wordt aan `drought_flood_count` toegekend en daarna nooit gebruikt.

Repareren betekent: argumenten in de juiste volgorde, en `drought_flood_count`
in plaats van `drought_flood_count_new` doorgeven als `observed_matches`. Dan
gebruiken observed en simulated dezelfde regel, en is die regel de bedoelde.

### Wat blijft staan

De **analytische** ECA p-waardes zijn niet aangetast. `eca_p_value` gebruikt
`get_matching_pairs_eca`, en die matcht bij `direction="trigger"` op
`flood_start_time > drought_end_time`, dus correct. Ook de precursor-richting
gebruikt `end_time`. `p_value_trigger`, `p_value_precursor`,
`match_count_trigger` en `match_count_precursor` zijn dus met de juiste regel
berekend.

Wat opnieuw moet: alles wat uit `p_value_monte_carlo_trigger` en
`observed_matches` volgt.

### Samenhang met D-01

D-01 en D-08 vragen beide een herberekening. Doe ze in één run-serie, niet in
twee. De gevoeligheidsanalyse van R4-01 moet toch al over meerdere
drempelwaardes, dus de gerepareerde matching hoort daar meteen in.

Voor de tekst betekent dit dat de Monte Carlo p-waardes in Tabel 3 gaan
veranderen, en daarmee mogelijk de kernbevinding waar R1-01 en AE-02 om vragen.

---

## D-09 De Visegrád-locatie is fout, en de lookup verbergt het

**VERVALLEN.** De gepubliceerde dataset heeft Visegrád op de juiste plek. Dit was een artefact van de afgedankte tak. Wel blijft staan: `find_nearest_grid_point` heeft geen maximale afstand, en dat hoort er wel in.

**Status: fout, moet gerepareerd worden. Raakt de locatielijst van het artikel.**

`definitive_file_6_04_25.nc` heeft het Visegrád-punt op 43,7917 / 19,2917. Dat is
Višegrad in Bosnië aan de Drina, niet Visegrád in Hongarije aan de Donau
(47,7675 / 18,9448 volgens de config en 47,79 / 18,91 volgens het manuscript).

Doordat de nearest-point lookup zonder maximale afstand werkt, valt Visegrád
vervolgens op Łączany (Vistula) op 2,32 graden. De resultaatrij voor de Donau
midstream is dus in werkelijkheid de Vistula, en die locatie komt twee keer voor.

Twee dingen te repareren:

1. Het Visegrád-punt opnieuw uit de bronnen halen op de juiste coördinaat.
2. Een maximale afstand op de lookup, met een harde fout erboven. Bij een grid van
   1/12 graad hoort een treffer binnen ongeveer 0,05 graad te vallen. Een
   afwijking van 2,3 graden had nooit stil mogen doorgaan.

Raakt R4-05, want dat punt gaat over ruimtelijke heterogeniteit tussen
riviersegmenten. Een segment dat op de verkeerde rivier ligt hoort daar niet in.

---

## D-10 Tabel 3 is niet reproduceerbaar met wat we hebben

**VERVALLEN.** Tabel 3 is exact gereproduceerd, zie `docs/reproducibility-check.md`.

**Status: open. Beslissing voor Floris, waarschijnlijk samen met de co-auteurs.**
**Prioriteit: hoogste. Dit bepaalt wat de revisie is.**

Uitgewerkt in `docs/reproducibility-check.md`. Samengevat: het notebook plus
`definitive_file_6_04_25.nc` kan Tabel 3 niet hebben gemaakt. Tabel 3 bevat twee
locatienamen die niet in de code staan, Visegrád en Łączany hebben daar
verschillende waardes waar onze combinatie ze identiek maakt, en geen enkel
resultatenbestand komt in de buurt van de gepubliceerde cijfers.

Drie routes, met heel verschillende omvang:

**A. De oorspronkelijke run terugvinden.** Zoeken naar de Colab-versie en de
dataset die Tabel 3 wel oplevert, vermoedelijk met de `merged_points_timeseries`
familie. Voordeel: je weet dan wat er gepubliceerd is. Risico: als die run met
verschoven labels is gemaakt, vind je een fout in plaats van een bevestiging.

**B. Opnieuw doorrekenen en Tabel 3 als achterhaald behandelen.** De pipeline
correct opbouwen, D-01, D-08 en D-09 meteen goed, en alle cijfers vervangen.
Sluit aan bij R4-01, dat toch een gevoeligheidsanalyse vraagt. Betekent wel dat
de resultaten in de revisie afwijken van R1, en dat moet in de Revision Notes
worden uitgelegd.

**C. Eerst B, en A alleen om het verschil te kunnen verklaren.** Nieuwe cijfers
als basis, de oude run erbij om te kunnen zeggen wat er is veranderd en waarom.

Route B of C is inhoudelijk het sterkst, want de fouten in D-01, D-08 en D-09
moeten toch worden gerepareerd. Maar dit is geen technische keuze. Alle cijfers in
een artikel vervangen tijdens een revisie is een beslissing voor de auteurs, en de
co-auteurs horen daarbij.

---

## D-11 De flooddrempel spiegelt de droogtedrempel niet

> **Terminologie, 5 september 2026.** "Spiegelen" wordt in deze stukken voor twee
> dingen gebruikt, en die moeten uit elkaar blijven:
> 1. **z-score-spiegeling**: het floodniveau is `norm.cdf(0.5) = 0,6915`, het
>    quantiel bij dezelfde z-score als de droogtedrempel SRI < -0,5. **Dit blijft**,
>    bevestigd door Floris op 4 en 5 september, en het geldt met name voor het
>    copula-deel, waar de curves op 0,6915 worden afgelezen.
> 2. **selectiviteitsspiegeling** (P-02): weekmaxima tegen hun eigen verdeling, zodat
>    beide drempels 30,9 procent van de weken selecteren. **Dit is losgelaten**,
>    route B, de berekening blijft zoals hij is.
> De tekst op pagina 17 mag dus "mirroring" in betekenis 1 houden, maar moet erbij
> zeggen dat betekenis 2 niet opgaat, met de cijfers. Zie T-29 punt 2.

**Status: GESLOTEN 1 september 2026, route B. De berekening blijft ongewijzigd.**
Beslist ná de rerun op threshold 0,5, zie `results/2026-09-01_reference_grid/` en
taak T-02. Gekozen op de inhoudelijke verdediging, niet op de cijfers.

Belangrijk voor wie dit teruglees: het cijfermatige argument tegen het spiegelen
gold alleen bij threshold 1, waar het 18 locaties hun significantie kostte. Bij
0,5 gaan de significante runs van 90 naar 89, drie verliezen en twee winnen, en
de mediane verschuiving in p is +0,0001. De symmetriekant pleit juist vóór
spiegelen: de floodzijde gaat van 13,80 procentpunten te hoog naar 0,02 en de
onbalans tussen de zijdes van 9,17 naar 5,37. De keuze rust dus volledig op het
argument hieronder, dat de 69,1e percentiel van de dagelijkse verdeling een
herkenbare hydrologische grootheid is en de spiegelvariant dat opgeeft.

Route B houdt in: de berekening blijft ongewijzigd,
de tekst wordt gecorrigeerd. Zie `CHANGELOG-methodology.md` en T-02.**
**Aanleiding: vraag van Floris, 23 augustus 2026.**
**Bijgewerkt 1 september 2026: alle metingen hieronder zijn bij `threshold=1`
gedaan, en T-01 heeft de threshold op 0,5 gezet. De cijfers bij 0,5 staan
onderaan, in het blok "Hoe dit ligt bij threshold 0,5".**

### Er is geen aparte quantielparameter

De vraag was of bij `threshold=1` het quantiel ook moet worden aangepast. Dat
hoeft niet, want de code doet dat al:

```python
threshold_floods = norm.cdf(threshold)   # 1 -> 0,8413
...
threshold = -1 * threshold               # droogte bij SRI < -1
```

Eén parameter bestuurt beide kanten. Bij `threshold=1` is de flooddrempel dus al
de 84,1e percentiel. In de code valt hier niets te wijzigen.

**Wel in de tekst.** Pagina 17 zegt "a flood is defined when run-off exceeds the
69th quantile, mirroring the drought threshold (the 69th quantile corresponds to
a Z-score of 0.5)". Bij `threshold=1` moet daar de 84e quantile en een Z-score
van 1 staan.

### Maar "mirroring" gaat niet op

Gemeten aandeel weken boven of onder de drempel, eerste periode:

**Let op: de cijfers hieronder zijn bij `threshold=1` gemeten, en sinds T-01
draait alles op 0,5.** Gemeten over alle 48 locaties en beide periodes:

| | flooddrempel | droogtedrempel | nominaal | onbalans |
|---|---|---|---|---|
| threshold 0,5, **de huidige keuze** | 44,6% | 35,8% | 30,9% | 1,25 |
| threshold 1, historisch | 26,2% | 15,1% | 15,9% | 1,74 |

Bron: `results/2026-09-01_threshold_selectivity/`. Bij beide drempels is de
floodkant selectiever dan de droogtekant, dus van spiegelen is in geen van beide
gevallen sprake. De onbalans is bij 0,5 wel kleiner.

De oorspronkelijke meting bij threshold 1, op drie locaties:

| locatie | boven flooddrempel | onder droogtedrempel |
|---|---|---|
| Aschach an der Donau | 28,2% | 14,8% |
| Donji Milanovac | 24,9% | 17,2% |
| Bremen | 24,7% | 16,1% |

### De oorzaak

`transform_to_quantiles(runoff_maximum_weekly, runoff_slice_time_location)`
drukt het **weekmaximum** uit als quantiel van de **ruwe dagelijkse** verdeling.
Een weekmaximum is per definitie hoger dan een gemiddelde dagwaarde, dus die
quantielen liggen systematisch te hoog. Gemeten mediaan bij Aschach: 0,653 in
plaats van 0,50.

De droogtekant heeft dit niet, want de SRI standaardiseert het weekgemiddelde
tegen de verdeling van datzelfde weekgemiddelde, per kalenderweek.

### De reparatie is één regel

Weekmaxima tegen hun eigen verdeling in plaats van tegen de dagelijkse:

| referentie | mediaan quantiel | weken boven 0,8413 |
|---|---|---|
| ruwe dagwaardes, huidig | 0,653 | 28,2% |
| weekmaxima zelf | 0,501 | **15,9%** |

15,9 procent is exact `norm.cdf(-1)`. Dan spiegelen de twee drempels wel, en
klopt de tekst op pagina 17 weer met de code.

### Twee verdedigbare keuzes, geen technische

**A. Referentie aanpassen naar de weekmaxima.** Dan spiegelen de drempels en
klopt de "mirroring"-claim. Nadeel: alle event-aantallen en p-waardes veranderen,
dus Tabel 3 opnieuw.

**B. Huidige berekening houden en de tekst aanpassen.** Dan moet de
"mirroring"-claim eruit en moet erbij dat de flooddrempel in de praktijk 44,6 procent van de weken selecteert bij threshold 0,5.

> **Correctie, 1 september 2026.** Hier stond eerst dat de methodensectie al
> "quantiles relative to the entire dataset for each location" zegt en dat de code
> precies dat doet. **Dat laatste is onjuist.** De referentie is
> `data.isel(valid_time=slice(begin, end))`, dus de dagelijkse reeks van de periode,
> 5479 dagen. Niet de volledige dataset van 10958. Route B leunde dus op een zin die
> iets anders beschrijft dan er draait, en die zin moet gecorrigeerd worden. Zie
> T-29 punt 5.

Route B verandert geen cijfers. Route A is methodologisch schoner. Beide vragen
een aanpassing in de tekst, want zoals het er nu staat is het niet juist.

Hoort bij R4-01, want dat punt gaat over de onderbouwing van precies deze
drempels.

### Hoe dit ligt bij threshold 0,5

Gemeten over alle 48 locaties en beide periodes, bron
`results/2026-09-01_threshold_selectivity/`:

| | boven flooddrempel | onder droogtedrempel | nominaal | ratio |
|---|---|---|---|---|
| threshold 1 | 26,2% (17,5 tot 36,0) | 15,1% (2,9 tot 18,4) | 15,87% | 1,74 |
| threshold 0,5 | 44,6% (33,3 tot 55,7) | 35,8% (19,8 tot 41,7) | 30,85% | 1,25 |

Twee dingen die bij 0,5 anders liggen dan hierboven beschreven:

1. **De asymmetrie is kleiner**, ratio 1,25 in plaats van 1,74. Het argument dat
   de flooddrempel de droogtedrempel niet spiegelt blijft staan, maar het is minder
   groot dan de threshold-1 cijfers suggereren.
2. **De droogtekant overschiet nu ook.** 35,8 procent waar `norm.cdf(-0.5)` 30,85
   voorschrijft, bijna vijf procentpunt te veel. Bij threshold 1 klopte die kant
   wel, 15,1 tegen 15,87. Dit is dus niet zuiver een floodprobleem meer.
   **Oorzaak niet vastgesteld.** Vermoeden, niet gemeten: de vorm van de gammafit
   per kalenderweek wijkt in het midden van de verdeling meer van normaal af dan
   in de staart. Wie hier in de tekst een uitspraak over doet moet het eerst
   narekenen.

### Doorgerekend op 0,5, en de weging verschuift

Bron: `results/2026-09-01_reference_grid/`, 384 runs, controlecel exact gelijk aan
de gepubliceerde berekening.

**Het cijfermatige argument tegen de reparatie bestaat bij 0,5 niet.** Significante
runs van de 96, Monte Carlo:

| | huidige berekening | reparatie |
|---|---|---|
| threshold 1 | 20 | 2 |
| threshold 0,5 | 90 | **89** |

Drie locaties verliezen hun significantie, twee winnen er een.

**En de reparatie doet wél wat hij belooft, alleen niet volledig.** Afwijking van
de nominale 30,85 procent, per locatie over 96 runs:

| | floodweken | droogteweken | onbalans tussen de zijdes |
|---|---|---|---|
| huidige berekening | 13,80 punten | 5,38 punten | 9,17 punten |
| reparatie | **0,02 punten** | 5,38 punten | **5,37 punten** |

De onbalans wordt bijna gehalveerd. Route A is dus beter geijkt dan route B, niet
alleen anders. Wat er overblijft is de droogtezijde, en dat is een los probleem.

### Waarom de droogtezijde bij 0,5 overschiet

Gemeten op drie locaties, periode 1:

| locatie | mediaan SRI | < -0,5 | > +0,5 | < -1 | > +1 |
|---|---|---|---|---|---|
| nominaal | 0,00 | 30,85 | 30,85 | 15,87 | 15,87 |
| Aschach | -0,15 | 33,80 | 27,42 | 14,80 | 15,31 |
| Krapowice | -0,16 | 36,73 | 28,06 | 16,33 | 17,22 |
| Maastricht | -0,06 | 33,80 | 30,87 | 17,09 | 15,31 |

De SRI ligt links van nul. Daarom vallen er te veel weken onder -0,5 en te weinig
boven +0,5. Bij -1 is het effect weg, en bij Aschach zelfs iets de andere kant op.
De onderste staart is dus niet dikker, alleen de band tussen -0,5 en -1 is voller.
Bij threshold 1 vielen de twee fouten tegen elkaar weg, en daarom leek die kant
daar goed geijkt. Dat was hij niet, hij kwam goed uit.

**Oorzaak niet vastgesteld.** Aanknopingspunt uit de meting: de gammafit gebeurt
per kalenderweek en heeft 14,8 waardes per fit, met de locatieparameter op nul
vast. Vermoeden, niet gemeten: een MLE-gammafit op zo weinig punten wordt door de
hoge waardes omhoog getrokken, waardoor de gefitte mediaan boven de
steekproefmediaan komt en de SRI systematisch negatief uitvalt. Te toetsen tegen
een empirische variant of een grotere fitsteekproef. Dat is nieuw werk.

Dit raakt ook T-01, want het betekent dat de drempel van 0,5 een slechter geijkte
droogtezijde heeft dan 1. Materiaal voor de gevoeligheidsanalyse van R4-01.

---

## D-12 De Dnieper detecteert bijna geen droogtes

**Status: open, inhoudelijk. Waarschijnlijk een punt voor de discussie.**

Krementsjoek heeft maar 2,9 procent weken met SRI < -1, waar 15,9 procent hoort.
Dat is geen rekenfout: de SRI heeft daar een spreiding van 0,999, geen NaN's en
geen clipping. De onderkant van de afvoerverdeling is samengedrukt, met een
weekminimum van 1473 tegen een mediaan van 1598. Bij Aschach is dat 588 tegen
1378.

Met zo weinig droogtes zijn er in de eerste periode maar 5 droogte-events en nul
drought-to-flood transities, en dat is waarom Tabel 3 voor alle drie de
Dnieper-locaties in beide periodes 1,0000 geeft.

**Te controleren hypothese.** Krementsjoek is Kremenchuk, waar een groot
stuwmeer in de Dnieper ligt. Kunstmatig opgehouden laagwater zou precies dit
patroon geven. Als dat de verklaring is, meet de analyse daar niet
droogte-tot-flood dynamiek maar reservoirbeheer.

Dit is direct het punt van Reviewer #4 in R4-02: de EFAS/LISFLOOD reanalyse kan
systematische afwijkingen hebben "especially in regions with strong human
regulation". Ook relevant voor R4-05 over lokale factoren.

### Scan over alle 48 locaties

Afgerond, zie `results/2026-08-23_sri_diagnostic/`. De mediaan over alle
locaties is 16,0 procent, tegen 15,9 verwacht. De SRI gedraagt zich dus vrijwel
overal precies zoals hij moet. Vier locaties niet:

| rivier | locatie | % weken SRI < -1 | min / mediaan afvoer |
|---|---|---|---|
| Dnieper | Krementsjoek | 2,9 | 0,92 |
| Dnieper | Cherson | 3,4 | 0,90 |
| Dnieper | Dnipro | 5,6 | 0,87 |
| Tagus | Vila Velha de Rodao | 6,6 | 0,76 |

Ter vergelijking de andere kant: Rhône bij Avignon haalt 18,4 procent met een
min/mediaan van 0,32, Rhine bij Nijmegen 17,9 procent met 0,33.

Het patroon is eenduidig. Bij de vier afwijkende locaties zakt het laagwater
nauwelijks onder de mediaan, 8 tot 24 procent, terwijl dat bij een vrij
afstromende rivier 60 tot 70 procent is. Alle drie de Dnieper-locaties zitten
erbij, plus één op de Tagus. Beide rivieren hebben een zware stuwmeercascade.

Dat is dus geen los geval maar een systematisch patroon dat samenhangt met
regulering, precies waar R4-02 op wijst. Het is bruikbaar materiaal voor het
antwoord op dat punt en op R4-05, en het verklaart waarom de Dnieper in Tabel 3
op alle zes de cellen 1,0000 staat.

Wat nog niet vastgesteld is: of dit regulering in de werkelijkheid is, of de
manier waarop EFAS/LISFLOOD die regulering modelleert. Dat onderscheid doet uit
voor hoe je het in de tekst opschrijft.

---

## D-13 De drempels worden per periode opnieuw bepaald

**Status: open. Beslissing voor Floris. Raakt de vergelijking tussen de periodes.**
**Doorgerekend op 1 september 2026**, zie `results/2026-09-01_reference_grid/`.
Bij ijking per periode lijken de twee periodes bijna identiek, 35,9 tegen 35,6
procent droogteweken. Bij een gemeenschappelijk ijkpunt blijkt periode 2 fors
droger, 29,0 tegen 40,4 procent. Mediaan verschil tussen de periodes per locatie:
1,8 procentpunt bij ijking per periode, 13,4 bij een gemeenschappelijk ijkpunt,
en bij 20 van de 48 locaties meer dan 15 punten. Rostov gaat van 3,7 naar 64,5
procent droogteweken. Route A kost drie locaties hun significantie, allemaal
gereguleerde rivieren in periode 1.
**Gevonden 24 augustus 2026, bij het natrekken van P-02.**

### Wat er gebeurt

Zowel de flooddrempel als de droogtedrempel wordt binnen elke periode apart
bepaald:

- `transform_to_quantiles(runoff_max_weekly, runoff_slice_time_location)` waarbij
  `runoff_slice_time_location` alleen de 5479 dagen van díe periode bevat
- `SRI_calculate` fit de gammaverdeling per kalenderweek, ook alleen binnen die
  periode

Beide periodes krijgen dus hun eigen ijkpunt. Een flood in periode 2 is
gedefinieerd ten opzichte van periode 2, niet ten opzichte van een gemeenschappelijke
standaard.

### Hoe groot is dat

De afvoer verschilt substantieel tussen de periodes. Verschuiving van de 84e
percentiel van periode 1 naar periode 2, over 48 locaties:

| | |
|---|---|
| mediane verschuiving | −8,6% |
| bereik | −33,8% tot +119,7% |
| lager in periode 2 | 34 van 48 |
| verschuiving groter dan 10% | 32 van 48 |
| mediane verschuiving van de mediane afvoer | −9,4% |

Grootste gevallen:

| rivier | locatie | 84e perc. p1 | p2 | |
|---|---|---|---|---|
| Tagus | La Bazagona | 34,2 | 75,2 | +119,7% |
| Tagus | Vila Velha de Rodao | 319,2 | 529,6 | +65,9% |
| Tagus | Toledo | 63,7 | 101,3 | +58,9% |
| Don | Rostov - Dov | 1403,4 | 928,8 | −33,8% |
| Don | Kochetovskaya | 1166,8 | 799,7 | −31,5% |
| Dnieper | Krementsjoek | 2316,3 | 1599,4 | −30,9% |

### Waarom dit uitmaakt

Op de Don is een flood in periode 2 een ruim 30 procent lagere afvoer dan een
flood in periode 1. Op de Tagus meer dan het dubbele de andere kant op. Die
verschuiving wordt door de per-periode normalisatie volledig weggenomen.

Het artikel vergelijkt de twee periodes met elkaar. Een uitspraak als "de
samenhang tussen droogte en flood is veranderd tussen 1995-2009 en 2010-2024"
vermengt daarmee twee dingen: een verandering in de samenhang, en een
verandering in het afvoerregime zelf. Bij 32 van de 48 locaties is die tweede
component groter dan tien procent.

### Twee routes

**A. Gemeenschappelijke referentie over de volledige 30 jaar.** Eén drempel per
locatie, geldig voor beide periodes. Dan meet het verschil tussen de periodes ook
werkelijk een verschil, en wordt een trend in de afvoer zichtbaar in de
event-aantallen in plaats van weggepoetst. Nadeel: alle cijfers veranderen.

**B. Per periode houden en het expliciet opschrijven.** Verdedigbaar als je
bedoelt "een flood zoals die in die periode voorkwam", dus relatief aan het
regime van dat moment. Dat is een legitieme keuze voor een studie naar samenhang
in plaats van naar trends. Voorwaarde: het moet in de methodensectie staan, met
de constatering dat de drempels tussen de periodes verschuiven en met hoeveel.
Zonder die toelichting leest de lezer de vergelijking anders dan hij bedoeld is.

Route B vraagt geen herberekening. Route A verandert alles maar maakt de
tweeperiodenvergelijking interpreteerbaar.

Hoort bij R4-01 en bij elke passage waarin de twee periodes tegen elkaar worden
afgezet.

### Doorgerekend, 1 september 2026

Bron: `results/2026-09-01_reference_grid/`. Aandeel weken per periode, gemiddeld
over 48 locaties, `quantile_reference="daily"`:

| ijking | periode | droogteweken | floodweken |
|---|---|---|---|
| per periode | 1 | 35,9% | 44,3% |
| per periode | 2 | 35,6% | 45,0% |
| volle 30 jaar | 1 | 29,0% | 48,3% |
| volle 30 jaar | 2 | 40,4% | 40,9% |

Bij ijking per periode lijken de twee periodes bijna identiek. Bij een
gemeenschappelijk ijkpunt blijkt periode 2 aanzienlijk droger.

Verschil tussen de periodes per locatie, in procentpunten droogteweken:

| ijking | mediaan | boven 15 punten | grootste |
|---|---|---|---|
| per periode | 1,8 | 0 van 48 | 13,3 bij Dnipro |
| volle 30 jaar | **13,4** | **20 van 48** | **60,8 bij Rostov** |

De Don is het duidelijkst: Rostov van 3,7 procent droogteweken in periode 1 naar
64,5 in periode 2, Kochetovskaya van 4,8 naar 62,1, Nikolaevskaya van 6,1 naar
60,8. Cherson op de Dnieper van 0,0 naar 39,4, dus daar zijn in periode 1 nul
droogtes bij een gemeenschappelijk ijkpunt.

**Dat is dit punt in cijfers.** De per-periode normalisatie haalt precies de
verandering weg die het artikel wil laten zien.

**Wat route A kost.** Drie locaties verliezen hun significantie bij
`quantile_reference="daily"`, zes bij de variant van P-02. Nul winnen er een. Het
zijn de gereguleerde rivieren in periode 1: Krementsjoek en de drie Don-locaties,
plus bij de variant Vernon, Pora Wesfalica en Bremen.

Of dat een verlies of een winst is, is een keuze en geen rekenkundig punt. Die
locaties tellen nu mee als bewijs terwijl hun droogtedefinitie meebeweegt met het
afvoerregime van de periode zelf.

### Nog na te kijken

De Tagus springt eruit met plus 60 tot 120 procent op alle drie de locaties. Dat
is een grote sprong voor vijftien jaar. Samen met de bevinding uit D-12, dat Vila
Velha de Rodao maar 6,6 procent droogteweken haalt, ziet de Tagus eruit als een
rivier waar de reanalyse of de regulering aandacht verdient voordat er conclusies
aan worden gehangen.

---

## D-14 De copula draait op een andere drempel dan de ECA

**Status: GESLOTEN 1 september 2026. Route C: beide op 0,5.** De copula stond al
op 0,5, de ECA gaat mee. Zie taak T-54 voor het werk dat daaruit volgt.
**Gevonden 1 september 2026, na de beslissing om de ECA op 1 te houden.**

### Wat er aan de hand is

De twee helften van het "twofold" raamwerk gebruiken een verschillende
droogtedefinitie.

| onderdeel | aanroep | droogte | levert |
|---|---|---|---|
| ECA | `threshold=1` | SRI < -1 | Tabel 3 |
| copula | positioneel `0.5` | SRI < -0,5 | transitiekansen, Appendix D |

De copula-aanroepen geven de argumenten positioneel mee:

```python
copula_func_drought_peak(data, lon, lat, begin, end, time_scale,
                         X, Y, flood_score, threshold, period_after_event, ...)
copula_func_drought_peak(data, nearest_lon, nearest_lat, first_begin, first_end,
                         '1W', X, Y, 0.9, 0.5, 4, ...)
```

Dus `flood_score=0.9` en `threshold=0.5`. Dat geldt voor alle zes de
copula-aanroepen, in cel 30, 31 en 35.

### Wat de drempel daar precies doet

In `copula_func_drought_peak` en `copula_func_mean_drought_severity` wordt
`threshold` alleen gebruikt voor `Intensity_calc`, en daarvan wordt vervolgens
uitsluitend `Drought_Intensity` gebruikt. `Flood_Intensity` wordt wel toegekend
maar nooit gelezen.

Gevolg: de drempel bepaalt in de copula **alleen welke droogtes meetellen**. De
floodkant is daar continu, want die loopt via `quantile_max_value`, het hoogste
floodquantiel in de vier weken na het droogte-einde, zonder drempel.

Met 0,5 telt de copula ongeveer 83 droogtes per locatie, met 1 zouden dat er
ongeveer 53 zijn.

### Het manuscript beschrijft 0,5, niet 1

Pagina 17 heeft één definitiesectie, en die geldt in de tekst voor het hele
artikel:

> "a flood is defined when run-off exceeds the 69th quantile, mirroring the
> drought threshold (the 69th quantile corresponds to a Z-score of 0.5)"

Ook het bijschrift van Figuur 3 en de discussie noemen SRI < -0,5 en de 69e
quantile. De tekst klopt dus met de copula en niet met de ECA.

### Drie routes

**A. Zo laten en het verschil expliciet verantwoorden.** Verdedigbaar, en er is
een inhoudelijk argument: de ECA toetst of samenvallen vaker gebeurt dan toeval
en heeft baat bij een conservatieve, conventionele droogtedefinitie. De copula
schat een afhankelijkheidsstructuur en heeft steekproefomvang nodig. Met 53 in
plaats van 83 droogtes wordt een bivariate fit dunner. Voorwaarde: het staat
expliciet in de methodensectie, met deze reden, en Figuur 3 en de discussie
worden gesplitst naar welk onderdeel ze beschrijven.

**B. Beide op 1.** Consistent en het makkelijkst uit te leggen. Betekent de
copula opnieuw draaien, dus nieuwe transitiekansen en een nieuwe Appendix D, met
ongeveer een derde minder droogte-events voor de fit. Effect nog niet nagerekend.

**C. Beide op 0,5.** Dan klopt de tekst zoals hij nu staat, maar dan gaat de ECA
naar 45 van de 48 significant en herroept dat de beslissing van 1 september.

Route A vraagt geen herberekening, alleen tekst. Route B vraagt een run en een
nieuwe appendix.

### Waarom dit een reviewervraag kan worden

R4-01 vraagt om onderbouwing van de drempels. Twee verschillende drempels binnen
één raamwerk, waarvan er één niet in de methodensectie staat, is precies het
soort ding waar dat punt over gaat. Route A is verdedigbaar maar alleen als het
er ook echt staat.

### Wat níet hoeft te veranderen

`X = [1, 2]` voor drought peak en `X = [0.5, 1]` voor mean severity zijn de
grenzen voor minor en severe drought binnen de copula, beschreven op pagina 22. Ze
staan los van de event-drempel en hoeven niet mee. Ze bevatten wel toevallig ook 0,5
en 1, dus in de tekst moeten ze duidelijk van de drempel onderscheiden worden.

**Correctie, 2 september 2026.** Hier stond dat `flood_score = 0.9` het vaste
floodquantiel in `fit_copula` is. Dat klopt niet. Het argument voedde alleen
`prob_flood_fixed`, en dat werd nergens gelezen. Het had dus geen enkel effect op de
uitkomsten. Bij het overzetten naar `src/dtf/copula.py` is het vervallen. Zie R-09
in de copula-review.

---

##  De copula-kolom kan pas na de herrun van T-11

- herkomst: eigen bevinding uit de copula-review, R-04
- status: **open**
- wie beslist: Floris, mogelijk met de co-auteurs

`transform_to_quantiles` krijgt in de ECA-kant de **dagelijkse** reeks als
referentie mee, cel 16 regel 152. In de copula-kant krijgt hij de **wekelijkse
gemiddelden**, cel 25 regel 67 en 97. `quantile_max_value` betekent daarmee niet
hetzelfde in Tabel 3 als in de appendix met de transitiekansen.

Dit is geen fout, het is een keuze die nergens is vastgelegd en die niet uit de
tekst valt af te leiden. Wat er moet gebeuren: of gelijktrekken en herrekenen, of
laten staan en in de methodensectie expliciet benoemen dat de twee onderdelen een
andere referentieverdeling gebruiken.

De copula-berekeningen van 2 september volgen de copula-kant, dus de wekelijkse
gemiddelden, omdat dat is wat gereproduceerd moest worden.

---

## D-16. Hoe de instabiele copulakeuze wordt gerapporteerd

- herkomst: eigen bevinding uit de copula-review, R-05, raakt R4-03
- status: **besloten 5 september 2026 door Floris: de volledige variant.** Tabel met
  de gekozen familie per cel, plus het AIC-verschil met de nummer twee, plus het
  maximale verschil tussen de transitiecurve van de winnaar en die van de nummer
  twee. Rekenwerk: enkele minuten, op de gerepareerde code (script 12 is pre-fix en
  moet mee). Landt in Appendix E. Schrijfwerk in batch B04
- wie beslist: Floris

Gemeten over alle 192 cellen: het mediane AIC-verschil met de nummer twee is 0,47,
en bij 175 van de 192 ligt het onder 2. De gangbare vuistregel is dat onder 2 geen
onderscheid gemaakt kan worden. De gekozen familie is in de meeste cellen dus een
van meerdere die ongeveer even goed passen.

Reviewer #4 vraagt alleen welke familie is gekozen. Dat antwoord alleen geven is
dunner dan het kan zijn. De opties: alleen de tabel met de gekozen familie, of die
tabel plus het AIC-verschil met de nummer twee, of daarbovenop nog het maximale
verschil tussen de curve van de winnaar en die van de nummer twee.

De laatste is het sterkste antwoord, want die laat zien of een instabiele keuze de
transitiekans eigenlijk wel raakt. Kost een run van enkele minuten.

---

## D-17. De vier passages die van teken omdraaien

- herkomst: volgt uit de reparatie van R-01
- status: **besloten 5 september 2026 door Floris: de vier passages worden
  herschreven.** Daarbij hoort een nieuwe analysevraag: zijn Po en Ebro na de
  reparatie nog de twee rivieren die de tekst als voorbeeld uitlicht, of horen dat
  nu andere te zijn. Zie taak T-61 in `docs/todo.md`. De formulering gaat wel naar
  de co-auteurs via het co-auteursdocument, want het raakt de kernbevinding van de
  copula-helft
- wie beslist: Floris met de co-auteurs

Vier passages vergelijken de conditionele curve met de unconditionele lijn en
draaien om: pagina 27 tweemaal, pagina 28 en pagina 30. Nu staat er dat
conditioneren op een droogte de floodkans verlaagt. Na de reparatie is hij licht
hoger.

Wat er moet gebeuren is duidelijk, hoe het geformuleerd wordt niet. De vraag is ook
of dit naar de co-auteurs gaat voordat de rest van de revisie wordt geschreven, want
het raakt de kernbevinding van de copula-helft. Zie
`results/2026-09-02_copula_definition_variants/manuscript_claim_check.md` voor de
citaten en de cijfers.

Let op dat de vergelijking van milde tegen zware droogte niet verandert. De
uitspraken daarover blijven staan.

---

## D-18. Wordt het onderscheid marginaal tegen copula opgeschreven

- herkomst: eigen bevinding, volgt uit de opsplitsing van 2 september
- status: **besloten 5 september 2026 door Floris: ja, beschrijven.** De alinea
  voor 2.4.2 ligt klaar in `results/2026-09-02_copula_bootstrap/report.md` sectie
  7, de cijfers per cel in `transition_ci.csv`. Batch B04
- wie beslist: Floris met de co-auteurs

Het gat tussen de conditionele en de unconditionele curve valt uiteen in een
marginaal deel, is het venster na een droogte natter dan een willekeurig venster, en
een copula deel, hangt de piek samen met de zwaarte van de droogte. Alleen het
tweede is waar een copula voor dient.

Gemeten over alle 192 cellen bij quantiel 0,6915: gat +0,057, marginaal +0,076,
copula -0,023. Bij Ebro en Po is het copula deel wel positief, bijvoorbeeld Ebro
Tudela periode 2 mean severity: +0,135 is +0,069 plus +0,066.

Opschrijven is eerlijk en voorkomt dat een reviewer in ronde drie vraagt wat de
copula toevoegt. Niet opschrijven laat een raamwerk centraal staan dat vooral iets
meet wat de ECA-kant al meet.

---

## D-19. Het criterium achter de tellingen op pagina 31

- herkomst: eigen bevinding uit de manuscripttoets
- status: **besloten 4 september 2026 door Floris: optie A, de
  onafhankelijkheidstoetsen. C afgewezen.** Zie `CHANGELOG-methodology.md`, entry
  2026-09-04, en taak T-60 voor het schrijfwerk
- wie beslist: Floris
- materiaal: `results/2026-09-04_increase_criterion/report.md`, gemaakt door
  `scripts/29_increase_criterion_counts.py`, leest alleen de bootstrap van 3
  september en de onafhankelijkheidstoetsen van 2 september, beide post-fix

Pagina 31 zegt dat toename van de transitiekans wordt gezien bij 5 locaties voor
Drought Peak en 6 voor Mean Severity in periode 1, en 7 en 9 in periode 2. Nergens
staat wanneer iets als toename telt.

Eerste narekening, pre-fix op de rangas: bij een drempel van +0,02 op het mediane
verschil tussen de zware en de milde curve komt er 7, 5, 6, 9 uit. Exact
reproduceren kan niet, de gepubliceerde berekening heeft geen seed.

### Acht criteria naast elkaar, post-fix

Alle op het verschil zwaar min mild, toename en afname allebei geteld. Volgorde
van de kolommen: periode 1 drought peak, periode 1 mean severity, periode 2 drought
peak, periode 2 mean severity. Van de 190 cellen in de bootstrap hebben 13 geen
zware curve, want geen enkele droogte boven de zware drempel. Die tellen niet mee.

| criterium | toenames | afnames |
|---|---|---|
| gepubliceerd | 5, 6, 7, 9 | niet gegeven |
| mediaan over y voorbij +0,02, hetzelfde criterium als de eerste narekening | 5, 4, 7, 8 | 19, 13, 11, 6 |
| punt bij quantiel 0,69 voorbij +0,02 | 13, 13, 11, 19 | 24, 18, 19, 10 |
| 95 procent bootstrapinterval sluit nul uit bij 0,69 | 0, 1, 0, 0 | 1, 1, 0, 0 |
| idem bij 0,69, 0,90 of 0,95 | 1, 1, 0, 0 | 1, 1, 0, 0 |
| minstens 3 van 4 onafhankelijkheidstoetsen p < 0,05, richting uit tau | 1, 2, 2, 4 | 2, 1, 0, 0 |

Twee dingen springen eruit. Het mediaancriterium bij +0,02 geeft post-fix bijna
precies de gepubliceerde tellingen, 5, 4, 7, 8 tegen 5, 6, 7, 9. Dat is dus
vermoedelijk het criterium dat destijds op het oog is toegepast. Maar van die 24
toenames houdt er onder het bootstrapinterval bij 0,69 geen enkele stand, en onder de
toetsen twee. Het zijn afstanden tussen twee gesimuleerde curves waarvan de zware op
mediaan één event rust.

En onder de puntcriteria zijn er in periode 1 en bij drought peak in periode 2 meer
afnames dan toenames, alleen mean severity in periode 2 heeft er meer toenames. De zin
"most locations exhibit either no difference or a decrease" klopt dus grotendeels, de
zin dat de toenames "point to important regional dynamics" rust op tellingen die
onder onzekerheid niet standhouden.

### De met naam genoemde locaties

- Dnieper Krementsjoek, periode 1, mean severity: verschil bij 0,69 is +0,000,
  interval [-0,158, +0,156], 2 van 4 toetsen. De tekst noemt hier een toename, ook
  boven de unconditionele lijn. Niet onderbouwd.
- Dnieper Dnipro, periode 2, mean severity: +0,060 [-0,021, +0,240], 0 van 4.
- Tagus La Bazagona: de tekst noemt periode 1, de toetsen vinden periode 2, 4 van 4
  voor beide variabelen. Voor mean severity periode 1 is er geen zware curve.
- Tagus Vila Velha de Rodao: in drie van de vier cellen geen zware curve. De
  beschreven omslag van afname naar toename is niet te toetsen.
- Vistula en Oder midstream, drought peak, "toename alleen bij hogere quantielen":
  bij Warchau en Scinawa in periode 2 zijn de puntverschillen bij 0,90 en 0,95
  positief, maar elk interval bevat nul. Vistula Turon periode 1 is het enige
  Vistula-punt dat nul uitsluit, en dat is een afname op alle drie niveaus.

### Drie opties, met conceptteksten in het rapport

**A. De onafhankelijkheidstoetsen.** Toename als minstens drie van de vier toetsen
p < 0,05 geven en tau positief is. Geeft 1, 2, 2, 4 toenames en 2, 1, 0, 0 afnames.
Dit is dezelfde definitie als sectie 1 van het bootstraprapport, dus consistent met
wat er al voor R4-03 ligt. De toename van periode 1 naar 2 blijft, van 3 naar 6. De
positieve cellen zijn Po Piacenza, Ebro Haro en Tudela, Tagus La Bazagona en Danube
Aschach, precies de rivieren waar het artikel op leunt. De negatieve zijn Vistula
Turon en Weser Bodenwerder.

**B. Het bootstrapinterval bij 0,69.** Toename als het 95 procent interval van het
verschil geheel boven nul ligt. Geeft 0, 1, 0, 0 en 1, 1, 0, 0. Het meest directe
criterium op de curves die de figuren tonen, maar zo conservatief dat de alinea
verdwijnt: één toename, Danube Aschach.

**C. Het mediaancriterium bij +0,02.** Reproduceert de gepubliceerde tellingen bijna,
5, 4, 7, 8, maar zonder onzekerheid. Een reviewer die R4-03 heeft gesteld zal dat
opmerken, en van de 24 toenames overleven er 0 tot 2 een onzekerheidscriterium.

**Voorstel: A**, met de intervallen uit B in Appendix E als onzekerheid bij de curves.
A meet de samenhang tussen droogtezwaarte en piek over alle events van een cel, en
dat is wat het verschil tussen de zware en de milde curve hoort uit te drukken. B en
C meten de afstand tussen twee curves waarvan één op bijna geen events rust.

Wat er bij A in de tekst moet veranderen: het criterium zelf, de tellingen, de
Dnieper-passage terugbrengen of schrappen, La Bazagona van periode 1 naar 2, de
Vistula en Oder passage terugbrengen tot puntschattingen met intervallen die nul
bevatten, en het negatieve cluster benoemen. Raakt D-17 en D-18.

Methodologie verandert niet, dit is een keuze voor een telcriterium dat in de tekst
ontbrak. Wel een regel in `CHANGELOG-methodology.md` zodra de keuze valt, want de
gepubliceerde tellingen veranderen.

### Besluit 4 september 2026: C afgewezen

Floris heeft C, het mediaancriterium bij +0,02, afgewezen en A, de
onafhankelijkheidstoetsen, gekozen. De onderbouwing van de afwijzing staat hier
volledig, zodat hij in de Revision Notes en de brief aan de reviewers te gebruiken
is. Hoe A is bepaald en welke rivieren erbinnen vallen staat in T-60.

Waarom C niet, in vijf punten:

1. **Geen onzekerheid.** C telt op puntschattingen. Reviewer #4 vraagt in R4-03
   expliciet om betrouwbaarheidsintervallen bij de transitiekansen. Een telling die
   die intervallen negeert, in hetzelfde artikel waar we ze toevoegen, is niet te
   verdedigen.
2. **De zware curve rust op bijna geen data.** Mediaan één droogte-event boven de
   zware drempel per cel. Het verschil met de milde curve is dan vooral de vorm van
   de gefitte copula, niet een waarneming. Een afstand van 0,02 tussen twee zulke
   curves is ruis.
3. **De tellingen houden geen stand.** Van de 24 cellen die C als toename aanwijst,
   overleeft er 0 het bootstrapinterval bij quantiel 0,69, 1 het interval op een van
   de drie niveaus, en 2 de onafhankelijkheidstoetsen. Zie de overlaptabel in
   `results/2026-09-04_increase_criterion/report.md`.
4. **De drempel is willekeurig.** De 0,02 volgt nergens uit. Bij 0,05 worden de
   tellingen 0, 1, 2, 2. Een criterium waarvan de uitkomst zo sterk van een
   ongefundeerde constante afhangt, hoort niet in de tekst.
5. **De gepubliceerde tellingen zijn niet reproduceerbaar.** De oorspronkelijke
   berekening had geen seed, en post-fix komt C op 5, 4, 7, 8 tegen 5, 6, 7, 9. C
   vasthouden omdat het dicht bij de oude getallen komt, is oude getallen verdedigen
   die we zelf niet meer kunnen maken.

Wat er tegenover staat: onder A gaan de toenames van 27 naar 9, onder B naar 1. Dat
is een forse terugname van de alinea op pagina 31. Zelf melden is een sterkere
positie dan het door een reviewer laten vinden, en A houdt precies de locaties over
waar het artikel al op leunt: Po, Ebro, Tagus, Danube.

Concept voor de Revision Notes, Engels:

> In the submitted version, the counts of locations with increased transition
> probability (5, 6, 7 and 9) were based on visual inspection of the conditional
> curves without a stated criterion. We were able to approximately reproduce them
> with a threshold of +0.02 on the median difference between the major and the minor
> curve, but this criterion ignores sampling uncertainty: the major curve typically
> rests on a single drought event above the severity threshold, and none of the
> locations counted this way show a difference whose 95% bootstrap interval excludes
> zero. We have therefore replaced the counts by a criterion based on the four
> dependence tests introduced in Section 2.4.2 [A], which reduces the number of
> locations with a detectable increase to 1, 2, 2 and 4, and identifies 3 locations
> with a detectable decrease. The paragraph on page 31 has been rewritten
> accordingly.

A is bevestigd, de haak [A] kan weg bij het overnemen.

---

## D-20. De curve die per constructie de diagonaal is

- herkomst: eigen bevinding uit de copula-review, R-10
- status: **besloten 5 september 2026 door Floris: beschrijven.** Eerst nagaan of
  de curve in het manuscript of Appendix D voorkomt, dan uitleggen als de definitie
  die hij is. Batch B04
- wie beslist: Floris

`conditional_probability_drought` is `1 - empirical_cdf(ur[:,1], flood_quantiles)`,
en `ur[:,1]` is per constructie uniform. Die curve is dus de rechte lijn 1 min y en
bevat geen informatie over de copula. Hij wordt niet geplot in figuur 2 maar zit wel
in het resultaat.

Nagaan of hij ergens in het manuscript of de appendices opduikt. Zo ja, eruit of
uitleggen als de definitie die hij is.

---

## D-21. De nulhypothese van de ECA laat floods vallen waar de definities ze niet toestaan

- herkomst: vraag van Floris op 4 september 2026, na de gerepareerde ECA, of de
  implementatie klopt gezien 92 van de 96 runs significant en 84 op p precies 0
- status: **open, rekenwerk klaar op 4 september 2026, nog niet in `results/`**
- wie beslist: Floris, met de co-auteurs, want dit raakt de hoofdbevinding
- materiaal: scratchpad-scripts `nulltest_all.py`, `restricted_null_all.py`,
  `stratified_null_all.py`, `overlap_map.py`, met hun CSV's. **Niet in de repo.** De
  scratchpad is op 4 september al een keer gewist, dus de cijfers staan hier volledig
  uitgeschreven. Overzetten naar `scripts/` en een `results/2026-09-04_eca_null_diagnosis/`
  zodra Floris dat vrijgeeft
- raakt: T-01, T-10, T-29, R4-01, R4-04, de abstract en de conclusie
- **rapport met figuren, 5 september 2026:** `results/2026-09-05_eca_null_routes_report/report.pdf`,
  gemaakt door `scripts/33_eca_null_routes_report.py`. Legt de routes naast elkaar
  voor de keuze, met een advies. De vier diagnose-CSV's staan daar in `data/`
- **derde rapport, 5 september 2026:** `results/2026-09-05_eca_null_dprime/report.pdf`, de
  resultaten van D', gemaakt door `scripts/32_eca_null_dprime_report.py`. De nul zelf:
  `scripts/31_run_permutation_null.py`
- **tweede rapport, 5 september 2026:** `results/2026-09-05_eca_simulations_report/report.pdf`,
  gemaakt door `scripts/34_eca_simulations_report.py`. Antwoord op de vraag of de toets
  hele events hussel of alleen starts: alleen starts, als punten. Met de echte weekreeks
  van Aschach als illustratie van de toets, de nul, de drie problemen en de nulmodellen

### De implementatie is trouw, de nulhypothese niet

De code reproduceert de notebook, de reparatie van de einddetectie is gedocumenteerd
en de Monte Carlo-vectorisatie is elementsgewijs gecontroleerd. Daar zit het niet.

`monte_carlo_p_value` houdt de droogtes vast, neemt het aantal floodstarts en strooit
die willekeurig over **alle weken**, 10.000 keer. De p-waarde is het aandeel
strooiingen met minstens zo veel matches als waargenomen. Dat toetst de hypothese
"floodstarts liggen willekeurig in de tijd, onafhankelijk van droogtes". Die
hypothese is bij deze definities al onwaar voordat er iets hydrologisch gebeurt,
omdat beide labels uit dezelfde afvoerreeks komen.

### Waarom: bij percentiel 0,69 is "flood" bijna "niet in droogte"

Een droogteweek heeft een laag weekgemiddelde en daarmee meestal ook een laag
weekmaximum. Bij threshold 0,5 ligt de flooddrempel bovendien laag: de 69e
percentiel van de dagwaardes, waar het mediane weekmaximum al op quantiel 0,65 zit.
Gemeten over alle 48 locaties en beide periodes, medianen:

| | threshold 0,5 | threshold 1 |
|---|---|---|
| aandeel droogteweken | 36% | 15% |
| aandeel floodweken | 46% | 27% |
| P(flood, gegeven droogteweek) | 0,05 | 0,00 |
| P(flood, gegeven niet-droogteweek) | **0,67** | 0,32 |

Twee van elke drie niet-droogteweken heten bij 0,5 flood.

**Let op, dit is geen verbod maar een kansverschil.** Een floodweek kan wel een
droogteweek zijn, want de SRI is seizoensrelatief en de flooddrempel absoluut. Over
96 runs bij 0,5: 1591 weken zijn tegelijk droogte en flood, 5,9 procent van de
droogteweken, en 764 van de 8032 floodstarts, 9,5 procent, beginnen op een
droogteweek. Bij threshold 1 is dat 0,3 procent. Zie de kaart onderaan.

### Wat dat met een droogte-einde doet

Een droogte eindigt zodra het gemiddelde weer boven -0,5 komt. De week erna is dus
per definitie een niet-droogteweek, en die is voor twee derde een floodweek. De week
ervóór, de laatste droogteweek, was vrijwel zeker geen floodweek. Een floodweek
direct na een droogte is daarmee **automatisch een floodstart**, want een start is
een floodweek met een niet-floodweek ervoor. Dat is de definitie, geen hydrologie.

Lagverdeling van alle 5503 matches bij 0,5 op de gerepareerde baseline:

| lag na het droogte-einde | gemeten | onder onafhankelijkheid |
|---|---|---|
| week 1 | **71%** | ongeveer 27% |
| week 2 | 13% | ongeveer 24% |
| week 3 | 9% | ongeveer 21% |
| week 4 | 7% | ongeveer 19% |

Bij threshold 1: 43, 28, 16, 13 procent.

De beslissende meting: is de week na een droogte-einde vaker flood dan een
willekeurige andere niet-droogteweek? **Nee.** Bij 0,5 is P(flood in de week na een
droogte-einde) 0,58 tegen P(flood, gegeven niet-droogte) 0,67, en in 85 van de 96
runs is hij lager. Bij threshold 1: 0,14 tegen 0,32, in 93 van de 94 runs lager. De
afvoer die net uit een droogte komt is een gewone niet-droogteweek, geen natte.

### Vijf nulmodellen naast elkaar

Alle over 48 locaties en beide periodes, 2000 simulaties per run, dezelfde telling
als de toets. Alleen de verzameling weken waar een gesimuleerde start mag vallen
verschilt.

| nul | floodstarts geplaatst op | gebruikt waargenomen floodposities |
|---|---|---|
| A, gepubliceerd | alle weken | nee |
| B | alleen niet-droogteweken | nee |
| C | alleen weken die een floodstart kunnen zijn: niet-droogte en week ervoor geen flood | ja, voor "week ervoor" |
| B', gestratificeerd | het waargenomen aantal starts op droogteweken uniform over de droogteweken, de rest over de niet-droogteweken | nee |
| C', gestratificeerd plus startregel | als B', plus week ervoor geen flood | ja, voor "week ervoor" |

B en C verbieden floods in droogteweken en zijn daarmee iets te streng, want die
komen bij 0,5 voor. B' en C' laten er precies zo veel toe als er werkelijk zijn en
randomiseren alleen de timing binnen elke laag. **C' is de eerlijkste nul die er nu
ligt.**

| nul | threshold 0,5 | | threshold 1 | |
|---|---|---|---|---|
| | significant van 96 | gepoolde ratio | significant van 96 | gepoolde ratio |
| A | 92 | 1,81 | 30 | 1,26 |
| B | 90 | 1,58 | 30 | 1,24 |
| C | 74 | 1,18 | 21 | 1,06 |
| B' | 90 | 1,63 | 29 | 1,24 |
| C' | 80 | 1,25 | 21 | 1,07 |
| **D'**, blokken met lengte, gestratificeerd | **22** | **1,05** | **11** | **1,00** |

**D' is op 5 september gebouwd en gedraaid**, zie
`results/2026-09-05_eca_null_dprime/`. Droogtes vast, floods als blokken met hun eigen
lengte, normale weken als vrije vulling, blokken raken elkaar niet, verplaatsbaar
over stukken heen, met een aparte laag voor floods die in een droogteweek beginnen.
Geen gebruik van de waargenomen posities, dus zonder het voorbehoud van C'. 1000
simulaties per run, alle zelfcontroles geslaagd, 928 herstarts op 192.000 plaatsingen.

**Onder D' blijft bij 0,5 een gepoolde ratio van 1,05 over met 22 van de 96
significant, bij threshold 1 een ratio van 1,00 met 11 van de 96.** D' ligt dus onder
C'. De circulariteit van C' maakte hem niet te streng maar te mild: als blokken een
lengte hebben en twee derde van de niet-droogteweken flood is, volgt na vrijwel elk
droogte-einde binnen vier weken een blokstart, onder elke indeling. Het overschot van
de gepubliceerde toets is daarmee vrijwel geheel definitioneel. 22 van 96 is wel meer
dan de 5 die onder een zuivere nul te verwachten zijn, dus bij een deel van de
locaties blijft een echte rest. Welke, staat in het rapport.

Voorbeeld om A, B en C uit elkaar te houden, D is droogteweek, F floodweek, N geen
van beide:

```
week:   1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
label:  D  D  D  F  F  F  N  F  F  N  D  D  N  F  F
```

Echte starts: week 4, 8 en 14. A mag een gesimuleerde start ook op 1, 2, 3, 11 en 12
zetten. B sluit die uit maar laat 5, 6, 9 en 15 toe, midden in een run, waar geen
start kan beginnen. C houdt 4, 7, 8, 10, 13 en 14 over. Week 4 is in elke nul
kandidaat, want week 3 is droogte en dus geen flood. Kandidaatweken voor een start
liggen daardoor geconcentreerd direct na droogtes, en C bouwt dat in de nul in.

### Een geprobeerde en verworpen nul: floodruns verplaatsen

Runs als blokken met behoud van lengte verplaatsen binnen de niet-droogtestukken,
met een scheidingsweek tussen aangrenzende runs. Zelfcontroles slaagden, maar de
constructie rust op het verbod op floods in droogteweken, en dat verbod klopt bij
0,5 niet. Op Aschach periode 1 gaf hij verwacht 61,7 tegen 52 waargenomen, p = 1,0.
Bij threshold 1, waar de overlap nul is, gaf hij ratio 1,0 tot 1,15, in lijn met C'.
Een gestratificeerde run-versie is te bouwen maar is niet gedaan.

### Kruiscontrole met het gevoeligheidsraster

`results/2026-09-02_sensitivity_grid_endfix/`, gepubliceerde nul A. De SRI-as doet
vrijwel niets, de floodpercentiel-as alles. Significante runs van 96 bij venster 4:

| SRI-drempel | 0,60 | 0,6915 | 0,80 | 0,90 | 0,95 |
|---|---|---|---|---|---|
| 0,25 | 89 | 92 | 93 | 84 | 52 |
| 0,5 | 90 | 92 | 93 | 66 | **30** |
| 0,75 | 90 | 88 | 80 | 32 | 8 |
| 1,0 | 86 | 79 | 52 | 13 | 3 |
| 1,5 | 59 | 31 | 7 | 4 | 0 |

Bij SRI 0,5 met percentiel 0,95 blijft 30 van de 96 over met gepoolde ratio 1,25,
onder nul A. Bij strenge drempels aan beide kanten keert het om naar ratio 0,5 tot
0,7. Twee onafhankelijke wegen, de nul repareren of de flooddefinitie aanscherpen,
komen op ongeveer ratio 1,2 uit.

### Weken en events schalen niet mee

Een event is een aaneengesloten reeks weken. Een strengere flooddrempel maakt events
vooral korter en neemt ze minder vaak weg. Wie over selectiviteit schrijft moet
weken en events uit elkaar houden, zie T-29.

### De kaart: waar de definities exclusief worden

Overlap als aandeel van de droogteweken, gepoold over 96 runs, per SRI-drempel en
floodpercentiel:

| SRI-drempel | 0,60 | 0,6915 | 0,80 | 0,90 | 0,95 |
|---|---|---|---|---|---|
| 0,25 | 20,2% | 10,6% | 3,2% | 0,6% | 0,1% |
| 0,5 | 13,1% | 5,9% | 1,6% | 0,3% | 0,0% |
| 0,75 | 7,1% | 2,8% | 0,8% | 0,2% | 0,0% |
| 1,0 | 3,6% | 1,7% | 0,5% | 0,1% | 0,0% |
| 1,5 | 1,2% | 0,5% | 0,1% | 0,0% | 0,0% |

De gepubliceerde configuratie, 0,5 met 0,6915, zit op 5,9 procent. Onder de procent
kom je bij SRI 0,5 vanaf floodpercentiel 0,90, en bij percentiel 0,6915 pas boven een
SRI-drempel van 1,5. Van de twee varianten uit route 2 hieronder is het
floodpercentiel omhoog dus de weg die de definities exclusief maakt zonder de
SRI-drempel van de copula te raken.

Dezelfde indeling, P(flood, gegeven niet-droogteweek), mediaan over 96 runs. Hoe
hoger, hoe meer "flood" samenvalt met "niet-droogte" en hoe groter het
lag-1-artefact:

| SRI-drempel | 0,60 | 0,6915 | 0,80 | 0,90 | 0,95 |
|---|---|---|---|---|---|
| 0,25 | 0,87 | 0,76 | 0,57 | 0,33 | 0,19 |
| 0,5 | 0,80 | 0,67 | 0,49 | 0,28 | 0,16 |
| 0,75 | 0,72 | 0,60 | 0,43 | 0,25 | 0,14 |
| 1,0 | 0,65 | 0,54 | 0,38 | 0,22 | 0,12 |
| 1,5 | 0,57 | 0,47 | 0,34 | 0,19 | 0,11 |

Deze twee kaarten zijn niet hetzelfde. De overlap is bij 0,90 al bijna weg, maar
de complementariteit zit daar nog op 0,28 en het lag-1-effect blijft.

### Wat niet fout is

- de implementatie en de reproductie van de notebook
- de reparatie van de einddetectie op 2 september, die versterkt het effect eerder
  dan dat hij het veroorzaakt
- de copula. Die selecteert alleen droogtes op `threshold`, via `Intensity_calc`
  naar `Drought_Intensity`, en heeft de floodkant als continue variabele, zie
  `_copula_inputs` in `src/dtf/copula.py`. **Het floodpercentiel in de ECA aanpassen
  raakt de copula dus niet, de SRI-drempel wel**

### Voorbehouden

- C en C' gebruiken de waargenomen floodreeks voor "week ervoor geen flood" en zijn
  daarmee deels circulair, mogelijk iets te streng. B en B' zijn te mild omdat ze
  een start midden in een floodrun laten vallen. De waarheid ligt tussen 1,25 en
  1,63 bij 0,5
- de ruimtelijke afhankelijkheid tussen locaties, al genoemd in de README van het
  raster, komt hier bovenop en maakt de gepoolde p te laag
- de veertien jaarverschuivingen als nul behouden seizoen en autocorrelatie maar
  laten floods in droogteweken vallen, en repareren dit dus niet: ratio 1,63 bij 0,5

### Routes, nog niet gekozen

1. **Nul repareren, drempels houden.** SRI 0,5 en percentiel 0,69 blijven, consistent
   met de copula en de tekst. Een variant van `monte_carlo_p_value` met
   gestratificeerde kandidaten en startregel, het raster opnieuw. Rapporteren met B'
   en C' als grenzen
2. **Definities exclusief maken door de drempel te verplaatsen.** Voorkeur van
   Floris, 4 september: een week hoort niet tegelijk droogte en flood te heten. Twee
   varianten: de SRI-drempel omhoog, wat breekt met de copula op 0,5, of het
   floodpercentiel in de ECA omhoog met SRI op 0,5, wat de copula niet raakt. De
   kaart hierboven laat zien vanaf waar de overlap onder de procent komt.
   **Kanttekening: exclusiviteit repareert de nul niet.** Bij threshold 1 is de
   overlap 0,3 procent en haalt C' de ratio toch van 1,26 naar 1,07. Het
   lag-1-effect komt uit de startregel, niet uit de overlap. Wie de drempel
   verplaatst moet de nul alsnog repareren, anders staat er een kleiner getal met
   dezelfde fout eronder
3. **Allebei.** De nul repareren als hoofdlijn en de flooddefinitie als
   gevoeligheidsas erbij. Het meest volledige antwoord op R4-01
4. **Eerst met co-auteurs.**

Niet in deze ronde: een nul op synthetische afvoer, een stochastisch model per
locatie met de volledige pijplijn erop, als controle van buitenaf op wat de
definities uit zichzelf produceren.

Bij elke route een regel in `CHANGELOG-methodology.md` zodra de keuze valt, want
de hoofdbevinding verandert van "1,8 keer zo vaak als toeval" naar iets tussen 1,25
en 1,63.

---

## D-21. De dataset is EFAS op 1 boogminuut, de tekst zegt 5 km en citeert het GloFAS-artikel

- herkomst: eigen bevinding, 5 september 2026, bij het uitzoeken van de vraag
  "EFAS of GloFAS" uit T-12 · raakt **Reviewer #4** (R4-02) en sectie 2.2
- status: **open, te bevestigen door Floris en Paolo.** Floris meldt op 5 september
  dat de data van ewds.climate.copernicus.eu komt, de Early Warning Data Store. Daar
  staan zowel EFAS als GloFAS, dus dat beslist het nog niet. De metadata in het
  bestand wel
- wie beslist: Floris, met Paolo voor de referenties

Gelezen uit `8_maart_european_river_runoff_1994_2024.nc`, de GRIB-attributen die bij
het downloaden zijn meegekomen:

| attribuut | waarde | betekenis |
|---|---|---|
| `GRIB_iDirectionIncrementInDegrees` | 0,016667 | 1 boogminuut, ongeveer 1,5 tot 1,8 km |
| `GRIB_Nx` x `GRIB_Ny` | 4530 x 2970 | Europees domein, lon -25,2 tot 50,2, lat 22,8 tot 72,2 |
| `GRIB_shortName` | `dis06` | "Mean discharge in the last 6 hours", de EFAS-variabele. GloFAS levert `dis24` op 0,1 graad wereldwijd |
| `GRIB_dateOfModelVersion` | 2023-01-01 | EFAS v5, de versie die op 1 boogminuut draait |
| `GRIB_centre` | ecmf | ECMWF als producent |

Conclusie: de dataset is **EFAS historical, versie 5, 1 boogminuut**, uit de EWDS.
Reviewer #4 heeft dus gelijk dat het EFAS/LISFLOOD is.

Drie dingen in sectie 2.2 kloppen daar niet mee:

1. **"5 x 5 km grid resolution"**: dat was EFAS v4. Versie 5 draait op 1 boogminuut.
2. **"forced with temperature and precipitation data from the ERA5 climate
   reanalysis"**: de EFAS historical simulations worden gedreven door het gridded
   observatieproduct EMO-1, niet door ERA5. Te bevestigen tegen de
   EWDS-documentatie van `efas-historical`, maar als dat klopt is ook de
   karakterisering "reanalyse gedreven door ERA5" van Reviewer #4 onjuist, en
   moet dat netjes in het antwoord
3. **Harrigan et al. 2020** is het GloFAS-ERA5-artikel. Voor EFAS hoort de
   referentie naar de EWDS-dataset zelf plus de EFAS-systeembeschrijving. In
   `review/referenties-r4-02-r4-04.md` wordt dan Tilloy et al. 2025 (HERA, 2448
   Europese stations) de belangrijkste validatiereferentie, en Hirpa 2018,
   Alfieri 2020 en Harrigan 2020 vallen weg of worden "vergelijkbaar product"

Wat er nog bij hoort: de reeks in het bestand heeft één waarde per dag om 12:00,
terwijl `dis06` een zesuursgemiddelde is. Hoe die dagwaarde tot stand is gekomen
(daggemiddelde bij download, of één van de vier zesuursvakken) moet Floris uit de
downloadinstellingen halen, want de tekst zegt "average daily (24-hour)".

Gevolg voor het werk: T-12 kan door zodra dit bevestigd is. Sectie 2.2 gaat mee in
batch B01 als feitelijke correctie, de referenties in B06.

---

## D-22. Zijn de locatiespecifieke severity-bevindingen robuust onder de drempelkeuze

- herkomst: eigen bevinding uit de gevoeligheidscontrole met strengere drempels
- status: **open**, het rekenwerk is klaar
- wie beslist: Floris met de co-auteurs

De drempelkeuze zelf is beslist, zie `CHANGELOG-methodology.md` van 4 september: 0,5
met gespiegeld floodniveau blijft. Wat daarbij naar boven kwam is een aparte vraag.

Over de 186 cellen die in beide analyses zitten is de correlatie tussen Kendall's tau
bij drempel 0,5 en bij drempel 1,0 slechts +0,12, en het teken komt in 52 procent van
de cellen overeen. Van de achttien cellen die bij 0,5 door minstens twee
onafhankelijkheidstoetsen worden aangewezen, blijven er twee over bij 1,0. De
gemeten spreiding van het verschil tussen beide tau's is 0,129, terwijl pure
toevalsvariatie bij de mediane omvang van 55 events al 0,093 oplevert.

Dat betekent niet dat de bevindingen bij 0,5 fout zijn. De vier toetsen daar zijn
onafhankelijk van elkaar en de clusters waren ruimtelijk samenhangend, wat tegen puur
toeval pleit. Maar het betekent wel dat ze aan de drempel hangen.

Drie manieren om ermee om te gaan, allemaal verdedigbaar:

1. de locatiespecifieke claims laten staan, met de drempel er expliciet bij en de
   gevoeligheid als beperking in de tekst
2. de claims terugbrengen tot het niveau van "op enkele locaties is er aanwijzing
   voor", zonder namen
3. de namen alleen noemen waar ze bij beide drempels standhouden, dat zijn Vistula
   Turon periode 1 en Rhine Straatsburg periode 2

Cijfers in `results/2026-09-04_strict_definition_report/report.md`, sectie 5.

---

## Administratief: dubbel gebruikt D-nummer

`D-21` staat twee keer in dit bestand, met verschillende onderwerpen: de
nulhypothese van de ECA die floods laat vallen, en de dataset die EFAS op 1
boogminuut blijkt te zijn. Beide zijn inhoudelijk in orde, alleen het nummer botst.
Hernummeren is aan Floris, want beide worden elders aangehaald.

