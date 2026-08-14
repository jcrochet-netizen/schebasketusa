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

# Page servie dans l'iframe : le widget epouse la hauteur donnee a l'iframe,
# c'est la liste qui prend la place restante. N'importe quelle hauteur marche.
IFRAME_CSS = """<style>
html,body{height:100%;margin:0;background:transparent;}
.busa-nba{height:100%;max-width:none;border:0;border-radius:0;
  display:flex;flex-direction:column;}
.busa-nba .bn-list{flex:1 1 auto;max-height:none;}
</style>
"""


def main():
    linked = make_fragment(inline=False)    # logos servis en fichiers
    inline = make_fragment(inline=True)     # logos embarques en data-URI

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

    # cible de l'iframe, publiee sur GitHub Pages
    Path("index.html").write_text(
        "<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        "<meta name=\"robots\" content=\"noindex\">\n"
        + TITLE + IFRAME_CSS + "</head>\n<body>\n" + linked + "</body>\n</html>\n",
        encoding="utf-8")

    logos = len([t for t in TEAMS if logo_src(t, False)])
    print(f"logos cables : {logos}/30")
    for f in ("widget-wordpress.html", "widget-wordpress-inline.html"):
        print(f"{f}: {Path(f).stat().st_size/1024:.0f} Ko")


if __name__ == "__main__":
    main()
