# Tabel E1, copulakeuze en transitiekansen bij 0,6915

Gemaakt door `scripts/42_appendix_e_copula_table.py`, 22 oktober 2026, uit
script 40 (copulakeuze met de nummer twee), de bootstrap met 0,6915 in het
rooster (iid) en de onafhankelijkheidstoetsen. 190 regels, een per locatie,
periode en droogtevariabele.

- `appendix_e_copula_table.md`: de tabel met Engels bijschrift, voor Appendix E
  en als los tabelbestand bij de hersubmissie (ED-06)
- `appendix_e_copula_table.csv`: alle velden, onafgerond

Controle: de puntschatting uit de bootstrap is gelijk aan die van script 40
(verschil 0,0).

Let op bij het lezen: het bootstrapinterval van het copula-deel en de
permutatietoets op dat deel zijn twee verschillende maten en vallen niet altijd
samen. Bij Ebro Tudela, periode 2, drought peak sluit het interval nul uit
([0,008, 0,102]) terwijl geen van de vier toetsen significant is. De tekst
noemt daarom alleen de grootte van het copula-deel en verwijst voor de
intervallen naar deze tabel.
