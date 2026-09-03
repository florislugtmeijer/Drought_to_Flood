"""T-11: het uitlegdocument over de copula-analyse, als PDF.

Voor Floris. Legt de volledige analyse van het tweede deel van het artikel uit,
de copula-gebaseerde transitiekansen: wat de gepubliceerde methode is, wat er in
de code anders bleek, wat er is herberekend, hoe de gevoeligheidsvarianten en de
bootstrap werken, welke toetsen zijn gebruikt en hoe ze werken, en hoe de uitkomst
zich verhoudt tot de gepubliceerde resultaten.

Rekent niets opnieuw. Alle cijfers die uit de gerepareerde runs komen worden hier
uit de CSV's gelezen. Cijfers die uit runs van voor de reparatie van de
einddetectie stammen staan expliciet zo gelabeld.

Uitvoer: results/2026-09-03_copula_method_report/report.md en report.pdf

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with markdown --with xhtml2pdf --no-project \
      python scripts/26_method_report_pdf.py
"""
import csv, os, collections
import numpy as np
import markdown
from xhtml2pdf import pisa

ROOT = os.getcwd()
BS = "results/2026-09-02_copula_bootstrap"
DEP = "results/2026-09-02_dependence_tests/dependence_tests.csv"
COR = "results/2026-09-02_copula_corrected"
VAR = "results/2026-09-02_copula_definition_variants"
OUT = "results/2026-09-03_copula_method_report"
os.makedirs(OUT, exist_ok=True)
Y = np.linspace(0, 1, 101)
YC = [f"y_{i:03d}" for i in range(101)]
QM = 69
PAIR_NL = {"drought_peak": "drought peak", "mean_drought_severity": "mean severity"}
PER_NL = {"first": "1", "second": "2"}
KOLS = ("tau_p", "hoeffd_p", "aic_perm_p", "cp_q6915_p")

# ------------------------------------------------------------------ inlezen
ci = {}
for r in csv.DictReader(open(f"{BS}/transition_ci.csv")):
    ci[(r["river"], r["village"], r["period"], r["pair"], r["scheme"], r["quantity"],
        r["kind"])] = np.array([float(r[c]) for c in YC])
diag = {(r["river"], r["village"], r["period"], r["pair"], r["scheme"]): r
        for r in csv.DictReader(open(f"{BS}/bootstrap_diagnostics.csv"))}
dep = {(r["river"], r["village"], r["period"], r["pair"]): r
       for r in csv.DictReader(open(DEP))}
cellen = sorted({k[:4] for k in ci if k[4] == "iid"})
iid = [diag[c + ("iid",)] for c in cellen if c + ("iid",) in diag]


def w(cel, q, soort, j=QM):
    k = cel + ("iid", q, soort)
    return float(ci[k][j]) if k in ci else np.nan


def fmt_ci(cel, q, j=QM):
    p, lo, hi = w(cel, q, "point", j), w(cel, q, "lo", j), w(cel, q, "hi", j)
    if not np.isfinite(p):
        return "geen"
    ster = "**" if (lo > 0 or hi < 0) else ""
    return f"{ster}{p:+.3f}{ster} [{lo:+.3f}, {hi:+.3f}]"


def n_toetsen(cel):
    d = dep.get(cel)
    return (sum(1 for k in KOLS if float(d[k]) < 0.05) if d else 0), d


# gerepareerde kerncijfers bij q = 0,69
minor = np.array([w(c, "minor_resel", "point") for c in cellen])
marg = np.array([w(c, "marginal_part", "point") for c in cellen])
cop = np.array([w(c, "copula_part", "point") for c in cellen])
ok = np.isfinite(minor) & np.isfinite(marg) & np.isfinite(cop)
gap = marg + cop
uncond = minor - gap
n_ok = int(ok.sum())
med_minor, med_uncond, med_gap = (np.median(minor[ok]), np.median(uncond[ok]),
                                  np.median(gap[ok]))
n_onder = int(np.sum(gap[ok] < 0))
med_marg, med_cop = np.median(marg[ok]), np.median(cop[ok])

taus = np.array([float(dep[c]["tau"]) for c in cellen if c in dep])
sterk = [(c,) + n_toetsen(c) for c in cellen if n_toetsen(c)[0] >= 3]
sterk.sort(key=lambda x: -abs(float(x[2]["tau"])))
cnt_fam = collections.Counter(r["copula_point"] for r in iid)
sh = np.array([float(r["modal_share"]) for r in iid])
nf = np.array([int(r["n_families_seen"]) for r in iid])
same = sum(1 for r in iid if r["copula_point"] == r["copula_modal"])
br = np.array([float(r["median_width_minor"]) for r in iid])
fails = np.array([int(r["failed_replicates"]) for r in iid])
bias = np.array([float(r["median_bias"]) for r in iid])
supt = np.array([float(r["supt_over_196"]) for r in iid])
lag = np.array([abs(float(r["lag1_spearman_drought"])) for r in iid
                if r["lag1_spearman_drought"] not in ("", "nan")])
ratio = np.array([float(diag[(r["river"], r["village"], r["period"], r["pair"], "block")]
                        ["median_width_minor"]) / float(r["median_width_minor"])
                  for r in iid if float(r["median_width_minor"]) > 0
                  and (r["river"], r["village"], r["period"], r["pair"], "block") in diag])


def telling(kol):
    ps = [float(dep[c][kol]) for c in cellen if c in dep]
    return sum(1 for p in ps if p < 0.05), len(ps)


def sluit_uit(q, j=QM):
    p = n = t = 0
    for c in cellen:
        lo, hi = w(c, q, "lo", j), w(c, q, "hi", j)
        if not (np.isfinite(lo) and np.isfinite(hi)):
            continue
        t += 1
        p += lo > 0
        n += hi < 0
    return p, n, t


def fig(pad, caption):
    return f'\n<div class="fig"><img src="{ROOT}/{pad}" /><p class="cap">{caption}</p></div>\n'


L = []
A = L.append

A("# De copula-analyse van drought-to-flood transities")
A("## Methode, herberekening, en hoe de uitkomst zich verhoudt tot wat is gepubliceerd")
A("")
A("*Intern werkdocument bij de revisie van HYDROL79380R1, 3 september 2026. Alle")
A("cijfers komen uit de resultaatbestanden in `results/`, de scripts staan in de")
A("repository. Cijfers uit runs van vóór de reparatie van de einddetectie zijn zo")
A("gelabeld.*")
A("")

# ================================================================== 0
A("## 0. Waar dit document over gaat")
A("")
A("Het artikel heeft twee delen. Het eerste, de event coincidence analysis, vraagt of")
A("floods vaker kort na een droogte optreden dan het toeval voorspelt. Het tweede, de")
A("copula-analyse, vraagt iets anders: als er een droogte is geweest, hangt de hoogte")
A("van de piek erna dan samen met hoe zwaar die droogte was. Dit document gaat over")
A("dat tweede deel.")
A("")
A("Reviewer #4 vroeg twee dingen die er niet waren: welke copula per locatie is gekozen,")
A("en betrouwbaarheidsintervallen bij de transitiekansen. Het uitwerken daarvan bracht")
A("een aantal fouten in de code aan het licht, waarna de hele keten opnieuw is berekend.")
A("Dit document legt uit wat er is gedaan, hoe elke stap werkt, en wat er van de")
A("gepubliceerde bevindingen overeind blijft.")
A("")
A("Kort: de zwaarste fout, een ontbrekende stap in de formule op pagina 21, draait de")
A("hoofdbevinding van het tweede deel om. Wat overblijft is enerzijds een breed maar")
A("mild verschijnsel, het venster na een droogte is natter dan een willekeurig venster,")
A("en anderzijds een klein aantal locaties waar de zwaarte van de droogte er echt toe")
A("doet, in twee richtingen. De locaties die het artikel uitlicht, Po en Ebro, horen")
A("daarbij, met sterker bewijs dan het artikel nu geeft.")
A("")

# ================================================================== 1
A("## 1. De gepubliceerde methode, in gewone taal")
A("")
A("Per locatie en per periode van vijftien jaar gebeurt dit.")
A("")
A("**Droogtes vinden.** Uit de wekelijkse afvoer wordt een gestandaardiseerde")
A("afvoerindex berekend, de SRI. Een droogte begint als de SRI onder -0,5 zakt en duurt")
A("tot hij er weer boven komt. Van elke droogte worden twee kenmerken bewaard: de")
A("*drought peak*, de diepste SRI-waarde, en de *mean severity*, het totale tekort")
A("gedeeld door de duur.")
A("")
A("**De flood erna meten.** Voor elke droogte wordt gekeken naar de vier weken na")
A("afloop, en daaruit wordt de hoogste weekpiek genomen, uitgedrukt als quantiel van")
A("de afvoer op die locatie. Een waarde van 0,95 betekent een piek die daar maar vijf")
A("procent van de tijd wordt overschreden.")
A("")
A("**De samenhang modelleren met een copula.** Een copula beschrijft hoe twee")
A("grootheden samenhangen, los van hun eigen verdelingen. Het werkt met rangnummers:")
A("alle droogtes op volgorde van zwaarte, alle pieken op volgorde van hoogte, en de")
A("copula zegt hoe die twee ranglijsten met elkaar samenhangen. Het artikel probeert")
A("vijftien copulafamilies en kiest per locatie de beste met het AIC-criterium.")
A("")
A("**De transitiekans uitrekenen.** Pagina 21 geeft de formule:")
A("")
A("> P(Y > y | X ≥ x) = [1 − F_X(x) − F_Y(y) + C(F_X(x), F_Y(y))] / [1 − F_X(x)]")
A("")
A("In woorden: de kans dat de piek boven niveau y komt, gegeven dat de droogte")
A("minstens zwaarte x had. F_X en F_Y zijn de marginale verdelingen, die de ruwe")
A("waardes x en y vertalen naar de rangschaal waar de copula C op werkt. Het artikel")
A("rekent dit uit voor twee droogteniveaus, mild en zwaar, en tekent daarnaast een")
A("*unconditionele* curve, de kans op een piek boven y in een willekeurig venster van")
A("vier weken, als referentie.")
A("")

# ================================================================== 2
A("## 2. Wat er in de code anders was dan beschreven")
A("")
A("De code die de gepubliceerde figuren maakte, is regel voor regel vergeleken met de")
A("beschrijving. Vijf afwijkingen hadden effect op de cijfers.")
A("")
A("### 2.1 De stap F_Y ontbrak, en daardoor stonden twee curves op verschillende assen")
A("")
A("De code stopte de floodwaarde y rechtstreeks in de copula, zonder de vertaling")
A("F_Y(y) naar de rangschaal. Omdat de copula per constructie met rangen werkt, stond")
A("de conditionele curve daardoor op de as \"rang van de piek binnen de post-droogte")
A("pieken\", terwijl de unconditionele curve op de as \"runoff-quantiel\" stond. Beide")
A("werden op dezelfde x-as getekend, met als label \"Future flood quantile value\".")
A("")
A("Dat maakt uit omdat post-droogte pieken hoog zijn: hun mediaan ligt rond quantiel")
A("0,87. De mediane post-droogte piek, rang 0,5, werd dus getekend op de plek waar de")
A("unconditionele curve quantiel 0,50 laat zien. De conditionele curve stond daardoor")
A("over de hele breedte te ver naar links en dus onder de unconditionele. Dat is de")
A("bevinding waar het artikel op leunt: conditioneren op droogte verlaagt de floodkans.")
A("")
A("De regel die het oplost, `prob_flood = dist2.cdf(Y, *params2)`, stond al in de code.")
A("Hij werd berekend en nergens gebruikt. Dat verklaart meteen een tweede bevinding,")
A("dat de gefitte marginale verdelingen, die pagina 21 wel beschrijft, in de code")
A("nergens in doorwerkten.")
A("")
A("**Omvang, gemeten op de definities van vóór de eindtijdreparatie:** bij het")
A("floodniveau van het manuscript, quantiel 0,69, ging de transitiekans na een milde")
A("droogte van mediaan 0,274 naar 0,775 zodra beide curves op dezelfde as werden gezet.")
A("Het aantal cellen waar de conditionele curve onder de unconditionele lag ging van 188")
A("van de 192 naar 33.")
A("")
A(fig(f"{COR}/figures/three_presentations.png",
      "Figuur 1. Dezelfde cel, Ebro bij Tudela in periode 2, in drie weergaves. Links zoals "
      "gepubliceerd: conditionele curves op de rangschaal, unconditionele op de quantielschaal. "
      "Midden: de conditionele curves omgerekend naar de quantielschaal via F_Y. Rechts: "
      "andersom, de unconditionele lijn omgerekend naar de rangschaal. Beide reparaties geven "
      "dezelfde conclusie: de conditionele curves liggen op of boven de unconditionele. "
      "Definities van vóór de eindtijdreparatie; het patroon is structureel."))
A("")
A("### 2.2 Het floodvenster telde de laatste droogteweek mee")
A("")
A("Het venster voor de piek na de droogte begon op de laatste week van de droogte")
A("zelf en liep tot vier weken later, aan beide kanten inclusief. Dat zijn vijf weken,")
A("waarvan de eerste nog droogte is. Het manuscript zegt \"within four weeks after a")
A("drought ends\". De unconditionele curve gebruikte wel vier weken zonder de eigen")
A("week, dus de twee kanten waren ook onderling ongelijk. Gerepareerd naar vier weken")
A("strikt na afloop.")
A("")
A("### 2.3 De duur was een week te kort")
A("")
A("De *mean severity* deelt het totale tekort door de duur, en die duur was einde min")
A("begin. Een droogte van twee weken werd door 1 gedeeld. Gerepareerd naar het aantal")
A("weken.")
A("")
A("### 2.4 Het einde van eenweekse droogtes lag een week te laat")
A("")
A("Deze fout is gevonden in een parallelle review van de ECA-keten. De einddetectie")
A("eiste dat het einde ná de start lag, waardoor bij een droogte van precies één week")
A("de eigen week werd overgeslagen en het einde doorschoof naar het volgende gat.")
A("Ongeveer een derde van alle droogtes duurt één week. Het floodvenster begon daar")
A("dus een week te laat, precies de week waar de samenhang het sterkst zit.")
A("")
A("Voor de ECA leverde de reparatie 15,5 procent meer coïncidenties op en steeg de")
A("gepoolde ratio van 1,59 naar 1,82. Voor de copula-kant bleek hetzelfde: op de oude")
A("definities haalde de Ebro in geen enkele toets significantie, op de gerepareerde is")
A("het het sterkste punt van de kaart, zie sectie 8.")
A("")
A("### 2.5 Kleinere punten")
A("")
A("De berekening had geen vaste seed, dus de gepubliceerde curves waren niet exact")
A("reproduceerbaar. Het argument `flood_score = 0.9` voedde alleen een grootheid die")
A("nergens werd gelezen. Het oppervlak in de eerste figuur gebruikte een tien keer")
A("kleinere trekking dan de curves. En de trekker van het copula-package geeft bij de")
A("Joe-familie een klein aandeel niet-eindige waardes, die stil wegvielen. Alles")
A("gerepareerd in `src/dtf/copula.py`, met de afwijkingen van de bron gemarkeerd.")
A("")

# ================================================================== 3
A("## 3. De herberekening en de vier besluiten")
A("")
A("Vier keuzes zijn door Floris genomen, na doorrekening van beide varianten:")
A("")
A("1. De conditionele curve wordt afgelezen op F_Y(q), zodat hij dezelfde vraag")
A("   beantwoordt als de unconditionele curve. Dit is geen methodewijziging maar het")
A("   uitvoeren van de formule zoals pagina 21 hem al geeft.")
A("2. Het floodvenster is vier weken strikt na afloop.")
A("3. De duur is het aantal weken.")
A("4. De marginale verdelingen F_X en F_Y zijn parametrisch, uit de gefitte")
A("   verdelingen, zoals pagina 21 beschrijft. De empirische variant is ernaast gelegd")
A("   en verschilt mediaan 0,03; het beeld is hetzelfde.")
A("")
A("Op de gerepareerde definities, alle cellen bij quantiel 0,69:")
A("")
A(f"| | mediaan over {n_ok} cellen |")
A("|---|---|")
A(f"| transitiekans na een milde droogte | {med_minor:.3f} |")
A(f"| unconditionele kans | {med_uncond:.3f} |")
A(f"| verschil | {med_gap:+.3f} |")
A(f"| cellen met conditioneel onder unconditioneel | {n_onder} van {n_ok} |")
A("")
A("### 3.1 De opsplitsing: wat is marginaal, wat is copula")
A("")
A("Het verschil tussen de conditionele en de unconditionele curve valt exact in twee")
A("stukken uiteen, en dat onderscheid is de rode draad van dit document.")
A("")
A("> verschil = [ (1 − F_Y) − unconditioneel ] + [ conditioneel − (1 − F_Y) ]")
A("")
A("Het eerste stuk is het **marginale deel**. De curve 1 − F_Y is de overschrijdingskans")
A("van de post-droogte pieken zonder enige conditionering op zwaarte. Vergeleken met de")
A("unconditionele curve zegt dit: is het venster na een droogte natter dan een")
A("willekeurig venster. Daar is geen copula voor nodig.")
A("")
A("Het tweede stuk is het **copula-deel**. Bij volledige onafhankelijkheid tussen")
A("zwaarte en piek is de conditionele curve exact gelijk aan 1 − F_Y, dus dit stuk is")
A("dan nul. Alles wat hier overblijft is de bijdrage van de zwaarte van de droogte, en")
A("dat is precies wat het copula-raamwerk beoogt te meten.")
A("")
A(f"Mediaan over alle cellen bij 0,69: marginaal deel {med_marg:+.3f}, copula-deel")
A(f"{med_cop:+.3f}. Het breedste verschijnsel is dus het marginale. Het copula-deel is")
A("in het geheel klein, en waar het wel groot is, staat in sectie 8.")
A("")
A(fig(f"{COR}/figures/corrected_overview.png",
      "Figuur 2. Alle zestien rivieren, mediaan per rivier. Gestippeld: de gepubliceerde "
      "aflezing. Doorgetrokken: gecorrigeerd. Oranje: unconditioneel. Grijs gestippeld: de "
      "onafhankelijkheidslijn 1 − F_Y. De afstand grijs–oranje is het marginale deel, de "
      "afstand doorgetrokken–grijs is het copula-deel. Definities van vóór de eindtijdreparatie."))
A("")

# ================================================================== 4
A("## 4. Gevoeligheid van de copula-kant")
A("")
A("Drie gevoeligheidsvragen zijn doorgerekend, telkens over alle cellen.")
A("")
A("**De definitiekeuzes** uit sectie 2.2 en 2.3, elk apart en samen. Het floodvenster")
A("verschoof de conditionele curve met mediaan 0,010 en maximaal 0,40, en liet de")
A("gekozen copulafamilie in 30 van de 96 locatie-periodes omslaan. De duur verschoof")
A("mean severity met mediaan 0,033 en liet de familie in 36 van de 96 omslaan. Geen van")
A("beide veranderde de conclusie over de as uit sectie 2.1. Cijfers van vóór de")
A("eindtijdreparatie.")
A("")
A("**Parametrische tegen empirische marginalen.** Mediaan absoluut verschil 0,03, geen")
A("systematische richting. Eén echt verschil: waar geen enkele droogte boven de zware")
A("drempel ligt, weigert de parametrische route een zware curve te geven, terwijl de")
A("empirische route er een maakt uit de staart van een gesimuleerde copula op nul")
A("waarnemingen. Dat pleit voor parametrisch.")
A("")
A("**De as-omrekening in twee richtingen.** De conditionele curve naar de")
A("quantielschaal halen, of de unconditionele naar de rangschaal. Beide geven exact")
A("hetzelfde verschil waar F_Y omkeerbaar is. Ze lopen alleen uiteen onder het laagste")
A("quantiel dat post-droogte pieken halen, ongeveer 0,3, omdat daar geen rang voor")
A("bestaat. De quantielschaal is gekozen omdat hij het volledige floodbereik toont en")
A("aansluit bij de rest van het artikel.")
A("")
A("**De stabiliteit van de copulakeuze** is een vierde gevoeligheid, en de belangrijkste.")
A("Het AIC-verschil met de op één na beste familie lag, vóór de eindtijdreparatie, in")
A("175 van de 192 cellen onder 2, de gangbare grens waaronder geen onderscheid gemaakt")
A("kan worden. Sectie 6 kwantificeert dit met de bootstrap.")
A("")

# ================================================================== 5
A("## 5. De bootstrap, stap voor stap")
A("")
A("### 5.1 De vraag die een betrouwbaarheidsinterval beantwoordt")
A("")
A("Per cel, dus per combinatie van locatie, periode en droogtekenmerk, hebben we")
A("ongeveer negentig droogtes. Uit die negentig komt één transitiecurve. De vraag is:")
A("als de natuur ons toevallig negentig andere droogtes had gegeven, hoe anders had die")
A("curve er dan uitgezien. Dat is wat het interval uitdrukt.")
A("")
A("### 5.2 Hoe de bootstrap dat nabootst")
A("")
A("We hebben geen tweede steekproef, maar we kunnen er een nabootsen. Uit de negentig")
A("waargenomen paren, elk paar is één droogte met zijn zwaarte en zijn piek erna,")
A("trekken we negentig keer een paar *met teruglegging*. Sommige droogtes komen twee of")
A("drie keer voor, andere niet. Zo'n hertrokken set gedraagt zich als een nieuwe")
A("steekproef uit dezelfde populatie.")
A("")
A("Op elke hertrokken set wordt **de volledige berekening opnieuw gedaan**: de")
A("parameters van de marginale verdelingen, de rangtransformatie, de keuze van de")
A("copulafamilie met AIC over vijftien kandidaten, de drempels voor mild en zwaar, en")
A("de curves. Dat herhalen we 2000 keer. Van de 2000 uitkomsten nemen we per punt op de")
A("curve het 2,5e en het 97,5e percentiel. Dat zijn de grenzen van het interval.")
A("")
A("### 5.3 Keuzes en waarom")
A("")
A("**Herselectie van de copulafamilie per replicatie.** Als de familie wordt vastgezet,")
A("doet het interval alsof we zeker weten welke familie klopt, en dat weten we juist")
A("niet. Herselecteren neemt die onzekerheid mee. Ter diagnose is de vastgezette")
A("variant op één locatie per rivier ernaast berekend.")
A("")
A("**De marginale verdelingsfamilie eenmaal gekozen, de parameters per replicatie")
A("opnieuw geschat.** Volledige herselectie uit tien verdelingen per replicatie kost")
A("vier keer zoveel rekentijd, en de keuze van een verdelingsfamilie is een modelkeuze,")
A("geen schatting.")
A("")
A("**Het verschil tussen zwaar en mild apart gebootstrapt.** De twee curves komen uit")
A("dezelfde replicatie en zijn sterk gecorreleerd. Twee overlappende intervallen")
A("bewijzen daarom niet dat het verschil nul kan zijn. Het verschil krijgt zijn eigen")
A("interval uit dezelfde 2000 replicaties.")
A("")
A("**Percentiel-intervallen, geen BCa.** Een biascorrectie duwt de benodigde")
A("percentielen ver de staart in, waar 2000 replicaties te weinig zijn, en met")
A("herselectie is de schatter een keuze uit vijftien families en dus niet glad, waardoor")
A(f"de correctie op drijfzand staat. De mediane bias is gemeten: {np.median(bias):+.4f},")
A(f"uitersten {bias.min():+.4f} en {bias.max():+.4f}. Nagenoeg gecentreerd, dus")
A("percentielen volstaan.")
A("")
A("**Puntsgewijs.** Elk punt op de curve heeft zijn eigen interval met 95 procent")
A("dekking. Een band die over alle 101 punten tegelijk geldt zou mediaan")
A(f"{(np.median(supt)-1)*100:.0f} procent breder zijn. De reviewer vraagt om")
A("intervallen, puntsgewijs is wat daarbij hoort, en de verhouding is gerapporteerd.")
A("")
A("**Niets weggegooid op grond van de uitkomst.** Een replicatie die extreem uitvalt is")
A("precies waar het interval over gaat. Mislukte fits worden geteld:")
A(f"mediaan {int(np.median(fails))} van de 2000, maximum {fails.max()}.")
A("")
A("**Vaste seed per cel.** Elke cel heeft een eigen, afleidbare toevalsstroom, zodat de")
A("run exact herhaalbaar is.")
A("")
A("### 5.4 Controle op seriële afhankelijkheid: de blokbootstrap")
A("")
A("Droogtes volgen elkaar op in de tijd en zijn niet volledig los van elkaar. De gewone")
A("bootstrap doet alsof ze dat wel zijn. Als controle is een *circulaire blokbootstrap*")
A("gedraaid: in plaats van losse droogtes worden aaneengesloten blokjes van")
A("opeenvolgende droogtes getrokken, met bloklengte de derdemachtswortel van het")
A("aantal events, dus ongeveer vier. Blijft er samenhang tussen opeenvolgende droogtes")
A("bestaan, dan worden de intervallen breder.")
A("")
A(f"Gemeten: de correlatie tussen opeenvolgende droogtes heeft mediaan {np.median(lag):.3f}")
A(f"in absolute waarde. De blokbootstrap geeft intervallen die mediaan {np.median(ratio):.2f}")
A(f"keer zo breed zijn als de gewone, kwartielen {np.percentile(ratio,25):.2f} en")
A(f"{np.percentile(ratio,75):.2f}. De gewone intervallen zijn dus niet merkbaar te smal.")
A("")
A("### 5.5 Een fout onderweg, en wat die leert")
A("")
A("De eerste bootstrap-run is ongeldig verklaard en apart bewaard. Naast de hoofdroute")
A("werd de vastgezette-familie-diagnostiek berekend, en als die faalde werd de hele")
A("replicatie weggegooid. Dat falen gebeurde niet willekeurig: het trof juist")
A("replicaties met zwakke afhankelijkheid, waarbij de fit op de parametergrens uitkwam.")
A("Daardoor waren de intervallen in 42 cellen te smal. Na de reparatie is het")
A("faalpercentage op de hoofdroute nul.")
A("")
A(fig(f"{BS}/figures/ci_example.png",
      "Figuur 3. Ebro bij Haro, periode 2, mean severity, de sterkste cel. Links de milde en de "
      "zware curve met hun 95 procent intervallen. Rechts het verschil zwaar min mild, apart "
      "gebootstrapt. De trapjes in de banden komen door het beperkte aantal droogtes."))
A("")

# ================================================================== 6
A("## 6. De copulakeuze, en hoe hard hij staat")
A("")
A("Dit is het antwoord op de eerste helft van het reviewerpunt. Per cel is met AIC")
A("gekozen uit vijftien families. Gekozen families op de gerepareerde definities:")
A("")
A("| familie | cellen | familie | cellen |")
A("|---|---|---|---|")
fams = cnt_fam.most_common()
for i in range(0, len(fams), 2):
    row = f"| {fams[i][0]} | {fams[i][1]} "
    row += f"| {fams[i+1][0]} | {fams[i+1][1]} |" if i + 1 < len(fams) else "| | |"
    A(row)
A("")
A("De bootstrap laat zien hoe hard die keuze staat, want in elke replicatie wordt")
A("opnieuw gekozen:")
A("")
A(f"- de winnaar op de volle steekproef is in {same} van de {len(iid)} cellen ook de")
A("  meest gekozen familie over de replicaties")
A(f"- maar hij wordt mediaan in slechts **{np.median(sh):.0%}** van de replicaties")
A(f"  gekozen, kwartielen {np.percentile(sh,25):.0%} en {np.percentile(sh,75):.0%}")
A(f"- over de replicaties worden mediaan **{int(np.median(nf))}** verschillende families")
A(f"  gekozen, maximum {nf.max()}")
A("")
A("De keuze wélke familie is dus zelden hard. Voor de transitiekansen is dat")
A("opgevangen, omdat de intervallen de herselectie in zich dragen. Maar het antwoord")
A("aan de reviewer hoort dit te zeggen: hier is de gekozen familie, en hier is hoe smal")
A("de marge is.")
A("")

# ================================================================== 7
A("## 7. De toetsen op afhankelijkheid, en hoe ze werken")
A("")
A("Een betrouwbaarheidsinterval zegt hoe groot een effect is. Of het effect *bestaat*,")
A("dus of de samenhang tussen zwaarte en piek van toeval te onderscheiden is, is een")
A("andere vraag. Daarvoor zijn per cel vier toetsen gebruikt, die elk iets anders zien.")
A("")
A("**Kendall's tau.** Neem alle paren van twee droogtes. Als de zwaardere van de twee")
A("ook de hogere piek had, is het paar concordant, anders discordant. Tau is het aandeel")
A("concordant min het aandeel discordant, tussen -1 en +1. Nul betekent geen monotone")
A("samenhang. De p-waarde volgt analytisch uit het aantal paren.")
A("")
A("**Spearman's rho.** De gewone correlatie, maar op de rangnummers in plaats van de")
A("waardes. Meet ook monotone samenhang, weegt grote rangverschillen zwaarder dan tau.")
A("")
A("**Hoeffding's D.** Vergelijkt de gezamenlijke verdeling van de twee rangen met wat")
A("je zou zien bij onafhankelijkheid, over het hele vlak. Daardoor ziet deze toets ook")
A("*niet-monotone* samenhang, bijvoorbeeld als zowel milde als zeer zware droogtes lage")
A("pieken geven en middelzware juist hoge. Tau en rho zien zoiets niet. De p-waarde komt")
A("uit permutatie, zie hieronder.")
A("")
A("**De permutatietoets op de copulafit zelf.** Dit is de toets die het dichtst bij de")
A("methode van het artikel staat. Het idee: als zwaarte en piek onafhankelijk zijn,")
A("maakt het niet uit welke piek bij welke droogte hoort. Dus husselen we de pieken")
A("duizend keer willekeurig over de droogtes, en draaien elke keer exact de procedure")
A("van het artikel: rangtransformatie, AIC-selectie over vijftien families, fit. Dat")
A("levert duizend AIC-waardes op die je onder onafhankelijkheid mag verwachten. De")
A("p-waarde is het aandeel daarvan dat minstens zo goed past als de echte fit.")
A("")
A("Waarom dit belangrijk is: met vijftien kandidaten vindt AIC altijd wel een familie")
A("die op ruis lijkt te passen. Door de selectie in de nulverdeling op te nemen, wordt")
A("daarvoor gecorrigeerd. Een fit die beter is dan wat husselen oplevert, is echt.")
A("")
A("Husselen heeft nog een voordeel boven hertrekken: het laat beide marginale")
A("verdelingen exact intact en verbreekt alleen de koppeling. De toets isoleert dus")
A("precies de afhankelijkheid.")
A("")
A("**Uit dezelfde permutaties** komen ook p-waardes voor het copula-deel van sectie 3.1")
A("op drie floodniveaus, zodat de toets direct aan de grootheid in de figuren hangt.")
A("")
A("### 7.1 Over veel toetsen tegelijk")
A("")
A("Bij 190 cellen en een grens van p 0,05 verwacht je bij puur toeval al 9,5")
A("significante cellen. Elk aantal moet daartegen worden afgezet. De correctie van")
A("Benjamini en Hochberg beheerst het aandeel valse positieven over alle cellen samen.")
A("Twee kanttekeningen. Met duizend permutaties is de kleinst mogelijke p 0,001, terwijl")
A("de eerste correctiestap over 190 cellen p onder 0,00026 vraagt; de permutatietoetsen")
A("kúnnen die drempel dus niet halen, en de uitspraak over de correctie steunt op de")
A("analytische p van tau en rho. En de correctie hoort bij *zoeken* over de hele kaart.")
A("Voor een locatie die het artikel vooraf al aanwijst, zoals Po midstream, is de")
A("ongecorrigeerde p het relevante bewijs.")
A("")

# ================================================================== 8
A("## 8. Resultaten")
A("")
A("### 8.1 Over heel Europa")
A("")
A("| toets | cellen met p < 0,05 | verwacht bij toeval |")
A("|---|---|---|")
for kol, naam in (("tau_p", "Kendall's tau"), ("rho_p", "Spearman's rho"),
                  ("hoeffd_p", "Hoeffding's D"), ("aic_perm_p", "permutatie op de copulafit"),
                  ("cp_q6915_p", "copula-deel bij quantiel 0,69")):
    s, t = telling(kol)
    A(f"| {naam} | {s} van {t} | {t*0.05:.1f} |")
A("")
A(f"Ruwweg het dubbele van de toevalsverwachting, dus een zwak maar echt signaal in het")
A(f"geheel. Mediaan tau {np.median(taus):+.3f}, positief in {int(np.sum(taus>0))} van de")
A(f"{len(taus)} cellen. Geen enkele cel overleeft de correctie over alle cellen samen.")
A("Er is dus geen breed Europees effect van droogtezwaarte op de piek erna.")
A("")
A("### 8.2 Waar de samenhang wél sterk is")
A("")
A(f"{len(sterk)} cellen halen minstens drie van de vier toetsen. Vet: het 95 procent")
A("interval sluit nul uit.")
A("")
A("| rivier | locatie | per. | variabele | richting | tau | copula-deel bij 0,69 | toetsen |")
A("|---|---|---|---|---|---|---|---|")
for cel, ns, d in sterk:
    tau = float(d["tau"])
    A(f"| {cel[0]} | {cel[1]} | {PER_NL[cel[2]]} | {PAIR_NL[cel[3]]} | "
      f"{'verhoogt' if tau > 0 else 'verlaagt'} | {tau:+.3f} | {fmt_ci(cel, 'copula_part')} | {ns}/4 |")
A("")
npos = sum(1 for c, ns, d in sterk if float(d["tau"]) > 0)
A(f"Twee clusters. **Positief, {npos} cellen, het zuiden:** Po bij Piacenza in beide")
A("periodes, Ebro en Tagus in periode 2, Danube Aschach in periode 1. Een zwaardere")
A("droogte verhoogt daar de kans op een hoge piek. Bij Ebro en Tagus zit dat vooral op")
A(f"mean severity en in periode 2. **Negatief, {len(sterk)-npos} cellen, Centraal-Europa,")
A("periode 1:** Vistula bij Turon en Weser bij Bodenwerder. Daar verlaagt een zwaardere")
A("droogte de kans, en bij Turon is dat het grootste effect van de kaart. Fysisch")
A("plausibel: een uitgedroogde bodem vangt de eerste neerslag op.")
A("")
A(fig(f"{BS}/figures/dependence_overview.png",
      "Figuur 4. Alle 190 cellen. Horizontaal Kendall's tau, verticaal de sterkte van de "
      "permutatietoets op de copulafit. Grote punten: minstens drie van de vier toetsen "
      "onder 0,05. Groen verhoogt, rood verlaagt."))
A("")
A("### 8.3 De intervallen: waar sluiten ze nul uit")
A("")
A("Bij quantiel 0,69:")
A("")
A("| grootheid | boven nul | onder nul | bevat nul |")
A("|---|---|---|---|")
for q, lab in (("marginal_part", "marginaal deel"), ("copula_part", "copula-deel"),
               ("diff_resel", "zwaar min mild")):
    p, n, t = sluit_uit(q)
    A(f"| {lab} | {p} van {t} | {n} van {t} | {t-p-n} van {t} |")
A("")
A(f"Mediane intervalbreedte rond de milde curve: {np.median(br):.3f}. De as-fout uit sectie")
A("2.1 was ongeveer 0,5, dus vier keer de onzekerheid.")
A("")
A(fig(f"{BS}/figures/ci_decomposition.png",
      "Figuur 5. Het marginale deel (links) en het copula-deel (rechts) over alle cellen: "
      "mediaan van de puntschatting, mediaan van het interval, en de spreiding tussen cellen. "
      "Het marginale deel is positief en breed gedragen; het copula-deel ligt rond nul."))
A("")
A(fig(f"{BS}/figures/ci_per_river.png",
      "Figuur 6. Per rivier het verschil zwaar min mild met 95 procent band, mediaan over de "
      "locaties, periodes en variabelen van die rivier."))
A("")

# ================================================================== 9
A("## 9. Hoe dit zich verhoudt tot de gepubliceerde resultaten")
A("")
A("### 9.1 De hoofdbevinding van het tweede deel draait om")
A("")
A("Het artikel stelt dat conditioneren op een voorafgaande droogte de floodkans")
A("verlaagt, en dat de zwaarte van de droogte dat gedeeltelijk terugdraait. De eerste")
A("helft was een gevolg van de as-fout. Op één as liggen de conditionele curves op of")
A("licht boven de unconditionele: het venster na een droogte is eerder natter dan")
A("droger dan een willekeurig venster. Dat is consistent met de ECA-kant, die meer")
A("coïncidenties vindt dan het toeval voorspelt, en de twee delen van het artikel")
A("spraken elkaar dus onterecht tegen.")
A("")
A("### 9.2 Uitspraken per passage")
A("")
A("| passage | uitspraak in het artikel | wat de herberekening en de toetsen zeggen |")
A("|---|---|---|")
A("| p6, abstract | mean severity en drought peak werken verschillend | blijft, maar de meeste locaties tonen geen aantoonbaar effect van beide |")
A("| p27 | Po: verhoogde kans bij zwaardere droogte, alleen periode 2 | de samenhang is echt, maar in beide periodes. \"Only during the second period\" klopt niet |")
A("| p27, p28, p30 | conditioneel blijft lager dan unconditioneel | vervalt, was de as-fout |")
A("| p28 | Ebro midstream: hogere kans in beide periodes (drought peak) | mager voor drought peak. Het echte Ebro-signaal zit bij mean severity in periode 2, Haro vier van vier toetsen |")
A("| p31 | tellingen 5, 6, 7, 9 locaties met toename | het criterium staat niet in de tekst en is niet exact te reproduceren |")
A("| p31 | Dnieper als regio met verhoogde kans | niet toetsbaar, te weinig droogte-events |")
A("| p31 | Tagus La Bazagona, lichte toename in periode 1 | de toetsen vinden La Bazagona juist in periode 2, als op één na sterkste punt |")
A("| p34 | robuuste systemen zijn Po en Ebro | blijft en wordt sterker onderbouwd. Tagus La Bazagona hoort erbij |")
A("")
A("### 9.3 Wat nieuw is")
A("")
A("Drie dingen staan nu nergens in het artikel en horen er wel in.")
A("")
A("Het onderscheid tussen het marginale en het copula-deel. Het brede verschijnsel is")
A("marginaal en is wat de ECA ook meet; het copula-raamwerk voegt daar op de meeste")
A("plekken niets aan toe, en op een handvol plekken juist wel.")
A("")
A("Het negatieve cluster in Centraal-Europa. Bij Vistula en Weser in periode 1 verlaagt")
A("een zwaardere droogte de kans op een hoge piek. Dat is fysisch interpreteerbaar en")
A("is materiaal voor de vraag van Reviewer #4 naar het mechanisme.")
A("")
A("De instabiliteit van de copulakeuze. De reviewer vraagt welke familie is gekozen;")
A("het eerlijke antwoord is welke, en dat die keuze in de meeste cellen op een klein")
A("AIC-verschil rust.")
A("")
A("### 9.4 Wat er voor de Revision Notes uit volgt")
A("")
A("Twee implementatiefouten met effect op de gepubliceerde cijfers, de ontbrekende stap")
A("F_Y en de einddetectie, plus twee kleinere definitiekwesties. De beschreven methode")
A("was in alle gevallen correct, de code week ervan af. Melden is een sterkere positie")
A("dan laten vinden. De volledige verantwoording staat in `CHANGELOG-methodology.md`.")
A("")

# ================================================================== 10
A("## 10. Beperkingen")
A("")
A("1. De bootstrap hertrekt de droogte-events en houdt het aantal events, de")
A("   SRI-standaardisatie en de quantieltransformatie vast. De intervallen zijn een")
A("   ondergrens op de totale onzekerheid.")
km = np.array([int(r["k_major"]) for r in iid])
A(f"2. De zware curve rust op weinig events, mediaan {int(np.median(km))} boven de zware")
A("   drempel. Waar dat aantal klein is, is de curve extrapolatie in de staart.")
A("3. De intervallen zijn puntsgewijs en niet gecorrigeerd voor 190 gelijktijdige")
A("   cellen. Tellingen over de kaart heen moeten daar rekening mee houden.")
A("4. De permutatietoetsen hebben een resolutie van 0,001 en kunnen daardoor geen")
A("   uitspraak doen over overleving van de FDR-correctie.")
A("5. De Dnieper valt grotendeels buiten de analyse door te weinig droogte-events.")
A("6. De referentiegroepen van de conditionele en de unconditionele curve verschillen,")
A("   events tegen weken. Dat blijft ook na de as-correctie een verschil.")
A("7. Het tweede deel gebruikt de wekelijkse gemiddelden als quantielreferentie, de")
A("   ECA-kant de dagelijkse reeks. Dat is nog een openstaand punt.")
A("")

# ================================================================== 11
A("## 11. Bronnen")
A("")
A("Code: `src/dtf/copula.py` en `scripts/11` tot en met `26`. Resultaten:")
A("`results/2026-09-02_copula_definition_variants/`, `results/2026-09-02_copula_corrected/`,")
A("`results/2026-09-02_copula_bootstrap/` en `results/2026-09-02_dependence_tests/`,")
A("elk met README en manifest. Beslissingen: `CHANGELOG-methodology.md` en")
A("`docs/open-decisions.md`, D-15 tot en met D-20. Het eindrapport met alle cijfers per")
A("cel: `results/2026-09-02_copula_bootstrap/report.md`.")
A("")

md_text = "\n".join(L) + "\n"
open(f"{OUT}/report.md", "w").write(md_text)

# ------------------------------------------------------------------ PDF
html_body = markdown.markdown(md_text, extensions=["tables"])
css = """
@page { size: A4; margin: 2.0cm 2.0cm 2.2cm 2.0cm;
        @frame footer { -pdf-frame-content: footer; bottom: 0.8cm; margin-left: 2cm;
                        margin-right: 2cm; height: 0.8cm; } }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10.2pt; line-height: 1.38; color: #111; }
h1 { font-size: 20pt; margin: 0 0 4pt 0; }
h2 { font-size: 14pt; margin: 20pt 0 6pt 0; border-bottom: 1px solid #999; padding-bottom: 2pt; }
h3 { font-size: 11.5pt; margin: 14pt 0 4pt 0; }
p { margin: 0 0 7pt 0; text-align: justify; }
blockquote { margin: 6pt 18pt; padding: 4pt 10pt; background: #f2f2f2; border-left: 3px solid #999;
             font-family: Courier, monospace; font-size: 9.5pt; }
table { width: 100%; border-collapse: collapse; margin: 6pt 0 10pt 0; font-size: 8.6pt; }
th, td { border: 1px solid #bbb; padding: 3pt 4pt; text-align: left; vertical-align: top; }
th { background: #e8e8e8; }
code { font-family: Courier, monospace; font-size: 9pt; }
.fig { margin: 10pt 0 12pt 0; text-align: center; }
.fig img { width: 16.5cm; }
.cap { font-size: 8.8pt; color: #333; text-align: left; margin: 4pt 0 0 0; }
#footer { font-size: 8pt; color: #666; text-align: right; }
"""
html = f"""<html><head><meta charset="utf-8"><style>{css}</style></head><body>
{html_body}
<div id="footer">De copula-analyse van drought-to-flood transities, 3 september 2026, pagina <pdf:pagenumber/></div>
</body></html>"""
with open(f"{OUT}/report.pdf", "wb") as fh:
    status = pisa.CreatePDF(html, dest=fh, encoding="utf-8")
print(f"markdown: {OUT}/report.md ({len(L)} regels)")
print(f"pdf: {OUT}/report.pdf, fouten: {status.err}")
