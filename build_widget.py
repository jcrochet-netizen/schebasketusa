#!/usr/bin/env python3
"""Genere le widget calendrier NBA 2026-27 a partir de schedule.json.

Sorties :
  widget-wordpress.html          fragment a coller dans un bloc "HTML personnalise"
  nba-calendrier-2026-27.html    page autonome (previsualisation locale)
  artifact.html                  meme fragment, pour publication en Artifact
"""
import base64
import json
import re
from datetime import date
from pathlib import Path

from teams import TEAMS, OPP_TO_TRI, VENUE_LABELS, LOGO_BASE, LOGOS_MANQUANTS

EPOCH = date(2026, 10, 1)
VENUE_ORDER = ["", "Paris", "Manchester", "Mexico", "Austin"]


def hex_to_rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def _lum(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def logo_needs_dark_chip(tri):
    """Certains logos ne sont servis qu'en blanc (Brooklyn) : ils sont prevus
    pour un fond noir et seraient invisibles sur fond clair. On les detecte a
    la couleur plutot que de les traiter en cas particulier."""
    path = Path("logos") / f"{tri}.svg"
    if not path.exists():
        return 0
    cols = set(re.findall(r"#[0-9A-Fa-f]{6}|#[0-9A-Fa-f]{3}\b", path.read_text(encoding="utf-8")))
    if not cols:
        return 0
    return 1 if min(_lum(c) for c in cols) > 0.6 else 0


def logo_src(tri, inline):
    """URL du logo : soit un lien vers le fichier, soit une data-URI embarquee."""
    if tri in LOGOS_MANQUANTS:
        return ""
    path = Path("logos") / f"{tri}.svg"
    if not path.exists():
        return ""
    if not inline:
        return f"{LOGO_BASE}{tri}.svg"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return "data:image/svg+xml;base64," + b64


def build_data(inline):
    raw = json.load(open("schedule.json", encoding="utf-8"))
    tris = sorted(TEAMS)
    idx = {t: i for i, t in enumerate(tris)}

    # 0 tricode, 1 nom, 2 surnom, 3 conference, 4 couleur claire, 5 rgb clair,
    # 6 couleur sombre, 7 rgb sombre, 8 logo, 9 logo a poser sur pastille foncee
    teams_js = [
        [t, TEAMS[t][0], TEAMS[t][1], TEAMS[t][2],
         TEAMS[t][3], hex_to_rgb(TEAMS[t][3]),
         TEAMS[t][4], hex_to_rgb(TEAMS[t][4]),
         logo_src(t, inline), logo_needs_dark_chip(t)]
        for t in tris
    ]

    sched = {}
    for tri in tris:
        rows = []
        for g in raw[tri]["games"]:
            y, m, d = (int(x) for x in g["date"].split("-"))
            day_off = (date(y, m, d) - EPOCH).days
            hh, mm = (int(x) for x in g["time"].split(":"))
            flags = (1 if g["away"] else 0) | (2 if g.get("cup") else 0)
            if "venue" in g:
                flags |= VENUE_ORDER.index(VENUE_LABELS[g["venue"]]) << 2
            rows.append([idx[OPP_TO_TRI[g["opp"]]], flags, day_off, hh * 60 + mm])
        sched[tri] = rows

    return teams_js, sched


CSS = """
.busa-nba{
  /* palette claire : neutres legerement froids, pour ne pas se battre
     avec les 30 couleurs de franchise qui servent d'accent */
  --bn-ground:#ffffff; --bn-surface:#f4f6f8; --bn-line:#e4e8ed;
  --bn-ink:#15181d; --bn-ink2:#5b636f; --bn-ink3:#8b939f;
  --bn-team:#15181d; --bn-team-rgb:21,24,29;
  /* les logos NBA sont dessines pour un fond clair : sur fond sombre on les
     pose sur une pastille claire, sinon les marques monochromes disparaissent */
  --bn-crest-bg:none; --bn-crest-pad:0;

  max-width:640px; margin:0 auto; background:var(--bn-ground); color:var(--bn-ink);
  border:1px solid var(--bn-line); border-radius:14px; overflow:hidden;
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,
    "Helvetica Neue",Arial,sans-serif;
  font-size:16px; line-height:1.45; text-align:left;
  -webkit-font-smoothing:antialiased;
}
.busa-nba *,.busa-nba *::before,.busa-nba *::after{box-sizing:border-box;}
.busa-nba p,.busa-nba h2,.busa-nba h3,.busa-nba ol,.busa-nba li{margin:0;padding:0;}
.busa-nba ol{list-style:none;}

@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]) .busa-nba:not([data-busa-theme="light"]){
    --bn-ground:#101317; --bn-surface:#191d23; --bn-line:#272c34;
    --bn-ink:#e9ecf0; --bn-ink2:#9ba3af; --bn-ink3:#6e7683;
    --bn-crest-bg:#eef1f5; --bn-crest-pad:.26rem;
  }
}
:root[data-theme="dark"] .busa-nba:not([data-busa-theme="light"]){
  --bn-ground:#101317; --bn-surface:#191d23; --bn-line:#272c34;
  --bn-ink:#e9ecf0; --bn-ink2:#9ba3af; --bn-ink3:#6e7683;
  --bn-crest-bg:#eef1f5; --bn-crest-pad:.26rem;
}

/* --- en-tete --- */
.busa-nba .bn-head{
  display:flex; flex-wrap:wrap; gap:.75rem 1rem; align-items:flex-end;
  justify-content:space-between; padding:.95rem 1rem .85rem;
  border-bottom:1px solid var(--bn-line);
}
.busa-nba .bn-id{display:flex; align-items:center; gap:.65rem; min-width:0;}
.busa-nba .bn-idtxt{min-width:0;}
.busa-nba .bn-eyebrow{
  font-size:.62rem; font-weight:600; letter-spacing:.13em; text-transform:uppercase;
  color:var(--bn-ink3);
}
.busa-nba .bn-season{
  font-size:1.1rem; font-weight:650; letter-spacing:-.015em; line-height:1.2;
  color:var(--bn-ink);
}
/* ecusson : logo fourni par le site, sinon monogramme aux couleurs du club */
.busa-nba .bn-crest{
  flex:none; display:grid; place-items:center;
  width:2.4rem; height:2.4rem; border-radius:50%;
  background:rgba(var(--bn-team-rgb),.11);
  box-shadow:inset 0 0 0 1px rgba(var(--bn-team-rgb),.22);
  font-size:.62rem; font-weight:750; letter-spacing:.02em;
  color:var(--bn-team); overflow:hidden;
}
.busa-nba .bn-crest img{
  width:100%; height:100%; object-fit:contain; display:block;
}
.busa-nba .bn-crest.has-logo{
  background:var(--bn-crest-bg,none); box-shadow:none; padding:var(--bn-crest-pad,0);
}
/* logos servis uniquement en blanc : pastille foncee dans les deux themes */
.busa-nba .bn-crest.has-logo.chip-dark{background:#15181d; padding:.26rem;}
.busa-nba .bn-pick{position:relative; display:block;}
.busa-nba .bn-pick::after{
  content:""; position:absolute; right:.7rem; top:50%; width:.42rem; height:.42rem;
  border-right:1.6px solid var(--bn-ink2); border-bottom:1.6px solid var(--bn-ink2);
  transform:translateY(-70%) rotate(45deg); pointer-events:none;
}
.busa-nba select{
  -webkit-appearance:none; appearance:none;
  font:inherit; font-size:.875rem; font-weight:550; color:var(--bn-ink);
  background:var(--bn-surface); border:1px solid var(--bn-line); border-radius:9px;
  padding:.42rem 1.9rem .42rem .7rem; min-width:12.5rem; max-width:100%; cursor:pointer;
}
.busa-nba select:focus-visible{outline:2px solid var(--bn-team); outline-offset:2px;}

/* --- filtres (portent aussi les compteurs : pas de ligne de stats en plus) --- */
.busa-nba .bn-filters{
  display:grid; grid-template-columns:repeat(3,1fr); gap:.3rem;
  padding:.6rem 1rem; border-bottom:1px solid var(--bn-line);
}
.busa-nba .bn-filters button{
  display:flex; align-items:baseline; justify-content:center; gap:.4rem;
  font:inherit; font-size:.78rem; color:var(--bn-ink2);
  background:transparent; border:1px solid transparent; border-radius:8px;
  padding:.34rem .3rem; cursor:pointer; transition:background .15s,color .15s;
}
.busa-nba .bn-filters button:hover{background:var(--bn-surface);}
.busa-nba .bn-filters button b{
  font-size:.78rem; font-weight:650; font-variant-numeric:tabular-nums;
  color:var(--bn-ink);
}
.busa-nba .bn-filters button[aria-pressed="true"]{
  background:rgba(var(--bn-team-rgb),.1); color:var(--bn-team);
  border-color:rgba(var(--bn-team-rgb),.22);
}
.busa-nba .bn-filters button[aria-pressed="true"] b{color:var(--bn-team);}
.busa-nba .bn-filters button:focus-visible{outline:2px solid var(--bn-team); outline-offset:1px;}

/* --- liste --- */
.busa-nba .bn-list{
  max-height:min(60vh,32rem); overflow-y:auto; overscroll-behavior:contain;
  scrollbar-width:thin; scrollbar-color:var(--bn-line) transparent;
}
.busa-nba .bn-list::-webkit-scrollbar{width:8px;}
.busa-nba .bn-list::-webkit-scrollbar-thumb{
  background:var(--bn-line); border-radius:4px;
}
.busa-nba .bn-month{
  position:sticky; top:0; z-index:1; background:var(--bn-ground);
  padding:.7rem 1rem .3rem;
}
.busa-nba .bn-month h3{
  font-size:.66rem; font-weight:650; letter-spacing:.12em; text-transform:uppercase;
  color:var(--bn-ink3);
}
.busa-nba .bn-g{
  display:grid; grid-template-columns:4.1rem 1.35rem 1fr auto;
  align-items:center; gap:.55rem;
  padding:.42rem 1rem; border-top:1px solid var(--bn-line);
}
.busa-nba .bn-month + .bn-g{border-top:0;}
.busa-nba .bn-date{
  font-size:.78rem; color:var(--bn-ink2); font-variant-numeric:tabular-nums;
  white-space:nowrap;
}
.busa-nba .bn-ico{font-size:.82rem; line-height:1; text-align:center;}
.busa-nba .bn-opp{
  display:flex; align-items:baseline; gap:.35rem; min-width:0;
  font-size:.875rem; font-weight:500; color:var(--bn-ink);
}
.busa-nba .bn-name{min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}
.busa-nba .bn-short{display:none;}
.busa-nba .bn-time{
  font-size:.85rem; font-weight:600; color:var(--bn-ink);
  font-variant-numeric:tabular-nums;
}
.busa-nba .bn-g.is-home{background:rgba(var(--bn-team-rgb),.045);}
.busa-nba .bn-g.is-past{opacity:.42;}
.busa-nba .bn-g.is-next .bn-date{color:var(--bn-team); font-weight:650;}
.busa-nba .bn-g.is-next .bn-time{color:var(--bn-team);}

.busa-nba .bn-tag{
  flex:none; padding:.03rem .3rem;
  font-size:.6rem; font-weight:650; letter-spacing:.05em; text-transform:uppercase;
  color:var(--bn-ink2); background:var(--bn-surface);
  border:1px solid var(--bn-line); border-radius:4px;
}
.busa-nba .bn-empty{padding:2rem 1rem; text-align:center; color:var(--bn-ink3); font-size:.85rem;}

/* --- note de bas de widget --- */
.busa-nba .bn-note{
  padding:.65rem 1rem .75rem; border-top:1px solid var(--bn-line);
  background:var(--bn-surface);
  font-size:.7rem; line-height:1.5; color:var(--bn-ink3);
}
.busa-nba .bn-note b{color:var(--bn-ink2); font-weight:600;}

.busa-nba .bn-sr{
  position:absolute; width:1px; height:1px; padding:0; margin:-1px;
  overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; border:0;
}

/* mobile : on masque le mot du filtre mais jamais son emoji, et on bascule
   sur le surnom de la franchise pour eviter les noms tronques */
@media (max-width:430px){
  .busa-nba .bn-filters button .bn-lbl{display:none;}
  .busa-nba .bn-g{grid-template-columns:3.6rem 1.2rem 1fr auto; gap:.4rem;}
  .busa-nba .bn-opp{font-size:.85rem;}
  .busa-nba .bn-full{display:none;}
  .busa-nba .bn-short{display:inline;}
}
@media (prefers-reduced-motion:reduce){
  .busa-nba *{transition:none !important;}
}
"""


HTML = """<div class="busa-nba" id="busaNba">
  <div class="bn-head">
    <div class="bn-id">
      <span class="bn-crest" id="bnCrest" aria-hidden="true"></span>
      <div class="bn-idtxt">
        <p class="bn-eyebrow">Calendrier NBA 2026-27</p>
        <h2 class="bn-season" id="bnName">&nbsp;</h2>
      </div>
    </div>
    <label class="bn-pick">
      <span class="bn-sr">Choisir une franchise</span>
      <select id="bnTeam"></select>
    </label>
  </div>

  <div class="bn-filters" role="group" aria-label="Filtrer les matchs">
    <button type="button" data-f="all" aria-pressed="true">Tous<b id="bnNa">0</b></button>
    <button type="button" data-f="home" aria-pressed="false">&#127968;<span class="bn-lbl">&nbsp;Domicile</span><b id="bnNh">0</b></button>
    <button type="button" data-f="away" aria-pressed="false">&#9992;&#65039;<span class="bn-lbl">&nbsp;Ext&eacute;rieur</span><b id="bnNe">0</b></button>
  </div>

  <div class="bn-list" id="bnList"></div>

  <p class="bn-note">
    &#127968; domicile &middot; &#9992;&#65039; ext&eacute;rieur &mdash;
    horaires en <b>heure fran&ccedil;aise</b> (un match jou&eacute; le soir aux
    &Eacute;tats-Unis est dat&eacute; au jour fran&ccedil;ais, soit le lendemain).
    2&nbsp;matchs de d&eacute;but d&eacute;cembre restent &agrave; programmer selon le
    parcours en NBA&nbsp;Cup. Calendrier officiel NBA au 13/08/2026.
  </p>
</div>
"""


JS = """
(function(){
  var TEAMS=__TEAMS__, SCHED=__SCHED__, VENUES=__VENUES__;
  var EPOCH=Date.UTC(2026,9,1), DAY=864e5;
  var DAYS=['dim.','lun.','mar.','mer.','jeu.','ven.','sam.'];
  var MONTHS=['janvier','f\\u00e9vrier','mars','avril','mai','juin','juillet',
              'ao\\u00fbt','septembre','octobre','novembre','d\\u00e9cembre'];

  var root=document.getElementById('busaNba');
  var sel=document.getElementById('bnTeam');
  var list=document.getElementById('bnList');
  var btns=root.querySelectorAll('.bn-filters button');
  var filter='all', current='ATL';

  var now=new Date();
  var todayOff=Math.round((Date.UTC(now.getFullYear(),now.getMonth(),now.getDate())-EPOCH)/DAY);

  // --- selecteur, groupe par conference ---
  [['E','Conf\\u00e9rence Est'],['O','Conf\\u00e9rence Ouest']].forEach(function(c){
    var g=document.createElement('optgroup'); g.label=c[1];
    TEAMS.map(function(t,i){return [t,i];})
      .filter(function(p){return p[0][3]===c[0];})
      .sort(function(a,b){return a[0][1].localeCompare(b[0][1],'fr');})
      .forEach(function(p){
        var o=document.createElement('option');
        o.value=p[0][0]; o.textContent=p[0][1]; g.appendChild(o);
      });
    sel.appendChild(g);
  });

  function pad(n){return n<10?'0'+n:''+n;}
  function idx(tri){for(var i=0;i<TEAMS.length;i++){if(TEAMS[i][0]===tri)return i;}return 0;}

  function isDark(){
    var de=document.documentElement;
    if(root.getAttribute('data-busa-theme')==='light') return false;
    if(de.getAttribute('data-theme')==='dark') return true;
    if(de.getAttribute('data-theme')==='light') return false;
    return window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  function paint(){
    var t=TEAMS[idx(current)], dark=isDark();
    root.style.setProperty('--bn-team', dark?t[6]:t[4]);
    root.style.setProperty('--bn-team-rgb', dark?t[7]:t[5]);
  }

  function crest(){
    var t=TEAMS[idx(current)], el=document.getElementById('bnCrest');
    el.className='bn-crest';
    if(t[8]){
      var img=new Image();
      img.alt=''; img.loading='lazy'; img.decoding='async';
      // si le logo ne charge pas, on retombe sur le monogramme
      img.onerror=function(){ el.className='bn-crest'; el.textContent=t[0]; };
      img.src=t[8];
      el.textContent='';
      el.className='bn-crest has-logo'+(t[9]?' chip-dark':'');
      el.appendChild(img);
    } else {
      el.textContent=t[0];
    }
  }

  function render(){
    var games=SCHED[current]||[];
    var nh=0,na=0;
    games.forEach(function(g){ (g[1]&1)?na++:nh++; });
    document.getElementById('bnNa').textContent=games.length;
    document.getElementById('bnNh').textContent=nh;
    document.getElementById('bnNe').textContent=na;
    document.getElementById('bnName').textContent=TEAMS[idx(current)][1];

    var shown=games.filter(function(g){
      return filter==='all' || (filter==='home')===!(g[1]&1);
    });

    if(!shown.length){ list.innerHTML='<p class="bn-empty">Aucun match.</p>'; return; }

    var nextIdx=-1;
    for(var i=0;i<shown.length;i++){ if(shown[i][2]>=todayOff){ nextIdx=i; break; } }

    var html='', lastMonth=-1;
    shown.forEach(function(g,i){
      var d=new Date(EPOCH+g[2]*DAY);
      var mo=d.getUTCMonth();
      if(mo!==lastMonth){
        lastMonth=mo;
        var label=MONTHS[mo].charAt(0).toUpperCase()+MONTHS[mo].slice(1);
        html+='<div class="bn-month"><h3>'+label+' '+d.getUTCFullYear()+'</h3></div>';
      }
      var away=!!(g[1]&1), cup=!!(g[1]&2), venue=VENUES[g[1]>>2]||'';
      var iso=d.getUTCFullYear()+'-'+pad(mo+1)+'-'+pad(d.getUTCDate());
      var cls='bn-g'+(away?'':' is-home')
              +(g[2]<todayOff?' is-past':'')+(i===nextIdx?' is-next':'');
      var tags=(cup?'<span class="bn-tag">NBA Cup</span>':'')
              +(venue?'<span class="bn-tag">'+venue+'</span>':'');
      var dnum=d.getUTCDate(), dlabel=DAYS[d.getUTCDay()]+' '+(dnum===1?'1er':dnum);
      html+='<li class="'+cls+'">'
          + '<time class="bn-date" datetime="'+iso+'">'+dlabel+'</time>'
          + '<span class="bn-ico" aria-hidden="true">'+(away?'\\u2708\\ufe0f':'\\ud83c\\udfe0')+'</span>'
          + '<span class="bn-opp"><span class="bn-sr">'
          +   (away?'\\u00c0 l\\u2019ext\\u00e9rieur chez ':'\\u00c0 domicile contre ')+'</span>'
          +   '<span class="bn-name bn-full">'+TEAMS[g[0]][1]+'</span>'
          +   '<span class="bn-name bn-short">'+TEAMS[g[0]][2]+'</span>'
          +   tags+'</span>'
          + '<span class="bn-time">'+pad(Math.floor(g[3]/60))+':'+pad(g[3]%60)+'</span>'
          + '</li>';
    });
    list.innerHTML='<ol>'+html+'</ol>';
  }

  function setTeam(tri,push){
    if(!SCHED[tri]) return;
    current=tri; sel.value=tri; paint(); crest(); render();
    if(push && history.replaceState) history.replaceState(null,'','#'+tri);
  }

  sel.addEventListener('change',function(){ setTeam(sel.value,true); list.scrollTop=0; });

  Array.prototype.forEach.call(btns,function(b){
    b.addEventListener('click',function(){
      filter=b.getAttribute('data-f');
      Array.prototype.forEach.call(btns,function(x){
        x.setAttribute('aria-pressed', x===b?'true':'false');
      });
      render(); list.scrollTop=0;
    });
  });

  if(window.matchMedia){
    var mq=window.matchMedia('(prefers-color-scheme: dark)');
    (mq.addEventListener?mq.addEventListener.bind(mq,'change'):mq.addListener.bind(mq))(paint);
  }

  // franchise d'ouverture : ?team=LAL (pratique en iframe) ou ancre #LAL
  function wanted(){
    var m=(location.search||'').match(/[?&]team=([A-Za-z]{3})/);
    var t=(m?m[1]:(location.hash||'').replace('#','')).toUpperCase();
    return SCHED[t]?t:'ATL';
  }
  setTeam(wanted(),false);
  window.addEventListener('hashchange',function(){
    var h=(location.hash||'').replace('#','').toUpperCase();
    if(SCHED[h]) setTeam(h,false);
  });
})();
"""


def make_fragment(inline):
    teams_js, sched = build_data(inline)
    js = (JS
          .replace("__TEAMS__", json.dumps(teams_js, ensure_ascii=False, separators=(",", ":")))
          .replace("__SCHED__", json.dumps(sched, separators=(",", ":")))
          .replace("__VENUES__", json.dumps(VENUE_ORDER)))
    return ("<style>\n" + CSS.strip() + "\n</style>\n\n"
            + HTML
            + "\n<script>\n" + js.strip() + "\n</script>\n")


PAGE_PAD = ("<style>body{margin:0;padding:2rem 1rem;background:#fff;}"
            "@media (prefers-color-scheme:dark){body{background:#0b0d10;}}</style>\n")
TITLE = "<title>Calendrier NBA 2026-27 &middot; BasketUSA</title>\n"

# Page servie dans l'iframe. La liste s'affiche en entier (pas de zone de
# defilement interne) : c'est la page parente qui defile, ce qui evite le
# double-scroll sur mobile. La hauteur est renvoyee au parent en postMessage.
# A placer APRES le fragment : le <style> du widget est dans le body, une regle
# de meme specificite mise dans le <head> se ferait ecraser.
IFRAME_CSS = """<style>
html,body{margin:0;background:transparent;overflow:hidden;}
.busa-nba{max-width:none;border:0;border-radius:0;}
.busa-nba .bn-list{max-height:none;overflow-y:visible;}
.busa-nba .bn-month{position:static;}
</style>
"""

IFRAME_JS = """<script>
(function(){
  var last=0;
  function envoyer(){
    var h=Math.ceil(document.body.getBoundingClientRect().height);
    if(!h||h===last) return;
    last=h;
    parent.postMessage({type:'busa-nba-height',height:h},'*');
  }
  window.addEventListener('load',envoyer);
  window.addEventListener('resize',envoyer);
  if(window.ResizeObserver) new ResizeObserver(envoyer).observe(document.body);
  document.addEventListener('DOMContentLoaded',envoyer);
  envoyer();
})();
</script>
"""


PAGES_URL = "https://jcrochet-netizen.github.io/schebasketusa/"
PAGES_ORIGIN = "https://jcrochet-netizen.github.io"
# Plancher mesure sur le rendu reel (pire cas : mobile, 80 matchs = 3220 px).
# Il evite le CLS avant le premier postMessage, et surtout garantit que rien
# n'est tronque si WordPress filtre le script parent. Le script le remet a 0
# des qu'il connait la hauteur exacte, sinon on garderait un blanc sur desktop.
IFRAME_MIN_H = 3300

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def fr_date(iso, avec_jour=True):
    y, m, d = (int(x) for x in iso.split("-"))
    dt = date(y, m, d)
    jour = f"{JOURS[dt.weekday()]} " if avec_jour else ""
    return f"{jour}{'1er' if d == 1 else d} {MOIS[m - 1]} {y}"


def build_embed():
    """Bloc pret a coller : contenu crawlable + iframe durcie.

    Le contenu d'une iframe n'est pas attribue a la page parente par Google.
    Sans texte et liste HTML reels autour, l'article serait vide pour le SEO.
    """
    raw = json.load(open("schedule.json", encoding="utf-8"))
    nom = {t: TEAMS[t][0] for t in TEAMS}

    # premier match de chaque franchise : 30 lignes, 60 mentions d'equipes
    ouvertures = []
    for tri in sorted(TEAMS, key=lambda t: TEAMS[t][0]):
        g = raw[tri]["games"][0]
        adv = nom[OPP_TO_TRI[g["opp"]]]
        lieu = f"à l’extérieur chez les {adv}" if g["away"] else f"à domicile contre les {adv}"
        ouvertures.append(
            f"    <li><strong>{nom[tri]}</strong> — {fr_date(g['date'])} "
            f"à {g['time'].replace(':', 'h')}, {lieu}.</li>")

    # dates a retenir, derivees des donnees
    tous = sorted({(g["date"], g["time"]) for t in raw.values() for g in t["games"]})
    premier, dernier = tous[0][0], tous[-1][0]
    h_premier = tous[0][1].replace(":", "h")
    # affiche du match d'ouverture (le PDF donne un 3:00 PM ET sur NBC,
    # soit 21h00 en France : c'est un match en prime time, pas un match de nuit)
    ouv = [(tri, g) for tri, t in raw.items() for g in t["games"]
           if g["date"] == premier and not g["away"]][0]
    affiche = f"{nom[ouv[0]]} – {nom[OPP_TO_TRI[ouv[1]['opp']]]}"
    paris = next(g for g in raw["SAS"]["games"] if g.get("venue", "").endswith("PARIS"))
    manch = next(g for g in raw["SAS"]["games"] if "MANCHESTER" in g.get("venue", ""))
    mex = next(g for g in raw["DEN"]["games"] if "MEXICO" in g.get("venue", ""))

    cles = [
        f"    <li><strong>Ouverture de la saison</strong> : {fr_date(premier)} à "
        f"{h_premier}, {affiche}.</li>",
        f"    <li><strong>NBA Paris Game</strong> : {fr_date(paris['date'])} à "
        f"{paris['time'].replace(':', 'h')}, {nom['SAS']} – {nom['NOP']} à l’Accor Arena.</li>",
        f"    <li><strong>NBA Manchester Game</strong> : {fr_date(manch['date'])} à "
        f"{manch['time'].replace(':', 'h')}, {nom['NOP']} – {nom['SAS']} à la Co-op Live.</li>",
        f"    <li><strong>NBA Mexico City Game</strong> : {fr_date(mex['date'])}, "
        f"{nom['DEN']} à l’Arena CDMX.</li>",
        f"    <li><strong>Fin de la saison régulière</strong> : nuit du "
        f"{fr_date(dernier)}.</li>",
    ]

    return f"""<!-- ============================================================
     Calendrier NBA 2026-2027 — bloc a coller dans un bloc HTML personnalise.
     Le texte et les listes ci-dessous sont le contenu indexe par Google :
     ne pas les supprimer, l'iframe seule ne rapporte aucun SEO.
     ============================================================ -->

<h2>Le calendrier NBA 2026-2027 franchise par franchise, en heure française</h2>

<p>La saison régulière NBA 2026-2027 s’ouvre le {fr_date(premier)} avec
{affiche}, et se termine dans la nuit du {fr_date(dernier)}. Bonne nouvelle pour les
suiveurs français : ce match d’ouverture est programmé à <strong>{h_premier}</strong>,
soit en prime time chez nous et non au milieu de la nuit. Chacune des 30 franchises
dispute 82 matchs, dont 41 à domicile et 41 à l’extérieur. Le calendrier ci-dessous
permet de sélectionner une équipe et d’afficher l’intégralité de son programme, avec
pour chaque rencontre l’adversaire, le lieu et l’horaire.</p>

<p><strong>Tous les horaires sont donnés en heure française.</strong> La NBA publie
son calendrier en heure de la côte Est américaine : un match programmé en soirée aux
États-Unis se joue donc au milieu de la nuit en France, et il est ici daté au jour
français, celui où vous le regardez. L’écart varie entre cinq et six heures selon la
période, les États-Unis et l’Europe ne changeant pas d’heure aux mêmes dates.</p>

<p>Deux rencontres de début décembre restent à programmer : elles dépendent du
parcours de chaque équipe en Emirates NBA Cup, dont les matchs de poule sont
signalés dans le calendrier.</p>

<h3>Les dates à retenir de la saison NBA 2026-2027</h3>

<ul>
{chr(10).join(cles)}
</ul>

<h3>Calendrier interactif : choisissez votre franchise</h3>

<iframe id="busa-nba-cal"
        src="{PAGES_URL}"
        title="Calendrier NBA 2026-2027 match par match, franchise par franchise, en heure française"
        loading="lazy"
        scrolling="no"
        referrerpolicy="strict-origin-when-cross-origin"
        style="display:block;margin:0 auto;width:100%;max-width:640px;
               min-height:{IFRAME_MIN_H}px;border:0;overflow:hidden"></iframe>

<script>
/* Ajuste la hauteur de l'iframe a son contenu (evite le double-scroll mobile).
   Ameliration progressive : si ce script est filtre par WordPress, l'iframe
   reste lisible grace au min-height ci-dessus. */
(function(){{
  var ORIGIN = '{PAGES_ORIGIN}';
  var frame  = document.getElementById('busa-nba-cal');
  window.addEventListener('message', function(e){{
    if (e.origin !== ORIGIN) return;                 /* origine de confiance */
    var d = e.data;
    if (!d || d.type !== 'busa-nba-height') return;
    var h = parseInt(d.height, 10);
    if (!h || h < 1) return;                         /* hauteur valide */
    if (!frame) frame = document.getElementById('busa-nba-cal');
    if (!frame) return;
    frame.style.height = h + 'px';
    frame.style.minHeight = '0';                     /* le plancher a servi */
  }}, false);
}})();
</script>

<h3>Le premier match de chaque franchise NBA en 2026-2027</h3>

<ul>
{chr(10).join(ouvertures)}
</ul>
"""


def main():
    linked = make_fragment(inline=False)    # logos servis en fichiers
    inline = make_fragment(inline=True)     # logos embarques en data-URI
    Path("embed-wordpress.html").write_text(build_embed(), encoding="utf-8")

    Path("widget-wordpress.html").write_text(linked, encoding="utf-8")
    Path("widget-wordpress-inline.html").write_text(inline, encoding="utf-8")

    # l'apercu en Artifact n'a pas d'hebergement d'assets : logos embarques
    Path("artifact.html").write_text(TITLE + PAGE_PAD + inline, encoding="utf-8")

    # apercu local : les logos sont a cote, en chemin relatif
    Path("nba-calendrier-2026-27.html").write_text(
        "<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        + TITLE + PAGE_PAD + "</head>\n<body>\n" + linked + "</body>\n</html>\n",
        encoding="utf-8")

    # cible de l'iframe, publiee sur GitHub Pages.
    # noindex : le contenu doit etre attribue a l'article BasketUSA, pas a
    # github.io — sans quoi on cree une page concurrente en duplicate.
    Path("index.html").write_text(
        "<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        "<meta name=\"robots\" content=\"noindex,follow\">\n"
        + TITLE + "</head>\n<body>\n" + linked + IFRAME_CSS + IFRAME_JS
        + "</body>\n</html>\n",
        encoding="utf-8")

    logos = len([t for t in TEAMS if logo_src(t, False)])
    print(f"logos cables : {logos}/30")
    for f in ("widget-wordpress.html", "widget-wordpress-inline.html"):
        print(f"{f}: {Path(f).stat().st_size/1024:.0f} Ko")


if __name__ == "__main__":
    main()
