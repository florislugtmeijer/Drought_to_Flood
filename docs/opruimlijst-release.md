# Opruimlijst voor de release van de code bij R2

Opgesteld 21 oktober 2026. Per regel ja of nee, dan voer ik het uit. Niets
hieruit is al gedaan.

**De regel, zoals Floris hem heeft gesteld:** in de repo komt de oude versie,
de nieuwe versie en de reden voor elke keuze. Geen opties of modellen die het
niet zijn geworden. Uitgewerkt als: een variant blijft alleen als er een getal
uit in het artikel of de Revision Notes staat. Besluit van Floris, 21 oktober:
de alternatieve nullen B′ en D′ worden niet behouden en niet genoemd. A blijft
als de gepubliceerde versie, C′ als de nieuwe.

Het R2-werk staat op `eca-endtime-fix`. Deze lijst beschrijft wat er van die tak
naar `main` gaat. `review/` en `manuscript/` gaan in geen geval mee.

---

## A. Eerst inhoud, anders lever je verkeerde getallen mee

Dit moet af voordat er iets gemerged wordt. Zonder deze stappen staat er in de
release een map met pre-fix cijfers of een tabel onder de oude nul.

| # | wat | waarom | ja/nee |
|---|---|---|---|
| O-01 | scripts 19 en 21 herdraaien op de gerepareerde code | `copula_corrected` en de figuren daarin zijn nog pre-fix, al sinds 3 september een restant van T-11. **Aanvulling 21 oktober:** 19 rekent ook de afgewezen empirische marginalen mee, en 21 is een vergelijkingsfiguur die de gepubliceerde curves uit de map van het verwijderde script 14 leest. Eerst kiezen welke figuren figuur 5 tot 8 worden (D-17), dan pas herdraaien | |
| O-02 | script 12 herdraaien, of de gekozen copulafamilie per cel uit de bootstrapmap halen | `copula_selection` is pre-fix. De appendixtabel voor R4-03 (welke familie per cel) mag daar niet uit komen | |
| O-03 | script 27 (fysische tabel, T-17) omzetten naar C′ | **gecorrigeerd 21 oktober:** de ratio komt niet uit het raster maar wordt in het script zelf berekend, met als verwachting het aandeel van alle weken waarna binnen vier weken een flood begint. Dat is de logica van nul A. Alleen `p_mc_trigger` komt uit het A-raster. Omzetten vraagt dus een nieuwe definitie van de verwachtingskolom, bijvoorbeeld `expCp / n_dr` uit `production.csv`. **Methodekeuze, wacht op Floris** | |
| O-04 | rapport- en figuurscript voor het C′-raster maken | het raster is klaar (2400 van 2400), maar de figuren en de concepttekst voor R4-01 (T-58) zijn gemaakt op het A-raster. Script 10 doet dat nu voor het oude raster | |
| O-05 | het script voor Tabel 3 maken (script 39 in T-15) onder C′, p-waardes op drie significante cijfers | bestaat nog niet. Tabel 3 is de hoofdtabel en verandert door C′ | |
| O-06 | flood-magnitude test (04) en seizoenscontrole (05) herdraaien, of eruit | beide van augustus, dus vóór de ECA-reparatie. T-13 wil de drie beperkingen uit de magnitude-test in de tekst, dan moet hij post-fix | |

---

## B. Scripts

"Erin" betekent: gaat naar `main`, krijgt bij het hernummeren een nieuw nummer
in de volgorde van de analyse.

| # | script | voorstel | reden | ja/nee |
|---|---|---|---|---|
| O-10 | 01 eca_threshold_comparison | eruit | pre-fix, vervangen door het raster | |
| O-11 | 02 sri_diagnostic | erin | levert de cijfers voor de Dnieper-alinea (D-12) | |
| O-12 | 03 quantile_reference_variant | eruit | rekende bij drempel 1, vervangen | |
| O-13 | 04 flood_magnitude_test | erin na O-06, anders eruit | | |
| O-14 | 05 season_control | erin na O-06, anders eruit | | |
| O-15 | 06 threshold_selectivity | erin | 44,6 tegen 35,8 procent in T-29, weekpercentages, niet geraakt door de reparatie | |
| O-16 | 07 en 08 reference_grid | erin | de verschuiving van de drempels tussen de periodes (D-13), staat in de Revision Notes | |
| O-17 | 09 en 10 sensitivity_grid onder nul A | eruit na O-03 en O-04 | het raster onder de oude nul. R1 had geen raster, dus het is oud noch nieuw | |
| O-18 | 11 copula_timing | eruit | rekentijdmeting | |
| O-19 | 12 copula_selection | erin na O-02 | | |
| O-20 | 13 copula_scale_check | eruit | diagnose tijdens de copula-review | |
| O-21 | 14 tot en met 18, copula-review | eruit | het zoekwerk naar de F_Y-fout. De fout en het effect staan in de changelog | |
| O-22 | 15 function_dependency_map | eruit | interne kaart van de notebook | |
| O-23 | 19 en 21 corrected | erin na O-01 | | |
| O-24 | 20 unconditional_on_rank | **vraag** | een van de drie presentaties uit de copula-review. Hangt af van welke presentatie in de figuren komt (D-17) | |
| O-25 | 22 bootstrap | erin | intervallen voor R4-03 | |
| O-26 | 23 bootstrap_report | eruit | intern rapport | |
| O-27 | 24 bootstrap_figures | erin als er een figuur uit in het artikel komt, anders eruit | | |
| O-28 | 25 dependence_tests | erin | basis van het telcriterium (D-19) | |
| O-29 | 26 method_report_pdf | eruit | intern uitlegdocument | |
| O-30 | 27 physical_results_table | erin na O-03 | | |
| O-31 | 27, 28 en 30 strict | erin | de Revision Notes noemen tau-correlatie 0,12 en de 46 procent na de droogte, en D-22 markeert namen bij drempel 1,0. Dat is een gerapporteerde gevoeligheid, geen afgewezen model | |
| O-32 | 29 strict_report_pdf | eruit | intern rapport | |
| O-33 | 28 copula_quantile_reference | erin | +0,055 tegen +0,056 staat in de Revision Notes | |
| O-34 | 29 increase_criterion_counts | erin | de tellingen 1, 2, 2, 4 op pagina 31 | |
| O-35 | 31 tot en met 35, nul-verkenning | eruit | besluit Floris 21 oktober | |
| O-36 | 36 eca_null_production | erin, D′ uit de docstring | rekent A en C′ naast elkaar. B′ zit er als kolom in, zie O-60 | |
| O-37 | 37 sensitivity_grid_cprime | erin | het nieuwe raster voor R4-01 | |
| O-38 | 38 t62_location_claims | **vraag** | beslisrapport voor de formulering bij D-22. Erin alleen als er een tabel uit in het artikel komt | |

---

## C. Resultaatmappen

`results/` staat nu helemaal in `.gitignore`, er gaat dus niets vanzelf mee.
Voorstel: geen gedateerde werkmappen in `main`, maar een map `figures/` en een
map `tables/` met alleen wat in het artikel en de appendices staat, gemaakt door
de scripts uit B. De ruwe uitvoer is met de scripts opnieuw te maken.

| # | wat | voorstel | ja/nee |
|---|---|---|---|
| O-40 | `figures/` en `tables/` aanmaken, genummerd zoals in het artikel | erin, nodig voor ED-06 | |
| O-41 | `_ONGELDIG`, `_PREFIX_ENDTIME`, `_GEMENGD`, samen ongeveer 14 MB | lokaal verwijderen, ze staan niet in git | |
| O-42 | grote uitvoer die meegaat voor wie niet wil herrekenen: `production.csv` en `grid.csv` van C′, bootstrap- en toetsuitvoer | **vraag**: meeleveren of alleen de scripts | |

---

## D. Documenten

| # | wat | voorstel | reden | ja/nee |
|---|---|---|---|---|
| O-50 | `CHANGELOG-methodology.md` | erin als publieke versie, ingekort | de huidige versie bevat B′, D′, D″, P-02 en de strenge drempel als afgewogen opties. De publieke versie geeft per wijziging oud, nieuw, reden en effect op de cijfers. De volledige versie blijft lokaal | |
| O-51 | `docs/open-decisions.md` en `proposed-changes.md` | eruit | interne beslisdocumenten met alle afgewezen routes | |
| O-52 | `docs/todo.md` | eruit | interne werklijst | |
| O-53 | `docs/reproducibility-check.md` | erin | laat zien dat Tabel 3 van R1 exact uit de notebook komt. Dat onderbouwt de oude versie | |
| O-54 | `docs/function-provenance.md` | erin | welke notebookcel welke functie in `src/dtf/` werd. Dat is de brug van oud naar nieuw | |
| O-55 | `notebooks/` met de R1-notebook | erin | de oude versie | |
| O-56 | `.claude/skills/` | eruit | interne werkafspraken | |
| O-57 | `review/` en `manuscript/` | eruit | vertrouwelijk, blijft in `.gitignore` | |

---

## E. Wat er nog niet is en gemaakt moet worden

| # | wat | toelichting | ja/nee |
|---|---|---|---|
| O-60 | B′ uit `production.csv` laten of de kolommen weghalen | B′ zit als kolom in de productierun. Wegfilteren bij het wegschrijven is schoon, de run zelf hoeft niet opnieuw | |
| O-61 | databestand in de repo met checksum | `data/raw/`, 1,48 MB, SHA256 begint met `d5900f65cdb394ad`. Bij die stap een naam zonder 1994 (de data begint op 1 januari 1995), met alle paden in één keer mee | |
| O-62 | alle paden uit `~/Downloads/` halen | twintig scripts openen het bestand nu daar. Eén plek in `config/` | |
| O-63 | `config/analysis.yaml` | drempel 0,5, floodniveau 0,6915, venster 4 weken, 10.000 simulaties, seeds. Nu verspreid over code en scriptargumenten | |
| O-64 | `pyproject.toml` en `uv.lock` | `vinecopulas` moet vast, de familie-nummering en de bekende Clayton-fout hangen aan de versie | |
| O-65 | `README.md` | wat het is, hoe je het draait, in welke volgorde, welk script welke figuur of tabel maakt, verwijzing naar het artikel | |
| O-66 | scripts hernummeren in de volgorde van de analyse | lost de dubbele nummers 15, 27, 28 en 29 op | |
| O-67 | docstrings opschonen | 09, 10, 22 en 36 verwijzen naar mappen die niet meegaan, onder meer D′ | |
| O-68 | `LICENSE` en `CITATION.cff` | **vraag**: welke licentie. Mogelijk heeft de VU daar beleid over | |
| O-69 | `.DS_Store` en `__pycache__` weg en in `.gitignore` | | |
| O-70 | data-availability statement in het manuscript | verwijst naar de repo. Pas na de hernoeming van de repo | |

---

## Open vragen in deze lijst

O-24, O-38, O-42 en O-68 vragen een keuze. De rest is een voorstel waar ja of
nee volstaat.
