# Openstaande beslissingen

Beslissingen die de resultaten of de tekst van het artikel raken en die nog
genomen moeten worden. Niets hiervan wordt stilzwijgend opgelost. Bij elke
beslissing: wie beslist, en wat er verandert als het zo of zo valt.

Gesloten beslissingen verhuizen naar `CHANGELOG-methodology.md` met de
onderbouwing en het effect op de cijfers.

---

## D-01 Threshold: 0,5 of 1

**Status: open, maar de richting is nu bekend. Beslist door Floris.**
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
