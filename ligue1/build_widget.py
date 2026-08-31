#!/usr/bin/env python3
"""Genere le widget calendrier Ligue 1 2026-27 a partir de schedule.json.

Sorties :
  index.html                     cible de l'iframe (GitHub Pages)
  embed-wordpress.html           bloc a coller : contenu crawlable + iframe durcie
  widget-wordpress-inline.html   variante autonome (logos embarques si presents)
"""
import base64
import json
import re
from datetime import date
from pathlib import Path

from clubs import CLUBS, LOGO_BASE, LOGOS_MANQUANTS

EPOCH = date(2026, 8, 1)

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def hex_to_rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def _lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def logo_chip_sombre(code):
    """Un logo servi uniquement en blanc exige une pastille foncee."""
    p = Path("logos") / f"{code}.svg"
    if not p.exists():
        return 0
    cols = set(re.findall(r"#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}\b",
                          p.read_text(encoding="utf-8")))
    return 1 if cols and min(_lum(c) for c in cols) > 0.6 else 0


def logo_src(code, inline):
    if code in LOGOS_MANQUANTS:
        return ""
    for ext in ("svg", "png"):
        p = Path("logos") / f"{code}.{ext}"
        if p.exists():
            if not inline:
                return f"{LOGO_BASE}{code}.{ext}"
            mime = "image/svg+xml" if ext == "svg" else "image/png"
            return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    return ""


def build_data(inline):
    raw = json.load(open("schedule.json", encoding="utf-8"))["journees"]
    ordre = sorted(CLUBS, key=lambda k: CLUBS[k][0])          # tri alphabetique
    codes = [CLUBS[k][2] for k in ordre]
    idx = {k: i for i, k in enumerate(ordre)}

    # 0 code, 1 nom, 2 nom court, 3 couleur claire, 4 rgb clair,
    # 5 couleur sombre, 6 rgb sombre, 7 logo, 8 pastille foncee
    clubs_js = []
    for k in ordre:
        nom, court, code, cl, cd = CLUBS[k]
        clubs_js.append([code, nom, court, cl, hex_to_rgb(cl), cd,
                         hex_to_rgb(cd), logo_src(code, inline),
                         logo_chip_sombre(code)])

    # par club : [adversaire, exterieur(0/1), numero de journee, jour depuis EPOCH]
    sched = {code: [] for code in codes}
    for num, j in sorted(((int(n), v) for n, v in raw.items())):
        y, m, d = (int(x) for x in j["date"].split("-"))
        off = (date(y, m, d) - EPOCH).days
        for match in j["matchs"]:
            dom, ext = match["dom"], match["ext"]
            sched[CLUBS[dom][2]].append([idx[ext], 0, num, off])
            sched[CLUBS[ext][2]].append([idx[dom], 1, num, off])

    for code in sched:
        sched[code].sort(key=lambda g: g[2])
    return clubs_js, sched


def fr_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    dt = date(y, m, d)
    return f"{JOURS[dt.weekday()]} {'1er' if d == 1 else d} {MOIS[m - 1]} {y}"




PAGES_URL = "https://jcrochet-netizen.github.io/schebasketusa/ligue1/"
PAGES_ORIGIN = "https://jcrochet-netizen.github.io"
IFRAME_MIN_H = 700

IFRAME_CSS = """<style>
html,body{margin:0;background:transparent;overflow:hidden;}
.busa-l1{max-width:none;border:0;border-radius:0;}
.busa-l1 .l1-list{max-height:26rem;}
</style>
"""

IFRAME_JS = """<script>
(function(){
  var last=0;
  function envoyer(){
    var h=Math.ceil(document.body.getBoundingClientRect().height);
    if(!h||h===last) return;
    last=h;
    parent.postMessage({type:'busa-l1-height',height:h},'*');
  }
  window.addEventListener('load',envoyer);
  window.addEventListener('resize',envoyer);
  if(window.ResizeObserver) new ResizeObserver(envoyer).observe(document.body);
  document.addEventListener('DOMContentLoaded',envoyer);
  envoyer();
})();
</script>
"""

TITLE = "<title>Calendrier Ligue 1 2026-27 &middot; BasketUSA</title>\n"
PAGE_PAD = ("<style>body{margin:0;padding:2rem 1rem;background:#fff;}"
            "@media (prefers-color-scheme:dark){body{background:#0b0d10;}}</style>\n")


def make_fragment(inline):
    clubs_js, sched = build_data(inline)
    js = (Path("widget.js").read_text(encoding="utf-8")
          .replace("__CLUBS__", json.dumps(clubs_js, ensure_ascii=False,
                                           separators=(",", ":")))
          .replace("__SCHED__", json.dumps(sched, separators=(",", ":"))))
    return ("<style>\n" + Path("widget.css").read_text(encoding="utf-8").strip() + "\n</style>\n\n"
            + Path("widget.html").read_text(encoding="utf-8")
            + "\n<script>\n" + js.strip() + "\n</script>\n")


def build_embed():
    """Contenu crawlable + iframe durcie : une iframe seule ne rapporte rien en SEO."""
    raw = json.load(open("schedule.json", encoding="utf-8"))["journees"]
    J = {int(k): v for k, v in raw.items()}
    nom = {k: CLUBS[k][0] for k in CLUBS}

    j1 = J[1]
    affiches = [f"    <li><strong>{nom[m['dom']]} – {nom[m['ext']]}</strong></li>"
                for m in j1["matchs"]]

    # tous les clubs, avec leur premier adversaire
    prem = []
    for pdfname in sorted(CLUBS, key=lambda k: CLUBS[k][0]):
        m = next(x for x in j1["matchs"]
                 if pdfname in (x["dom"], x["ext"]))
        dom = m["dom"] == pdfname
        adv = nom[m["ext"] if dom else m["dom"]]
        lieu = f"reçoit {adv}" if dom else f"se déplace à {adv}"
        prem.append(f"    <li><strong>{nom[pdfname]}</strong> — {lieu}.</li>")

    debut, fin = J[1]["date"], J[34]["date"]

    return f"""<!-- ============================================================
     Calendrier Ligue 1 2026-2027 — bloc a coller dans un bloc HTML personnalise.
     Le texte et les listes ci-dessous sont le contenu indexe par Google :
     ne pas les supprimer, l'iframe seule ne rapporte aucun SEO.
     ============================================================ -->

<h2>Le calendrier de Ligue 1 2026-2027 club par club</h2>

<p>La saison 2026-2027 de Ligue 1 s’ouvre le {fr_date(debut)} et s’achève le
{fr_date(fin)}. Les 18 clubs disputent 34 journées, soit 34 matchs chacun&nbsp;:
17 à domicile et 17 à l’extérieur, chaque équipe affrontant toutes les autres deux
fois. Le calendrier ci-dessous permet de sélectionner un club et d’afficher
l’intégralité de son programme, journée par journée.</p>

<p><strong>Les dates indiquées sont celles des journées, telles que publiées par la
LFP.</strong> Les jours et horaires précis de chaque rencontre sont fixés
ultérieurement selon la programmation télévisée&nbsp;: une journée de Ligue 1 se
dispute généralement du vendredi au dimanche, et certaines rencontres peuvent être
décalées en cas de coupe d’Europe.</p>

<h3>La première journée de Ligue 1 2026-2027</h3>

<ul>
{chr(10).join(affiches)}
</ul>

<h3>Calendrier interactif : choisissez votre club</h3>

<iframe id="busa-l1-cal"
        src="{PAGES_URL}"
        title="Calendrier de Ligue 1 2026-2027, match par match, club par club"
        loading="lazy"
        scrolling="no"
        referrerpolicy="strict-origin-when-cross-origin"
        style="display:block;margin:0 auto;width:100%;max-width:640px;
               min-height:{IFRAME_MIN_H}px;border:0;overflow:hidden"></iframe>

<script>
/* Ajuste la hauteur de l'iframe a son contenu. Amelioration progressive : si ce
   script est filtre par WordPress, l'iframe reste lisible grace au min-height. */
(function(){{
  var ORIGIN = '{PAGES_ORIGIN}';
  var frame  = document.getElementById('busa-l1-cal');
  window.addEventListener('message', function(e){{
    if (e.origin !== ORIGIN) return;
    var d = e.data;
    if (!d || d.type !== 'busa-l1-height') return;
    var h = parseInt(d.height, 10);
    if (!h || h < 1) return;
    if (!frame) frame = document.getElementById('busa-l1-cal');
    if (!frame) return;
    frame.style.height = h + 'px';
    frame.style.minHeight = '0';
  }}, false);
}})();
</script>

<h3>L’entrée en lice de chaque club de Ligue 1</h3>

<ul>
{chr(10).join(prem)}
</ul>
"""


def main():
    linked = make_fragment(inline=False)
    inline = make_fragment(inline=True)

    Path("widget-wordpress-inline.html").write_text(inline, encoding="utf-8")
    Path("embed-wordpress.html").write_text(build_embed(), encoding="utf-8")

    Path("index.html").write_text(
        "<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        "<meta name=\"robots\" content=\"noindex,follow\">\n"
        + TITLE + "</head>\n<body>\n" + linked + IFRAME_CSS + IFRAME_JS
        + "</body>\n</html>\n", encoding="utf-8")

    Path("apercu-local.html").write_text(
        "<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        + TITLE + PAGE_PAD + "</head>\n<body>\n" + linked + "</body>\n</html>\n",
        encoding="utf-8")

    logos = len([c for c in CLUBS if logo_src(CLUBS[c][2], False)])
    print(f"logos cables : {logos}/18")
    for f in ("index.html", "embed-wordpress.html"):
        print(f"{f}: {Path(f).stat().st_size/1024:.0f} Ko")


main()
