# Colab-bronbestanden

Archief. Deze notebooks worden niet meer bijgewerkt. Ze staan hier als ijkpunt
voor de herstructurering naar `src/dtf/`.

## `drought_to_flood_europe_colab_2026-08-23.ipynb`

De actuele bron, 104 cellen, 71 code. Geëxporteerd uit Colab op 23 augustus 2026.
Oorspronkelijke naam:
`LAATSTE_VERSIE_Kopie_van_Kopie_van_working_document_article_laatste (1).ipynb`.

Outputs en `execution_count` zijn gestript. De uitvoeringsvolgorde van de
oorspronkelijke Colab-sessie is hier dus niet uit te lezen, en daarmee ook niet
welke van de dubbele functiedefinities de gepubliceerde resultaten heeft gemaakt.

## `drought_to_flood_europe_colab_2026-03-02_with_outputs.ipynb`

Versie van 2 maart 2026. Inhoudelijk vrijwel gelijk aan de bovenstaande: het
verschil zit in twee cellen, een uitgecommentarieerde `set_index` in cel 20 en
drie witregels in cel 62.

Belangrijk omdat 22 code-cellen hier nog hun output hebben. Dat is het enige
harde ijkpunt om te controleren of de herstructureerde code dezelfde getallen
oplevert. Niet weggooien.

## Waarom dit archief bestaat

De bron bevat 47 functiedefinities voor 33 unieke functies. Veertien functies
hebben inhoudelijk verschillende varianten, `monte_carlo_p_value` heeft vier
implementaties. Welke variant canoniek is, wordt per functie vastgesteld en
gedocumenteerd in `CHANGELOG-methodology.md`. Tot dat af is, is dit archief de
enige plek waar alle varianten bewaard zijn.
