# Openstaande beslissingen

**Bijgewerkt 23 augustus 2026 na verificatie.** Verscheidene punten hieronder
kwamen uit de verkeerde notebook-versie en zijn vervallen. Zie
`docs/reproducibility-check.md`. Vervallen: D-03, D-08, D-09, D-10.
Nog echt open: D-01, D-02, D-04, D-05, D-06, D-07.

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

**Status: doorgerekend op 23 augustus 2026, beslissing nog open. Beslist door Floris.**

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
de reviewer en geen leesfout van onze kant.

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

**Status: open. Beslist door Floris.**

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

**Status: open, laag risico.**

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

**Status: open. Beslissing voor Floris. Raakt alle event-aantallen.**
**Aanleiding: vraag van Floris, 23 augustus 2026.**

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

| locatie | boven flooddrempel | onder droogtedrempel |
|---|---|---|
| Aschach an der Donau | 28,2% | 14,8% |
| Donji Milanovac | 24,9% | 17,2% |
| Bremen | 24,7% | 16,1% |

De droogtekant klopt: `norm.cdf(-1)` is 0,1587, dus ongeveer 16 procent. De
floodkant ligt op 25 tot 28 procent, ruim anderhalf keer zo vaak. Van spiegelen
is dus geen sprake.

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

**B. Huidige berekening houden en de tekst aanpassen.** De methodensectie zegt
nu al "quantiles relative to the entire dataset for each location", en dat is
precies wat de code doet. Dan moet alleen de "mirroring"-claim eruit en moet
erbij dat de flooddrempel in de praktijk 25 tot 28 procent van de weken selecteert.

Route B verandert geen cijfers. Route A is methodologisch schoner. Beide vragen
een aanpassing in de tekst, want zoals het er nu staat is het niet juist.

Hoort bij R4-01, want dat punt gaat over de onderbouwing van precies deze
drempels.

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
