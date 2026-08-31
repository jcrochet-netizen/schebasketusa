(function(){
  var CLUBS=__CLUBS__, SCHED=__SCHED__;
  var EPOCH=Date.UTC(2026,7,1), DAY=864e5;
  var JOURS=['dim.','lun.','mar.','mer.','jeu.','ven.','sam.'];
  var MOIS=['janvier','février','mars','avril','mai','juin','juillet',
            'août','septembre','octobre','novembre','décembre'];
  // abreviations françaises usuelles (mars, mai, juin, août ne s'abregent pas)
  var MOIS_AB=['janv.','févr.','mars','avr.','mai','juin','juil.',
               'août','sept.','oct.','nov.','déc.'];

  var root=document.getElementById('busaL1');
  var sel=document.getElementById('l1Club');
  var list=document.getElementById('l1List');
  var btns=root.querySelectorAll('.l1-filters button');
  var filtre='all', courant='PSG';

  var now=new Date();
  var jourJ=Math.round((Date.UTC(now.getFullYear(),now.getMonth(),now.getDate())-EPOCH)/DAY);

  CLUBS.forEach(function(c){
    var o=document.createElement('option');
    o.value=c[0]; o.textContent=c[1]; sel.appendChild(o);
  });

  function idx(code){
    for(var i=0;i<CLUBS.length;i++){ if(CLUBS[i][0]===code) return i; }
    return 0;
  }

  function sombre(){
    var de=document.documentElement;
    if(root.getAttribute('data-busa-theme')==='light') return false;
    if(de.getAttribute('data-theme')==='dark') return true;
    if(de.getAttribute('data-theme')==='light') return false;
    return window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  function peindre(){
    var c=CLUBS[idx(courant)], d=sombre();
    root.style.setProperty('--l1-club', d?c[5]:c[3]);
    root.style.setProperty('--l1-club-rgb', d?c[6]:c[4]);
  }

  function ecusson(){
    var c=CLUBS[idx(courant)], el=document.getElementById('l1Crest');
    el.className='l1-crest';
    if(c[7]){
      var img=new Image();
      img.alt=''; img.loading='lazy'; img.decoding='async';
      img.onerror=function(){ el.className='l1-crest'; el.textContent=c[0]; };
      img.src=c[7];
      el.textContent='';
      el.className='l1-crest has-logo'+(c[8]?' chip-dark':'');
      el.appendChild(img);
    } else {
      el.textContent=c[0];
    }
  }

  function rendre(){
    var matchs=SCHED[courant]||[];
    var nh=0,na=0;
    matchs.forEach(function(g){ g[1]?na++:nh++; });
    document.getElementById('l1Na').textContent=matchs.length;
    document.getElementById('l1Nh').textContent=nh;
    document.getElementById('l1Ne').textContent=na;
    document.getElementById('l1Name').textContent=CLUBS[idx(courant)][1];

    var vus=matchs.filter(function(g){
      return filtre==='all' || (filtre==='home')===!g[1];
    });
    if(!vus.length){ list.innerHTML='<p class="l1-empty">Aucun match.</p>'; return; }

    var suivant=-1;
    for(var i=0;i<vus.length;i++){ if(vus[i][3]>=jourJ){ suivant=i; break; } }

    var html='', moisCourant=-1;
    vus.forEach(function(g,i){
      var d=new Date(EPOCH+g[3]*DAY), mo=d.getUTCMonth();
      if(mo!==moisCourant){
        moisCourant=mo;
        var lbl=MOIS[mo].charAt(0).toUpperCase()+MOIS[mo].slice(1);
        html+='<div class="l1-month"><h3>'+lbl+' '+d.getUTCFullYear()+'</h3></div>';
      }
      var ext=!!g[1], adv=CLUBS[g[0]];
      var jj=d.getUTCDate();
      var iso=d.getUTCFullYear()+'-'+(mo+1<10?'0':'')+(mo+1)+'-'+(jj<10?'0':'')+jj;
      var cls='l1-g'+(ext?'':' is-home')
             +(g[3]<jourJ?' is-past':'')+(i===suivant?' is-next':'');
      html+='<li class="'+cls+'">'
          + '<span class="l1-j">J'+g[2]+'</span>'
          + '<span class="l1-ico" aria-hidden="true">'+(ext?'✈️':'🏠')+'</span>'
          + '<span class="l1-opp"><span class="l1-sr">'
          +   (ext?'À l’extérieur chez ':'À domicile contre ')+'</span>'
          +   '<span class="l1-name l1-full">'+adv[1]+'</span>'
          +   '<span class="l1-name l1-short">'+adv[2]+'</span></span>'
          + '<time class="l1-date" datetime="'+iso+'">'
          +   JOURS[d.getUTCDay()]+' '+(jj===1?'1er':jj)+' '+MOIS_AB[mo]+'</time>'
          + '</li>';
    });
    list.innerHTML='<ol>'+html+'</ol>';
  }

  function choisir(code,pousser){
    if(!SCHED[code]) return;
    courant=code; sel.value=code; peindre(); ecusson(); rendre();
    if(pousser && history.replaceState) history.replaceState(null,'','#'+code);
  }

  sel.addEventListener('change',function(){ choisir(sel.value,true); list.scrollTop=0; });

  Array.prototype.forEach.call(btns,function(b){
    b.addEventListener('click',function(){
      filtre=b.getAttribute('data-f');
      Array.prototype.forEach.call(btns,function(x){
        x.setAttribute('aria-pressed', x===b?'true':'false');
      });
      rendre(); list.scrollTop=0;
    });
  });

  if(window.matchMedia){
    var mq=window.matchMedia('(prefers-color-scheme: dark)');
    (mq.addEventListener?mq.addEventListener.bind(mq,'change'):mq.addListener.bind(mq))(peindre);
  }

  function voulu(){
    var m=(location.search||'').match(/[?&]club=([A-Za-z]{2,4})/);
    var c=(m?m[1]:(location.hash||'').replace('#','')).toUpperCase();
    return SCHED[c]?c:'PSG';
  }
  choisir(voulu(),false);
  window.addEventListener('hashchange',function(){
    var h=(location.hash||'').replace('#','').toUpperCase();
    if(SCHED[h]) choisir(h,false);
  });
})();
