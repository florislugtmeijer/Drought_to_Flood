# Is er echt zo weinig copula-afhankelijkheid? Vier toetsen per cel

| | |
|---|---|
| gedraaid | 2 september 2026, op de gerepareerde einddetectie (commit 23429e1) |
| script | `scripts/25_dependence_tests.py` |
| omvang | 190 cellen, 1000 permutaties per cel, 12,8 minuten op 8 kernen |
| vraag | Floris: onderzoek opnieuw of de copula's echt zo weinig betekenis hebben, en of de significantiebepaling deugt |

## Waarom vier toetsen

De eerdere onderbouwing leunde op Kendall's tau als beschrijvend getal. Tau ziet
alleen monotone samenhang. Daarom vier invalshoeken: tau en Spearman's rho
(monotoon, analytische p), Hoeffding's D (ziet ook niet-monotone samenhang,
permutatie-p) en een permutatietoets op de copulafit zelf, waarbij de nulverdeling
dezelfde selectie over vijftien families doorloopt als de echte fit. Dat laatste is
essentieel: vijftien kandidaten vinden altijd wel iets, en die vertekening zit zo
in de nul. Daarnaast permutatie-p's voor het copula-deel van het gat op drie
floodniveaus.

Permuteren in plaats van bootstrappen is hier de juiste toets: husselen verbreekt
alleen de koppeling en laat beide marginale verdelingen exact intact. De bootstrap
beantwoordt hoe groot een effect is, de permutatie of het bestaat.

## Uitkomst over heel Europa

| toets | p < 0,05 | verwacht bij puur toeval | BH-FDR 5% |
|---|---|---|---|
| Kendall tau | 19 van 190 | 9,5 | 0 |
| Spearman rho | 18 | 9,5 | 0 |
| Hoeffding D | 14 | 9,5 | 0 |
| permutatie op de copulafit | 19 | 9,5 | 0 |
| copula-deel bij q=0,69 | 17 | 9,5 | 0 |

Twee keer de toevalsverwachting, dus een zwak maar echt signaal in het geheel,
maar geen enkele cel overleeft de correctie voor 190 gelijktijdige toetsen.

Kanttekening bij die laatste kolom: met 1000 permutaties is de kleinst mogelijke
p 0,001, terwijl de eerste BH-stap over 190 cellen p onder 0,00026 vraagt. De
permutatietoetsen kúnnen die drempel dus niet halen. De FDR-uitspraak steunt op de
analytische p van tau en rho, en ook daar overleeft niets.

## Maar het signaal clustert, en precies waar het artikel wijst

Twaalf cellen worden door minstens drie van de vier toetsen aangewezen, en dat zijn
geen losse toevalstreffers:

| cluster | richting | cellen |
|---|---|---|
| Po Piacenza, beide periodes, beide paren | positief | 4 |
| Ebro Haro en Tudela, periode 2, mean severity | positief | 2 |
| Tagus La Bazagona, periode 2, beide paren | positief | 2 |
| Danube Aschach, periode 1, mean severity | positief | 1 |
| Vistula Turon, periode 1, beide paren | negatief | 2 |
| Weser Bodenwerder, periode 1, drought peak | negatief | 1 |

Ebro Haro periode 2 mean severity haalt 4 van 4 met p's van 0,002 tot 0,006, het
sterkste resultaat van de hele kaart. Po Piacenza is de locatie die het artikel in
figuur 5 uitlicht, en de samenhang is daar in beide periodes aantoonbaar. Tagus
La Bazagona wordt op pagina 31 genoemd, al noemt de tekst periode 1 en vindt de
toets periode 2.

Voor deze vooraf benoemde locaties is de ongecorrigeerde p legitiem bewijs, want
de correctie voor 190 toetsen hoort bij zoeken over de hele kaart, niet bij het
toetsen van een vooraf aangewezen claim.

De negatieve cluster is er ook echt: bij Vistula en Weser geeft een zwaardere
droogte een lagere kans op een hoge piek. Dat past bij uitdroging van de bodem die
neerslag opvangt, en het is materiaal voor de fysische interpretatie waar R4-04 om
vraagt.

## De reparatie van de einddetectie maakte dit zichtbaar

Dezelfde toetsen op de oude definities gaven 13 in plaats van 19 cellen voor tau,
en de Ebro haalde toen helemaal niets. De fout, end_time een week te laat bij
eenweekse events en dat is ruim een derde van de droogtes, drukte de samenhang dus
ook aan de copulakant omlaag, net als bij de ECA waar de matches met 15,5 procent
stegen. Die tainted run staat in `results/2026-09-02_dependence_tests_GEMENGD/`.

## Conclusie

De eerdere formulering "het signaal dat overblijft is geen copula-signaal" was te
hard. Correct is: over heel Europa is er geen breed severity-effect, de meeste
cellen zijn niet te onderscheiden van toeval. Maar op een handvol locaties is de
afhankelijkheid echt, consistent over vier verschillende toetsen, en dat zijn
grotendeels precies de locaties waar het artikel op leunt: Po midstream in beide
periodes, Ebro in periode 2 voor mean severity, Tagus La Bazagona. Daarnaast is er
een even echt negatief cluster in Centraal-Europa dat nu nergens in de tekst staat.
