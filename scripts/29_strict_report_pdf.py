"""Strikte definities: het vergelijkende rapport, als PDF.

Zet de gevoeligheidsvariant met droogtedrempel 1 en floodniveau 0,8413 naast de
gerapporteerde analyse op 0,5 en 0,6915. Rekent niets opnieuw; leest
  results/2026-09-04_strict_definition_points/     puntschattingen, beide varianten
  results/2026-09-04_strict_dependence_tests/      toetsen, strikt
  results/2026-09-04_strict_copula_bootstrap/      intervallen, strikt
  results/2026-09-02_dependence_tests/             toetsen, referentie
  results/2026-09-02_copula_bootstrap/             intervallen, referentie

Uitvoer: results/2026-09-04_strict_definition_report/report.md, report.pdf en
drie figuren.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with matplotlib --with markdown --with xhtml2pdf \
      --no-project python scripts/29_strict_report_pdf.py
"""
import csv, os, collections
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import markdown
from xhtml2pdf import pisa

ROOT = os.getcwd()
PTS = "results/2026-09-04_strict_definition_points"
DEP_S = "results/2026-09-04_strict_dependence_tests/dependence_tests.csv"
BS_S = "results/2026-09-04_strict_copula_bootstrap"
DEP_R = "results/2026-09-02_dependence_tests/dependence_tests.csv"
BS_R = "results/2026-09-02_copula_bootstrap"
OUT = "results/2026-09-04_strict_definition_report"
FIG = f"{OUT}/figures"
os.makedirs(FIG, exist_ok=True)
YC = [f"y_{i:03d}" for i in range(101)]
KOLS = ("tau_p", "hoeffd_p", "aic_perm_p")          # cp-toets valt weg bij strikt, zie tekst
PAIR_NL = {"drought_peak": "drought peak", "mean_drought_severity": "mean severity"}
PER_NL = {"first": "1", "second": "2"}
GREEN, RED, BLUE, GREY, ORANGE = "#2a7f3f", "#c0392b", "#2c6fbb", "#7a7a7a", "#e08214"


def lees(pad):
    return list(csv.DictReader(open(pad))) if os.path.exists(pad) else []


def cel(r):
    return (r["river"], r["village"], r["period"], r["pair"])


pts = lees(f"{PTS}/summary.csv")
ovl = lees(f"{PTS}/week_overlap.csv")
dep_s = {cel(r): r for r in lees(DEP_S)}
dep_r = {cel(r): r for r in lees(DEP_R)}
diag_s = {cel(r): r for r in lees(f"{BS_S}/bootstrap_diagnostics.csv") if r["scheme"] == "iid"}
diag_r = {cel(r): r for r in lees(f"{BS_R}/bootstrap_diagnostics.csv") if r["scheme"] == "iid"}


def lees_ci(pad):
    d = {}
    for r in lees(pad):
        if r["scheme"] != "iid":
            continue
        d[cel(r) + (r["quantity"], r["kind"])] = np.array([float(r[c]) for c in YC])
    return d


ci_s = lees_ci(f"{BS_S}/transition_ci.csv")
ci_r = lees_ci(f"{BS_R}/transition_ci.csv")
heeft_bs = bool(diag_s)
print(f"punten {len(pts)}, overlap {len(ovl)}, toetsen strikt {len(dep_s)}, "
      f"bootstrap strikt {len(diag_s)}", flush=True)


def w(ci, c, q, soort, j):
    k = c + (q, soort)
    return float(ci[k][j]) if k in ci else np.nan


def fmt_ci(ci, c, q, j):
    p, lo, hi = w(ci, c, q, "point", j), w(ci, c, q, "lo", j), w(ci, c, q, "hi", j)
    if not np.isfinite(p):
        return "geen"
    ster = "**" if (lo > 0 or hi < 0) else ""
    return f"{ster}{p:+.3f}{ster} [{lo:+.3f}, {hi:+.3f}]"


def n_toetsen(d):
    return sum(1 for k in KOLS if d and float(d[k]) < 0.05)


def sluit_uit(ci, q, j):
    p = n = t = 0
    for c in {k[:4] for k in ci}:
        lo, hi = w(ci, c, q, "lo", j), w(ci, c, q, "hi", j)
        if not (np.isfinite(lo) and np.isfinite(hi)):
            continue
        t += 1; p += lo > 0; n += hi < 0
    return p, n, t


def fig(pad, cap):
    return f'\n<div class="fig"><img src="{ROOT}/{pad}" /><p class="cap">{cap}</p></div>\n'


# ------------------------------------------------------------------ cijfers
ref = [r for r in pts if r["variant"] == "referentie_0.5"]
stk = [r for r in pts if r["variant"] == "strikt_1.0"]
n_ref = np.array([int(r["n_events"]) for r in ref]); n_stk = np.array([int(r["n_events"]) for r in stk])
kmin_s = np.array([int(r["k_minor"]) for r in stk]); kmaj_s = np.array([int(r["k_major"]) for r in stk])
tmin_s = np.array([float(r["t_minor"]) for r in stk])
collapse = int(np.sum(tmin_s < 0.01))
ov_r = [r for r in ovl if r["variant"] == "referentie_0.5"]; ov_s = [r for r in ovl if r["variant"] == "strikt_1.0"]


def ov_som(rows, k):
    return sum(int(r[k]) for r in rows)


def med(rows, k):
    v = np.array([float(r[k]) for r in rows if r[k] not in ("", "nan")])
    v = v[np.isfinite(v)]
    return np.median(v) if len(v) else np.nan


L = []; A = L.append
A("# Strikte definities: droogte bij SRI onder -1, floodniveau 0,8413")
A("## Effect op de copula-analyse, vergeleken met de gerapporteerde analyse op 0,5")
A("")
A("*Gevoeligheidsvariant op verzoek van Floris, 4 september 2026. Strikt gescheiden")
A("van de hoofdanalyse: eigen scripts, eigen resultaatmappen, geen bestaande code")
A("aangepast. De referentie op 0,5 is in dezelfde run met dezelfde seeds opnieuw")
A("berekend zodat de vergelijking zuiver is.*")
A("")
A("## 0. De vraag en wat de drempel wel en niet raakt")
A("")
A("Bij drempel 0,5 is een week droogte als de wekelijkse SRI onder -0,5 ligt, en flood")
A("als het wekelijkse maximum boven quantiel 0,6915 komt. Die twee sluiten elkaar niet")
A("uit. De vraag is wat er gebeurt als beide strenger worden: droogte onder -1, flood")
A("boven norm.cdf(1) = 0,8413, dus dezelfde z-score gespiegeld.")
A("")
A("In de copula-kant werkt dat anders dan in de ECA-kant. De **droogtedrempel** raakt")
A("alles: welke weken droogte zijn, hoeveel events er zijn, de drought peak en de mean")
A("severity, die nu het tekort onder -1 meet. De **flooddrempel** raakt de berekening")
A("niet, want de floodzijde van de copula is continu, het hoogste quantiel in het")
A("venster na de droogte. De spiegeling naar 0,8413 bepaalt alleen op welk niveau we")
A("aflezen. Voor de ECA-kant, waar de flooddrempel wél in de telling zit, bestaat het")
A("gevoeligheidsraster al: drempel 1 met floodquantielen 0,8 en 0,9 staat daar in.")
A("")
A("**Eén gevolg vooraf.** Pagina 22 zet de grens voor een milde droogte op drought peak")
A("1 en voor een zware op 2. Met droogtedrempel 1 heeft elke droogte per definitie een")
A("piek van minstens 1, dus valt elke droogte onder \"mild\". De milde curve wordt dan de")
A("onafhankelijkheidslijn en het copula-deel van de milde curve is per constructie nul.")
A(f"Gemeten: bij {collapse} van de {len(stk)} strikte cellen is de milde drempel op de")
A("copula-schaal vrijwel nul. De X-waardes zijn bewust ongewijzigd gelaten, dat is een")
A("besluit voor Floris. Wat overeind blijft en hieronder centraal staat: de zware curve,")
A("het verschil zwaar min mild, en de vier toetsen op afhankelijkheid, die niet van X")
A("afhangen.")
A("")

# ------------------------------------------------------------------ 1
A("## 1. Hoe vaak is een week tegelijk droogte en flood")
A("")
A("Over alle 96 locatie-periodes samen, met de eigen gespiegelde floodgrens:")
A("")
A("| | drempel 0,5 / 0,6915 | drempel 1,0 / 0,8413 |")
A("|---|---|---|")
A(f"| droogteweken | {ov_som(ov_r,'drought_weeks')} | {ov_som(ov_s,'drought_weeks')} |")
A(f"| floodweken | {ov_som(ov_r,'flood_weeks')} | {ov_som(ov_s,'flood_weeks')} |")
A(f"| weken die beide zijn | {ov_som(ov_r,'both_weeks')} | {ov_som(ov_s,'both_weeks')} |")
A(f"| aandeel van de droogteweken dat ook flood is | {ov_som(ov_r,'both_weeks')/max(1,ov_som(ov_r,'drought_weeks')):.1%} | {ov_som(ov_s,'both_weeks')/max(1,ov_som(ov_s,'drought_weeks')):.1%} |")
A("")
A("De overlap bestaat dus bij 0,5, en de strengere definitie brengt hem terug. Merk op")
A("dat de overlap alleen de weekindeling raakt; in de copula-kant wordt de flood na de")
A("droogte pas in het venster ná het event gemeten, dus een droogteweek die zelf ook")
A("flood is telt daar niet als de piek erna.")
A("")

# ------------------------------------------------------------------ 2
A("## 2. Wat er met de events gebeurt")
A("")
A("| | referentie 0,5 | strikt 1,0 |")
A("|---|---|---|")
A(f"| droogte-events per cel, mediaan | {int(np.median(n_ref))} | {int(np.median(n_stk))} |")
A(f"| kleinste cel | {n_ref.min()} | {n_stk.min()} |")
A(f"| cellen onder 15 events, geen bootstrap | {int(np.sum(n_ref<15))} van {len(ref)} | {int(np.sum(n_stk<15))} van {len(stk)} |")
A(f"| events boven de zware drempel, mediaan k_major | {int(np.median([int(r['k_major']) for r in ref]))} | {int(np.median(kmaj_s))} |")
A(f"| cellen zonder enkele zware droogte | {sum(1 for r in ref if int(r['k_major'])==0)} | {int(np.sum(kmaj_s==0))} |")
A("")
A("De strengere drempel halveert ruwweg het aantal droogtes. Dat maakt elke schatting")
A("onzekerder en laat meer cellen zonder zware curve. De weinige zware droogtes die er")
A("wel zijn, zijn dan ook echt zwaar: SRI onder -2.")
A("")

# ------------------------------------------------------------------ 3
A("## 3. De puntschattingen: het gat en zijn onderdelen")
A("")
A("Mediaan over de cellen, beide varianten op vier afleesniveaus. Zo is te scheiden wat")
A("het afleesniveau doet en wat de droogtedrempel doet.")
A("")
A("| variant | niveau | uncond. | milde curve | gat | marginaal | copula (mild) | cellen gat < 0 |")
A("|---|---|---|---|---|---|---|---|")
for vnaam, rows in (("referentie 0,5", ref), ("strikt 1,0", stk)):
    for q in ("0.6915", "0.8413", "0.9", "0.95"):
        g = np.array([float(r[f"gap_q{q}"]) for r in rows if r[f"gap_q{q}"] not in ("", "nan")])
        g = g[np.isfinite(g)]
        A(f"| {vnaam} | {q.replace('.', ',')} | {med(rows, f'uncond_q{q}'):.3f} | "
          f"{med(rows, f'minor_q{q}'):.3f} | {med(rows, f'gap_q{q}'):+.3f} | "
          f"{med(rows, f'marginal_part_q{q}'):+.3f} | {med(rows, f'copula_part_q{q}'):+.3f} | "
          f"{int(np.sum(g < 0))} van {len(g)} |")
A("")
A("**Dit is de belangrijkste uitkomst van de variant.** Bij drempel 0,5 is het venster")
A("na een droogte natter dan een willekeurig venster, en dat effect neemt af naar de")
A("hoge quantielen toe. Bij drempel 1,0 is het venster na een droogte **droger** dan")
A("een willekeurig venster, op elk niveau, en in ruim twee derde van de cellen. Dat is")
A("de droogtedrempel en niet het afleesniveau: op hetzelfde niveau 0,8413 staat de")
A(f"referentie op {med(ref, 'marginal_part_q0.8413'):+.3f} en strikt op")
A(f"{med(stk, 'marginal_part_q0.8413'):+.3f}.")
A("")
A("Het copula-deel van de milde curve is bij strikt exact nul, zie sectie 0. Het hele")
A("gat is daar dus marginaal.")
A("")
A("### 3.1 Waarom het teken omdraait: het einde van een strenge droogte is geen einde van droogte")
A("")
A("Een droogte eindigt in de code op het moment dat de SRI weer boven de drempel komt.")
A("Bij drempel 1 is dat boven -1, en dan zit de rivier vaak nog in een milde droogte")
A("tussen -1 en -0,5. Het \"venster na de droogte\" valt dan grotendeels nog in droge")
A("omstandigheden, en een lage piek is dan geen verrassing. Bij drempel 0,5 betekent het")
A("einde dat de omstandigheden echt zijn omgeslagen. Gemeten in de vier weken na afloop:")
A("")
pd_ = lees(f"{PTS}/post_drought_sri.csv")
if pd_:
    A("| | referentie 0,5 | strikt 1,0 |")
    A("|---|---|---|")
    for lab, k in (("gemiddelde SRI na afloop", "mean_sri_after_events"),
                   ("aandeel weken na afloop met SRI < -0,5", "share_weeks_below_m05_after_events"),
                   ("aandeel weken na afloop met SRI < -1", "share_weeks_below_m1_after_events"),
                   ("gemiddelde SRI over alle weken", "mean_sri_all_weeks"),
                   ("aandeel van alle weken met SRI < -0,5", "share_weeks_below_m05_all")):
        a = np.median([float(r[k]) for r in pd_ if r["variant"] == "referentie_0.5"])
        b_ = np.median([float(r[k]) for r in pd_ if r["variant"] == "strikt_1.0"])
        fmt = (lambda x: f"{x:+.3f}") if "gemiddelde" in lab else (lambda x: f"{x:.1%}")
        A(f"| {lab} | {fmt(a)} | {fmt(b_)} |")
    A("")
    A("Mediaan over de 96 locatie-periodes. Onder strikt is een groot deel van de weken na")
    A("afloop nog steeds droog naar de maatstaf van de hoofdanalyse. Het venster meet dan")
    A("eerder het herstel uit een diepe droogte dan een overgang naar nat.")
else:
    A("*De toestandsdiagnose (post_drought_sri.csv) was nog niet beschikbaar.*")
A("")
A("Dit is een definitiekwestie, geen hydrologische bevinding op zichzelf. Wie de strenge")
A("droogtedrempel wil gebruiken en toch de overgang naar nat wil meten, moet het einde")
A("van de droogte anders definiëren, bijvoorbeeld als het moment dat de SRI weer boven")
A("-0,5 komt, of het venster later laten beginnen. Dat is een keuze voor Floris.")
A("")
A(fig(f"{FIG}/strict_overlap_events.png",
      "Figuur 1. Links: aandeel droogteweken dat tegelijk floodweek is, per locatie-periode, "
      "onder beide definities. Rechts: aantal droogte-events per cel, referentie tegen strikt."))
A("")

# ------------------------------------------------------------------ 4
A("## 4. De copulakeuze onder de strenge definitie")
A("")
if heeft_bs:
    cs = collections.Counter(r["copula_point"] for r in diag_s.values())
    cr = collections.Counter(r["copula_point"] for r in diag_r.values())
    fam = sorted(set(cs) | set(cr), key=lambda f: -(cs[f] + cr[f]))
    A("| familie | referentie | strikt | familie | referentie | strikt |")
    A("|---|---|---|---|---|---|")
    for i in range(0, len(fam), 2):
        row = f"| {fam[i]} | {cr[fam[i]]} | {cs[fam[i]]} "
        row += f"| {fam[i+1]} | {cr[fam[i+1]]} | {cs[fam[i+1]]} |" if i + 1 < len(fam) else "| | | |"
        A(row)
    sh_s = np.array([float(r["modal_share"]) for r in diag_s.values()])
    sh_r = np.array([float(r["modal_share"]) for r in diag_r.values()])
    nf_s = np.array([int(r["n_families_seen"]) for r in diag_s.values()])
    same_s = sum(1 for r in diag_s.values() if r["copula_point"] == r["copula_modal"])
    zelfde = sum(1 for c in diag_s if c in diag_r and diag_s[c]["copula_point"] == diag_r[c]["copula_point"])
    A("")
    A(f"Stabiliteit over de bootstrap-replicaties: de winnaar komt strikt mediaan in")
    A(f"**{np.median(sh_s):.0%}** van de replicaties terug, tegen {np.median(sh_r):.0%} bij de")
    A(f"referentie; mediaan {int(np.median(nf_s))} verschillende families per cel. In")
    A(f"{same_s} van de {len(diag_s)} strikte cellen is de winnaar ook de modus.")
    A(f"Van de cellen die in beide analyses zitten kiest AIC in **{zelfde}** dezelfde")
    A("familie. Met minder events wordt de keuze dus nog losser dan hij al was.")
else:
    A("*De strikte bootstrap was nog niet klaar toen dit rapport werd gemaakt.*")
A("")

# ------------------------------------------------------------------ 5
A("## 5. De toetsen op afhankelijkheid: bestaat de samenhang nog")
A("")
A("Dezelfde vier toetsen als in de hoofdanalyse. Ze hangen niet af van de X-grenzen en")
A("zijn dus onder strikt volledig informatief. De toets op het copula-deel valt weg,")
A("omdat dat deel bij strikt per constructie nul is.")
A("")
A("| toets | referentie 0,5 | strikt 1,0 | verwacht bij toeval |")
A("|---|---|---|---|")
for k, naam in (("tau_p", "Kendall's tau"), ("rho_p", "Spearman's rho"),
                ("hoeffd_p", "Hoeffding's D"), ("aic_perm_p", "permutatie op de copulafit")):
    a = sum(1 for d in dep_r.values() if float(d[k]) < 0.05)
    b = sum(1 for d in dep_s.values() if float(d[k]) < 0.05)
    A(f"| {naam} | {a} van {len(dep_r)} | {b} van {len(dep_s)} | {len(dep_r)*0.05:.1f} / {len(dep_s)*0.05:.1f} |")
tau_r = np.array([float(d["tau"]) for d in dep_r.values()]); tau_s = np.array([float(d["tau"]) for d in dep_s.values()])
A("")
A(f"Mediaan tau: referentie {np.median(tau_r):+.3f}, strikt {np.median(tau_s):+.3f}.")
A("")
sterk_s = sorted([(c, n_toetsen(d), d) for c, d in dep_s.items() if n_toetsen(d) >= 2],
                 key=lambda x: -abs(float(x[2]["tau"])))
sterk_r = {c for c, d in dep_r.items() if n_toetsen(d) >= 2}
A(f"### Cellen die onder strikt minstens twee van de drie toetsen halen: {len(sterk_s)}")
A("")
A("Drie toetsen in plaats van vier, dus \"minstens twee\" is hier het equivalent van de")
A("\"minstens drie van vier\" in de hoofdanalyse.")
A("")
A("| rivier | locatie | per. | variabele | n | richting | tau strikt | tau ref. | ook sterk in ref. |")
A("|---|---|---|---|---|---|---|---|---|")
for c, ns, d in sterk_s:
    tr = dep_r.get(c)
    A(f"| {c[0]} | {c[1]} | {PER_NL[c[2]]} | {PAIR_NL[c[3]]} | {d['n_events']} | "
      f"{'verhoogt' if float(d['tau'])>0 else 'verlaagt'} | {float(d['tau']):+.3f} | "
      f"{float(tr['tau']):+.3f} | {'ja' if c in sterk_r else 'nee'} |" if tr else
      f"| {c[0]} | {c[1]} | {PER_NL[c[2]]} | {PAIR_NL[c[3]]} | {d['n_events']} | "
      f"{'verhoogt' if float(d['tau'])>0 else 'verlaagt'} | {float(d['tau']):+.3f} | n.v.t. | nee |")
A("")
verloren = [c for c in sterk_r if c not in {s[0] for s in sterk_s}]
A(f"Van de {len(sterk_r)} cellen die in de referentie sterk waren, blijven er")
A(f"{len(sterk_r)-len(verloren)} sterk onder strikt en vallen er {len(verloren)} weg.")
if verloren:
    A("Weggevallen: " + "; ".join(f"{c[0]} {c[1]} P{PER_NL[c[2]]} {PAIR_NL[c[3]]}" for c in sorted(verloren)) + ".")
A("")
A("Dat wegvallen is grotendeels een kwestie van macht, niet van richting: met half")
A("zoveel events is een even sterke samenhang moeilijker van toeval te onderscheiden.")
A("De tau-waardes zelf, zie de figuur, verschuiven weinig.")
A("")
A(fig(f"{FIG}/strict_tau_compare.png",
      "Figuur 2. Kendall's tau per cel, referentie (horizontaal) tegen strikt (verticaal). "
      "Gekleurd: cellen die in minstens een van beide analyses sterk zijn. De richting blijft "
      "in vrijwel alle cellen gelijk; de spreiding rond de diagonaal is het effect van de "
      "kleinere steekproef."))
A("")

# ------------------------------------------------------------------ 6
A("## 6. De intervallen onder strikt")
A("")
if heeft_bs:
    br_s = np.array([float(r["median_width_minor"]) for r in diag_s.values()])
    br_r = np.array([float(r["median_width_minor"]) for r in diag_r.values()])
    A(f"Mediane intervalbreedte rond de milde curve: referentie {np.median(br_r):.3f},")
    A(f"strikt {np.median(br_s):.3f}. Breder, zoals verwacht bij half zoveel events.")
    A("")
    A("Waar sluit het interval nul uit, elk op zijn eigen floodniveau:")
    A("")
    A("| grootheid | referentie bij 0,6915 | strikt bij 0,8413 |")
    A("|---|---|---|")
    for q, lab in (("marginal_part", "marginaal deel"), ("diff_resel", "zwaar min mild"),
                   ("copula_part", "copula-deel (mild)")):
        pr, nr, tr_ = sluit_uit(ci_r, q, 69); ps, ns_, ts = sluit_uit(ci_s, q, 84)
        A(f"| {lab} | boven {pr}, onder {nr}, van {tr_} | boven {ps}, onder {ns_}, van {ts} |")
    A("")
    A("Bij strikt is \"zwaar min mild\" de informatieve grootheid: mild is daar de")
    A("onafhankelijkheidslijn, dus dit verschil is precies het copula-deel van de zware")
    A("curve.")
    A("")
    A("### Ebro en Po onder strikt, bij 0,8413")
    A("")
    A("| rivier | locatie | per. | variabele | n | k_maj | zwaar min mild | toetsen <0,05 |")
    A("|---|---|---|---|---|---|---|---|")
    for c in sorted(diag_s):
        if c[0] not in ("Po", "Ebro"):
            continue
        d = diag_s[c]
        A(f"| {c[0]} | {c[1]} | {PER_NL[c[2]]} | {PAIR_NL[c[3]]} | {d['n_events']} | {d['k_major']} | "
          f"{fmt_ci(ci_s, c, 'diff_resel', 84)} | {n_toetsen(dep_s.get(c))}/3 |")
    A("")
    A(fig(f"{FIG}/strict_per_river_diff.png",
          "Figuur 3. Per rivier het verschil zwaar min mild met 95 procent band, referentie op "
          "0,5 (blauw) en strikt op 1,0 (oranje), mediaan over de cellen van die rivier."))
else:
    A("*De strikte bootstrap was nog niet klaar toen dit rapport werd gemaakt.*")
A("")

# ------------------------------------------------------------------ 7
A("## 7. Verhouding tot de gepubliceerde resultaten en tot de hoofdanalyse")
A("")
A("**De as-correctie staat los van de drempel.** Ook onder strikt liggen de")
A("conditionele curves op of boven de unconditionele. De omkering van de")
A("gepubliceerde hoofdbevinding is dus geen artefact van de keuze 0,5.")
A("")
A("**Het marginale verschijnsel draait om.** Na een milde droogte (0,5) is het natter")
A("dan op een willekeurig moment, na een strenge droogte (1,0) droger. Sectie 3.1 laat")
A("zien dat dit grotendeels een definitiekwestie is: het einde van een strenge droogte")
A("laat de rivier nog in milde droogte achter. Voor de tekst betekent dit dat de zin")
A("\"conditioneren op een droogte verhoogt de kans licht\" alleen geldt bij de")
A("drempel van de hoofdanalyse en expliciet aan die drempel gekoppeld moet worden.")
A("")
A("**De severity-afhankelijkheid wordt dunner, niet anders.** De richting per cel")
A("blijft, de tau's schuiven weinig, maar met half zoveel events overleven minder cellen")
A("de toetsen. De clusters uit de hoofdanalyse, positief in het zuiden en negatief bij")
A("Vistula en Weser, zijn te herkennen in de tabel van sectie 5.")
A("")
A("**Wat strikt kost.** De grenzen voor mild en zwaar uit pagina 22 passen niet bij een")
A("droogtedrempel van 1: mild valt samen met alles. Wie de strenge definitie wil")
A("rapporteren moet die grenzen opnieuw kiezen, bijvoorbeeld 1,5 en 2, en dat is een")
A("methodekeuze die in de tekst moet. Daarnaast verdwijnen meer cellen onder de grens")
A("van vijftien events en wordt de Dnieper nog dunner.")
A("")
A("**Wat strikt oplevert.** Een schonere scheiding tussen droogte- en floodweken, en")
A("een zware curve die echt over zware droogtes gaat, SRI onder -2. Voor het antwoord")
A("aan Reviewer #4 over de drempelkeuze is dit een bruikbare robuustheidscontrole: de")
A("kern van het verhaal hangt niet aan 0,5.")
A("")
A("Of de gerapporteerde analyse op 0,5 blijft staan of naar 1,0 gaat, is een besluit")
A("voor Floris. Dit document geeft de cijfers voor beide, niet de keuze.")
A("")
A("## 8. Beperkingen")
A("")
A("1. De X-grenzen zijn ongewijzigd, waardoor de milde curve bij strikt degenereert.")
A("2. Minder events per cel: bredere intervallen, minder macht, meer cellen zonder")
A("   zware curve of zonder bootstrap.")
A("3. De flooddrempel zit niet in de copula-berekening; de spiegeling raakt alleen het")
A("   afleesniveau. Voor de ECA-kant geldt dat anders, zie het gevoeligheidsraster.")
A("4. Alle overige beperkingen van de hoofdanalyse gelden onverkort.")
A("")
A("## 9. Bronnen")
A("")
A("`scripts/27_strict_definition_points.py`, `scripts/28_strict_bootstrap_and_tests.py`,")
A("`scripts/29_strict_report_pdf.py`. Resultaten in de vier mappen met `strict` in de")
A("naam plus de twee referentiemappen van 2 september. Geen bestaande code gewijzigd;")
A("script 28 importeert de functies van scripts 22 en 25 en overschrijft alleen de")
A("drempelconstante.")

# ------------------------------------------------------------------ figuren
# figuur 1
fig1, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), constrained_layout=True)
ax = axes[0]
sr = [float(r["share_drought_weeks_also_flood"]) for r in ov_r if r["share_drought_weeks_also_flood"]]
ss = [float(r["share_drought_weeks_also_flood"]) for r in ov_s if r["share_drought_weeks_also_flood"]]
ax.hist(sr, bins=20, alpha=0.7, color=BLUE, label="Threshold 0.5 / 0.6915")
ax.hist(ss, bins=20, alpha=0.7, color=ORANGE, label="Threshold 1.0 / 0.8413")
ax.set_xlabel("Share of drought weeks that are also flood weeks"); ax.set_ylabel("Location-periods")
ax.legend(fontsize=9); ax.grid(alpha=0.3)
ax = axes[1]
key = lambda r: cel(r)
nr_map = {key(r): int(r["n_events"]) for r in ref}; ns_map = {key(r): int(r["n_events"]) for r in stk}
common = sorted(set(nr_map) & set(ns_map))
ax.scatter([nr_map[c] for c in common], [ns_map[c] for c in common], s=14, color=GREY, alpha=0.7)
m = max(max(nr_map.values()), 1); ax.plot([0, m], [0, m], color="black", lw=0.8, ls="--")
ax.plot([0, m], [0, m / 2], color="black", lw=0.6, ls=":"); ax.text(m * 0.7, m * 0.31, "half", fontsize=8)
ax.set_xlabel("Drought events per cell, threshold 0.5"); ax.set_ylabel("Drought events per cell, threshold 1.0")
ax.grid(alpha=0.3)
fig1.savefig(f"{FIG}/strict_overlap_events.png", dpi=170, facecolor="white"); plt.close(fig1)

# figuur 2
fig2, ax = plt.subplots(figsize=(7.2, 6.6), constrained_layout=True)
sterk_set = {s[0] for s in sterk_s} | sterk_r
for c in sorted(set(dep_r) & set(dep_s)):
    tr, ts = float(dep_r[c]["tau"]), float(dep_s[c]["tau"])
    st = c in sterk_set
    ax.scatter(tr, ts, s=40 if st else 12, color=(RED if ts < 0 else GREEN) if st else GREY,
               alpha=0.9 if st else 0.4, zorder=3 if st else 2)
    if st:
        ax.annotate(f"{c[0]} {c[1][:10]} P{PER_NL[c[2]]}", (tr, ts), fontsize=6.5,
                    xytext=(4, 2), textcoords="offset points")
lim = 0.45
ax.plot([-lim, lim], [-lim, lim], color="black", lw=0.8, ls="--")
ax.axhline(0, color="black", lw=0.6); ax.axvline(0, color="black", lw=0.6)
ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
ax.set_xlabel("Kendall's tau, threshold 0.5"); ax.set_ylabel("Kendall's tau, threshold 1.0")
ax.grid(alpha=0.3)
fig2.savefig(f"{FIG}/strict_tau_compare.png", dpi=170, facecolor="white"); plt.close(fig2)

# figuur 3
if heeft_bs:
    rivers = []
    for c in sorted(diag_r):
        if c[0] not in rivers:
            rivers.append(c[0])
    Yg = np.linspace(0, 1, 101)
    fig3, axes = plt.subplots(4, 4, figsize=(16, 13), sharex=True, sharey=True, constrained_layout=True)
    for ax, riv in zip(axes.ravel(), rivers):
        for ci, colour in ((ci_r, BLUE), (ci_s, ORANGE)):
            cs_ = [k[:4] for k in ci if k[0] == riv and k[4] == "diff_resel" and k[5] == "point"]
            if not cs_:
                continue
            P = np.array([ci[c + ("diff_resel", "point")] for c in cs_])
            LO = np.array([ci[c + ("diff_resel", "lo")] for c in cs_])
            HI = np.array([ci[c + ("diff_resel", "hi")] for c in cs_])
            ax.plot(Yg, np.nanmedian(P, axis=0), color=colour, lw=2)
            ax.fill_between(Yg, np.nanmedian(LO, axis=0), np.nanmedian(HI, axis=0), color=colour, alpha=0.18)
        ax.axhline(0, color="black", lw=1); ax.set_title(riv, fontsize=11); ax.set_xlim(0, 1); ax.grid(alpha=0.3)
    for ax in axes[-1, :]:
        ax.set_xlabel("Future flood quantile", fontsize=10)
    for ax in axes[:, 0]:
        ax.set_ylabel("Severe minus minor drought", fontsize=10)
    fig3.savefig(f"{FIG}/strict_per_river_diff.png", dpi=150, facecolor="white"); plt.close(fig3)

# ------------------------------------------------------------------ schrijven
md_text = "\n".join(L) + "\n"
open(f"{OUT}/report.md", "w").write(md_text)
html_body = markdown.markdown(md_text, extensions=["tables"])
css = """
@page { size: A4; margin: 2.0cm 2.0cm 2.2cm 2.0cm;
        @frame footer { -pdf-frame-content: footer; bottom: 0.8cm; margin-left: 2cm; margin-right: 2cm; height: 0.8cm; } }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10.2pt; line-height: 1.38; color: #111; }
h1 { font-size: 19pt; margin: 0 0 4pt 0; } h2 { font-size: 14pt; margin: 20pt 0 6pt 0; border-bottom: 1px solid #999; padding-bottom: 2pt; }
h3 { font-size: 11.5pt; margin: 14pt 0 4pt 0; } p { margin: 0 0 7pt 0; text-align: justify; }
table { width: 100%; margin: 6pt 0 10pt 0; font-size: 8.4pt; } th, td { border: 1px solid #bbb; padding: 3pt 4pt; text-align: left; vertical-align: top; }
th { background: #e8e8e8; } code { font-family: Courier, monospace; font-size: 9pt; }
.fig { margin: 10pt 0 12pt 0; text-align: center; } .fig img { width: 16.5cm; } .cap { font-size: 8.8pt; color: #333; text-align: left; margin: 4pt 0 0 0; }
#footer { font-size: 8pt; color: #666; text-align: right; }
"""
html = (f'<html><head><meta charset="utf-8"><style>{css}</style></head><body>{html_body}'
        f'<div id="footer">Strikte definities, gevoeligheidsvariant, 4 september 2026, pagina <pdf:pagenumber/></div></body></html>')
with open(f"{OUT}/report.pdf", "wb") as fh:
    status = pisa.CreatePDF(html, dest=fh, encoding="utf-8")
print(f"geschreven: {OUT}/report.md ({len(L)} regels), report.pdf, fouten {status.err}", flush=True)
