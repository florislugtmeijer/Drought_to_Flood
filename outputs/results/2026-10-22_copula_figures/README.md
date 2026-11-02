# Figuren 5 tot 9, copula-transitiekansen (R2)

Gemaakt door `scripts/41_copula_figures.py`, 22 oktober 2026, ongeveer een halve
minuut. Po Piacenza en Ebro Tudela voor beide droogtevariabelen (figuur 5 tot 8),
Vistula Toruń voor mean severity (figuur 9). Periode 1 boven, periode 2 onder.

- links: P(hoogste afvoer in de vier weken na de droogte > q | droogte >= x).
  Gestippeld de milde en de zware drempel; ontbreekt de zware lijn, dan ligt die
  drempel buiten de waargenomen droogtes (Po Piacenza, mean severity)
- rechts: milde (blauw) en zware (oranje) curve met 95%-bootstrapband (iid,
  B = 2000), unconditioneel (doorgetrokken grijs), onafhankelijkheid 1 - F_Y
  (gestippeld grijs), floodniveau 0,6915 (lichtgrijs verticaal)
- paneeltitel rechts: aantal droogtes en het aantal boven de zware drempel

Controles in `check.txt`: puntcurves gelijk aan de bootstrap (grootste afwijking
5e-07), oppervlakrij bij de milde drempel binnen 0,003 van de milde curve.

Kleuren gevalideerd op kleurenblindheid (blauw #2a78d6 tegen oranje #eb6834,
CVD dE 24,7). De ingediende figuren gebruikten groen en rood, en hun gearceerde
vlak was het gebied tussen de milde en de zware curve, geen onzekerheidsband.
