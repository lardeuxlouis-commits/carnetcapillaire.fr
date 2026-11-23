window.CC_LANCEMENT=true;
/* Carnet capillaire : micro-interactions (apparition douce, fermeture du menu), formulaire e-mail, encart et barre collante de l'accueil.
   Aucun traceur. localStorage seulement pour se souvenir qu'un encart a été vu ou fermé (try/catch partout). */
(function(){
  var d=document;d.documentElement.classList.add("js");
  var els=d.querySelectorAll(".rv");
  if("IntersectionObserver" in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target);}});},{rootMargin:"0px 0px -8% 0px"});
    els.forEach(function(el){io.observe(el);});
  }else{els.forEach(function(el){el.classList.add("in");});}
  var m=d.querySelector(".menu");
  if(m){d.addEventListener("click",function(e){if(m.open&&!m.contains(e.target))m.open=false;});
    d.addEventListener("keydown",function(e){if(e.key==="Escape"&&m.open){m.open=false;m.querySelector("summary").focus();}});}

  function lire(k){try{return localStorage.getItem(k);}catch(e){return null;}}
  function ecrire(k,v){try{localStorage.setItem(k,v);}catch(e){}}

  /* ---------- Capture e-mail ----------
     TODO e-mail : brancher ENDPOINT sur Brevo (gratuit jusqu'à 300 e-mails/jour) ou Kit.
     Ne JAMAIS mettre la clé API Brevo dans ce fichier : passer par une petite fonction serveur (VPS ou fonction serverless)
     qui appelle POST https://api.brevo.com/v3/contacts/doubleOptinConfirmation (double opt-in, template de confirmation,
     redirectionUrl = https://carnetcapillaire.fr/bienvenue/), ou utiliser l'URL d'un formulaire Brevo hébergé.
     Tant que ENDPOINT vaut null : démo, rien n'est envoyé. */
  var ENDPOINT=null; // TODO e-mail : "/api/inscription" (factice) -> URL de la fonction serveur Brevo ou Kit
  var n=0;
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
  function formHtml(o){
    n++;var id="cap"+n;
    return '<form class="cap" novalidate data-src="'+esc(o.src||"site")+'">'+
      '<p class="cap-t">'+esc(o.titre||"Reçois le mini-guide gratuit")+'</p>'+
      '<p class="cap-s">'+esc(o.sous||"« Les 5 erreurs qui abîment tes cheveux », 5 pages simples, dans ta boîte mail.")+'</p>'+
      '<div class="cap-f"><div><label for="'+id+'-e">Ton e-mail</label><input id="'+id+'-e" name="email" type="email" required autocomplete="email" inputmode="email" placeholder="prenom@exemple.fr"></div>'+
      '<div><label for="'+id+'-p">Ton prénom <span>(facultatif)</span></label><input id="'+id+'-p" name="prenom" type="text" autocomplete="given-name" maxlength="40"></div></div>'+
      '<p class="cap-hp" aria-hidden="true"><label>Ne pas remplir<input name="site" tabindex="-1" autocomplete="off"></label></p>'+
      '<label class="cap-ok"><input type="checkbox" name="consent" required> <span>J\'accepte de recevoir '+esc(o.quoi||"le mini-guide")+' puis les e-mails de conseils de Carnet capillaire (5 e-mails sur 10 jours, ensuite une lettre de temps en temps, avec parfois des liens affiliés signalés). Désinscription en un clic dans chaque e-mail. <a href="/mentions-legales/#confidentialite">Politique de confidentialité</a></span></label>'+
      '<button type="submit" class="btn">'+esc(o.bouton||"Recevoir le mini-guide")+'</button>'+
      '<p class="cap-n">Tu recevras d\'abord un e-mail pour confirmer ton adresse. Pas de spam, jamais de revente.</p>'+
      '<p class="cap-msg" role="status" aria-live="polite"></p></form>';
  }
  // MODE LANCEMENT (window.CC_LANCEMENT, injecté par build.py) : aucun formulaire e-mail tant que Brevo n'est pas branché
  if(window.CC_LANCEMENT){d.querySelectorAll("[data-capture],.cap-pop").forEach(function(el){el.remove();});}
  else window.CCform=formHtml;
  d.querySelectorAll("[data-capture]").forEach(function(el){
    el.innerHTML=formHtml({src:el.getAttribute("data-capture"),titre:el.getAttribute("data-titre"),sous:el.getAttribute("data-sous")});
  });
  d.addEventListener("submit",function(e){
    var f=e.target;if(!f.classList||!f.classList.contains("cap"))return;
    e.preventDefault();
    var msg=f.querySelector(".cap-msg"),em=f.email.value.trim(),btn=f.querySelector("button");
    msg.className="cap-msg";
    if(f.site.value)return; // robot
    if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em)){msg.textContent="Vérifie ton adresse e-mail.";msg.classList.add("err");f.email.focus();return;}
    if(!f.consent.checked){msg.textContent="Coche la case pour accepter de recevoir les e-mails.";msg.classList.add("err");f.consent.focus();return;}
    // Résultat du test (si le formulaire est dans un résultat) : envoyé pour personnaliser l'e-mail J0
    var res=f.closest(".qbody"),resume="",prods=[],guide="";
    if(res){var t=res.querySelector(".res-type,.res-top h2,.res-top h3");resume=t?t.textContent.trim():"";
      res.querySelectorAll("[data-prod]").forEach(function(p){prods.push(p.getAttribute("data-prod"));});
      var gd=res.querySelector("[data-guide]");guide=gd?gd.getAttribute("data-guide"):"";}
    var data={email:em,prenom:f.prenom.value.trim(),consentement:true,texte_consentement:f.querySelector(".cap-ok span").textContent,
      source:f.getAttribute("data-src"),resultat:resume,produits:prods,guide:guide,page:location.pathname,date:new Date().toISOString()};
    var ok=function(){ecrire("cc-inscrit","1");
      f.innerHTML='<p class="cap-t">Presque fini, vérifie ta boîte mail</p><p class="cap-s">Clique sur le lien de confirmation que tu vas recevoir : ton '+(res?"résultat et le mini-guide arrivent":"mini-guide arrive")+' juste après. Rien reçu ? Regarde dans les indésirables ou l\'onglet Promotions.</p>'+
        (ENDPOINT?"":'<p class="cap-n">Version de démonstration : aucun e-mail n\'est envoyé pour l\'instant.</p>');
      var p=d.querySelector(".cap-pop");if(p&&!p.contains(f))p.hidden=true;};
    if(!ENDPOINT){ok();return;}
    btn.disabled=true;btn.textContent="Envoi…";
    fetch(ENDPOINT,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)})
      .then(function(r){if(!r.ok)throw 0;ok();})
      .catch(function(){btn.disabled=false;btn.textContent="Réessayer";msg.textContent="L'envoi n'a pas marché. Réessaie dans un instant.";msg.classList.add("err");});
  });

  /* ---------- Accueil : encart mini-guide après 60 % de scroll (une seule fois, fermable) ---------- */
  var pop=d.querySelector(".cap-pop");
  if(pop&&!lire("cc-pop-vu")&&!lire("cc-inscrit")){
    var onS=function(){var h=d.documentElement,r=(h.scrollTop||d.body.scrollTop)/((h.scrollHeight-h.clientHeight)||1);
      if(r>=0.6){window.removeEventListener("scroll",onS);pop.hidden=false;ecrire("cc-pop-vu","1");}};
    window.addEventListener("scroll",onS,{passive:true});
    pop.querySelector(".pop-x").addEventListener("click",function(){pop.hidden=true;});
    d.addEventListener("keydown",function(e){if(e.key==="Escape")pop.hidden=true;});
  }

  /* ---------- Accueil : barre collante mobile, après le hero, fermable ---------- */
  var st=d.querySelector(".stick"),hero=d.querySelector(".hero");
  if(st&&hero&&"IntersectionObserver" in window&&!lire("cc-stick-x")){
    new IntersectionObserver(function(es){st.classList.toggle("on",!es[0].isIntersecting);}).observe(hero);
    st.querySelector(".stick-x").addEventListener("click",function(){st.remove();ecrire("cc-stick-x","1");});
  }
})();

// Statistiques GoatCounter (sans cookie) : événements de conversion
window.cc_evt=function(n){try{if(window.goatcounter&&window.goatcounter.count)window.goatcounter.count({path:n,title:n,event:true})}catch(e){}};
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a[href]");if(!a)return;var h=a.getAttribute("href")||"";
if(/^https?:\/\//.test(h)&&h.indexOf(location.host)<0)cc_evt("clic-produit-"+(a.hostname||"").replace(/^www\./,""));});

// Vidéos plus bas dans la page : chargées seulement quand elles approchent de l'écran
(function(){var v=document.querySelectorAll("video[data-lazyvid]");if(!v.length)return;function go(x){x.querySelectorAll("source[data-src]").forEach(function(s){s.src=s.getAttribute("data-src")});x.load();var p=x.play();if(p&&p.catch)p.catch(function(){})}
if(!("IntersectionObserver" in window)){v.forEach(go);return}var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){go(e.target);o.unobserve(e.target)}})},{rootMargin:"300px"});v.forEach(function(x){o.observe(x)})})();

// Onglets simples (classement des shampoings) : [data-tabs] > [role=tab] aria-controls ; flèches gauche/droite
(function(){document.querySelectorAll("[data-tabs]").forEach(function(l){var t=[].slice.call(l.querySelectorAll("[role=tab]"));function on(x,f){t.forEach(function(b){var s=b===x;b.setAttribute("aria-selected",s);b.tabIndex=s?0:-1;document.getElementById(b.getAttribute("aria-controls")).hidden=!s});if(f)x.focus()}
t.forEach(function(b,i){b.addEventListener("click",function(){on(b)});b.addEventListener("keydown",function(e){var d=e.key==="ArrowRight"?1:e.key==="ArrowLeft"?-1:0;if(d){e.preventDefault();on(t[(i+d+t.length)%t.length],true)}})})})})();
