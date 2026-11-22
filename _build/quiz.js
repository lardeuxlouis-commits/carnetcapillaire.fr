/* Quiz « Quel est ton type de cheveux ? » : 9 questions, calcul 100 % local.
   Texture (raides à crépus), épaisseur, cuir chevelu, porosité, souci principal.
   Aucune donnée envoyée ni stockée (pas de cookie, pas de localStorage).
   Capture e-mail en fin de résultat (site.js, case de consentement non cochée, double opt-in) : seule donnée envoyée, et seulement si la personne la remplit. */
(function () {
  var root = document.getElementById("quiz");
  if (!root) return;

  function curl(n) { // petite illustration SVG de la forme, n = 0 (raide) à 6 (zigzag très serré)
    var paths = [
      "M14 4v40",
      "M6 8c10 6 -4 14 6 20s-4 14 6 18",
      "M6 6c14 4 -8 12 6 18s-8 12 6 18",
      "M14 4c-10 4 10 8 0 12s10 8 0 12s10 8 0 12",
      "M14 4c-7 2 7 5 0 7s7 5 0 7s7 5 0 7s7 5 0 7s7 5 0 7",
      "M10 4l6 3l-6 3l6 3l-6 3l6 3l-6 3l6 3l-6 3l6 3l-6 3l6 3l-6 3",
      "M10 4l5 2l-5 2l5 2l-5 2l5 2l-5 2l5 2l-5 2l5 2l-5 2l5 2l-5 2l5 2l-5 2l5 2l-5 2"
    ];
    return '<svg viewBox="0 0 28 48" aria-hidden="true"><path d="' + paths[n] + '" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  }

  var Q = [
    { id: "forme", t: "Sans produit, une fois secs, à quoi ressemblent tes cheveux ?", h: "Regarde une mèche du milieu de la tête, lavée la veille et séchée à l'air libre, sans lisseur.",
      o: [["Raides, sans aucune ondulation", "", 1.2, 0], ["Une légère vague en S, presque raide aux racines", "", 2.1, 1], ["Des S bien marqués, qui frisottent vite", "", 2.7, 2],
          ["Des boucles souples en spirale, larges comme une craie", "", 3.05, 3], ["Des boucles serrées, de la taille d'un crayon", "", 3.6, 4],
          ["Des ressorts très serrés ou de petits zigzags", "", 4.2, 5], ["Des Z très serrés, on voit à peine la boucle", "", 4.6, 6]] },
    { id: "retract", t: "Entre mouillés et secs, ils raccourcissent de combien ?", h: "C'est la rétraction : plus elle est forte, plus la boucle est serrée. Cheveux raides : choisis la première réponse.",
      o: [["À peine, ils gardent presque la même longueur", "", -0.2], ["Un peu, d'un quart environ", "", 0], ["Beaucoup, d'un tiers environ", "", 0.15], ["Énormément, ils perdent la moitié ou plus", "", 0.3]] },
    { id: "epais", t: "Un seul cheveu entre tes doigts, il est plutôt…", h: "Compare avec un fil à coudre : plus fin, pareil ou plus épais ?",
      o: [["Fin, je le sens à peine", "Plus fin qu'un fil", "fin"], ["Moyen", "Comme un fil à coudre", "moyen"], ["Épais, bien présent", "Plus épais qu'un fil", "epais"]] },
    { id: "cuir", t: "Et ton cuir chevelu, deux jours après le lavage ?", h: "C'est lui qui décide du shampoing, bien plus que tes longueurs.",
      o: [["Plutôt équilibré", "", "ok"], ["Racines déjà grasses, parfois dès le lendemain", "", "gras"], ["Il tiraille, il est sec", "", "sec"],
          ["J'ai des pellicules", "", "pellicules"], ["Il démange fort, ou il y a des plaques depuis un moment", "", "alerte"]] },
    { id: "sechage", t: "Après le lavage, tes cheveux sèchent…", h: "À l'air libre, sans sèche-cheveux.",
      o: [["Très lentement, encore humides le soir", "", 0], ["En quelques heures", "", 1], ["Très vite, parfois en moins d'une heure", "", 2]] },
    { id: "produit", t: "Quand tu appliques un après-shampoing ou une crème…", h: "",
      o: [["Il reste en surface, mes cheveux paraissent vite chargés", "", 0], ["Il pénètre bien, sans trop alourdir", "", 1], ["Il disparaît, mes cheveux ont soif presque aussitôt", "", 2]] },
    { id: "toucher", t: "Au toucher, une longueur sèche est plutôt…", h: "Fais glisser tes doigts de la racine vers la pointe.",
      o: [["Lisse et glissante", "", 0], ["Douce, avec quelques zones rêches", "", 1], ["Rêche, un peu cassante, avec des pointes abîmées", "", 2]] },
    { id: "couleur", t: "Tes cheveux sont-ils colorés, décolorés ou lissés ?", h: "Coloration, mèches, balayage, lissage brésilien, ou lisseur plusieurs fois par semaine.",
      o: [["Non, ils sont naturels", "", "non"], ["Oui, colorés ou méchés", "", "couleur"], ["Oui, décolorés", "", "deco"], ["Oui, lissage brésilien ou lisseur fréquent", "", "lissage"]] },
    { id: "souci", t: "Ce qui t'embête le plus en ce moment ?", h: "Une seule réponse, la plus importante pour toi.",
      o: [["Ils regraissent trop vite", "", "gras"], ["Ils sont secs et ternes", "", "secheresse"], ["Ils cassent, les pointes s'abîment", "", "casse"],
          ["Pas de volume, ils sont plats", "", "volume"], ["Les frisottis, des boucles peu définies", "", "frisottis"],
          ["Mes premiers cheveux blancs", "", "blancs"], ["J'ai l'impression d'en perdre beaucoup", "", "chute"]] }
  ];

  var GROUPES = {
    raides: { nom: "raides", page: "/cheveux-raides/", texte: "Lisses, brillants, parfois plats : ton guide complet." },
    ondules: { nom: "ondulés", page: "/cheveux-ondules/", texte: "Des vagues à révéler sans les alourdir." },
    boucles: { nom: "bouclés", page: "/cheveux-boucles/", texte: "Comprendre tes boucles et leurs besoins." },
    frises: { nom: "frisés", page: "/cheveux-frises/", texte: "Des boucles serrées à hydrater sans relâche." },
    crepus: { nom: "crépus", page: "/cheveux-crepus/", texte: "Douceur, hydratation et protection." }
  };
  var PB = {
    gras: ["/cheveux-gras/", "Cheveux gras", "Pourquoi ça regraisse, et quel shampoing choisir."],
    secheresse: ["/cheveux-secs/", "Cheveux secs", "Les causes, la routine et le bon shampoing."],
    sec: ["/cheveux-secs/", "Cheveux et cuir chevelu secs", "Les gestes qui évitent de tirailler."],
    casse: ["/cheveux-abimes/", "Cheveux qui cassent", "Casse ou chute, et les gestes qui protègent."],
    volume: ["/cheveux-fins/", "Cheveux fins ou épais", "Du volume sans alourdir."],
    frisottis: ["/routine-cheveux-boucles/", "La routine boucles", "Définir et limiter les frisottis."],
    blancs: ["/cheveux-blancs/", "Cheveux blancs", "Les assumer ou les couvrir, henné compris."],
    chute: ["/chute-de-cheveux-femme/", "Chute de cheveux", "Ce qui est normal, et quand consulter."],
    pellicules: ["/cuir-chevelu-qui-gratte/", "Pellicules et démangeaisons", "Les gestes doux, et quand consulter."],
    alerte: ["/cuir-chevelu-qui-gratte/", "Pellicules et démangeaisons", "Les signes qui doivent faire consulter."]
  };

  var rep = {}, i = 0;
  root.innerHTML = '<div class="qprog" aria-hidden="true"><i></i></div><div class="qbody" aria-live="polite"></div>';
  var bar = root.querySelector(".qprog i"), body = root.querySelector(".qbody");

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function raides() { return rep.forme && rep.forme.v < 1.5; }
  function suivante(k) { // les cheveux raides n'ont pas de rétraction : on saute la question 2
    var n = k + 1;
    if (Q[n] && Q[n].id === "retract" && raides()) { rep.retract = { k: 0, v: -0.2 }; n++; }
    return n;
  }
  function precedente(k) {
    var n = k - 1;
    if (Q[n] && Q[n].id === "retract" && raides()) n--;
    return Math.max(0, n);
  }

  function show() {
    var q = Q[i];
    bar.style.width = (i / Q.length * 100) + "%";
    var h = '<div class="qfade"><p class="qmeta"><span>Question ' + (i + 1) + " sur " + Q.length + "</span><span>" + Math.round(i / Q.length * 100) + ' %</span></p>' +
      '<h2 id="qt">' + esc(q.t) + "</h2>" + (q.h ? '<p class="qhelp">' + esc(q.h) + "</p>" : "") + '<div class="qopts" role="group" aria-labelledby="qt">';
    q.o.forEach(function (o, k) {
      var sel = rep[q.id] && rep[q.id].k === k;
      h += '<button type="button" class="qopt" data-k="' + k + '" aria-pressed="' + (sel ? "true" : "false") + '">' + (q.id === "forme" ? curl(o[3]) : "") +
        "<span>" + esc(o[0]) + (o[1] ? "<small>" + esc(o[1]) + "</small>" : "") + "</span></button>";
    });
    h += '</div><div class="qnav"><button type="button" class="qback"' + (i === 0 ? " hidden" : "") + ">← Question précédente</button></div></div>";
    body.innerHTML = h;
    var t = body.querySelector("h2"); t.setAttribute("tabindex", "-1"); if (i > 0) t.focus({ preventScroll: true });
    body.querySelectorAll(".qopt").forEach(function (b) {
      b.addEventListener("click", function () {
        var k = +b.getAttribute("data-k"); rep[q.id] = { k: k, v: q.o[k][2] };
        b.setAttribute("aria-pressed", "true");
        setTimeout(function () { i = suivante(i); i < Q.length ? show() : result(); }, 180);
      });
    });
    body.querySelector(".qback").addEventListener("click", function () { if (i > 0) { i = precedente(i); show(); } });
  }

  function typeDe(score, ep) {
    if (score < 1.5) return { fin: "1A", moyen: "1B", epais: "1C" }[ep];
    var seuils = [[2.3, "2A"], [2.6, "2B"], [2.9, "2C"], [3.2, "3A"], [3.45, "3B"], [3.75, "3C"], [4.1, "4A"], [4.45, "4B"]];
    for (var s = 0; s < seuils.length; s++) if (score < seuils[s][0]) return seuils[s][1];
    return "4C";
  }

  function result() {
    bar.style.width = "100%";
    var ep = rep.epais.v, cuir = rep.cuir.v, souci = rep.souci.v, chim = rep.couleur.v;
    var type = typeDe(rep.forme.v + rep.retract.v, ep);
    var g = type[0] === "1" ? "raides" : type[0] === "2" ? "ondules" : (type === "3A" || type === "3B") ? "boucles" : (type === "3C" || type === "4A") ? "frises" : "crepus";
    var G = GROUPES[g];
    var p = rep.sechage.v + rep.produit.v + rep.toucher.v + (chim === "deco" ? 1 : 0); // 0 à 7
    var poro = p <= 1 ? "faible" : p <= 4 ? "moyenne" : "forte";
    var texture = g === "raides" || g === "ondules" ? "lisse" : "boucle";

    var lavage = {
      raides: "Shampoing doux dès que tes racines le demandent, même tous les jours si besoin, en massant le cuir chevelu. La mousse qui coule suffit pour les longueurs.",
      ondules: "Shampoing doux sans sulfate 2 à 3 fois par semaine, en massant surtout les racines.",
      boucles: "Shampoing doux ou co-wash 1 à 2 fois par semaine. Un clarifiant une fois par mois si tes boucles paraissent chargées.",
      frises: "Pré-poo à l'huile 20 minutes avant, puis shampoing doux une fois par semaine environ.",
      crepus: "Pré-poo à l'huile, puis shampoing doux par sections, une fois par semaine ou tous les 10 jours." }[g];
    if (cuir === "gras") lavage = texture === "lisse"
      ? "Shampoing doux pour cuir chevelu gras, appliqué seulement sur les racines, aussi souvent que nécessaire. Laver souvent avec un produit doux n'est pas un problème."
      : "Shampoing doux pour cuir chevelu gras sur les racines un peu plus souvent, et soins riches seulement sur les longueurs.";
    if (cuir === "pellicules") lavage += " Pour les pellicules, un shampoing antipelliculaire de pharmacie en alternance aide souvent.";
    var soin = { faible: "Après-shampoing léger sur les longueurs, bien rincé. Pour le masque, un bonnet chaud 15 minutes aide les soins à pénétrer.",
      moyenne: "Après-shampoing à chaque lavage sur les longueurs, et un masque hydratant une fois par semaine.",
      forte: "Masque riche à chaque lavage sur les longueurs. Glisse un soin aux protéines toutes les 2 à 4 semaines pour renforcer la fibre." }[poro];
    if (ep === "fin" && poro !== "forte") soin = "Après-shampoing léger, seulement des mi-longueurs aux pointes. Un masque toutes les deux semaines suffit, pour ne pas alourdir.";
    var hydra = texture === "lisse"
      ? (ep === "fin" ? "Un spray démêlant léger sur les pointes, rien de plus. Les huiles, à peine une goutte sur cheveux secs." : "Un soin sans rinçage en crème légère sur les pointes, et une goutte d'huile en finition si elles sont sèches.")
      : (g === "crepus" || g === "frises"
        ? (poro === "faible" ? "Méthode LCO : un liquide (eau ou leave-in), une crème, puis une goutte d'huile légère pour sceller." : "Méthode LOC : un liquide, une huile, puis une crème pour garder l'hydratation plusieurs jours.")
        : (ep === "fin" ? "Leave-in en spray ou en lait, très peu, sur cheveux trempés." : "Leave-in crème légère sur cheveux trempés, mèche par mèche."));
    var coiff = {
      raides: "Sèche d'abord les racines tête en bas, à température moyenne, avec un protecteur thermique si tu utilises un lisseur.",
      ondules: "Mousse ou gel léger, scrunch de bas en haut, séchage au diffuseur à basse température.",
      boucles: "Gel en « praying hands », scrunch, plopping 10 à 15 minutes dans un tee-shirt, puis diffuseur ou air libre.",
      frises: "Gel ou crème définissante en sections, twist-out ou wash and go, et une taie en satin pour la nuit.",
      crepus: "Twist-out ou braid-out sur cheveux hydratés, coiffures protectrices, bonnet ou taie en satin la nuit." }[g];
    if (ep === "fin" && g !== "crepus" && g !== "raides") coiff += " Cheveux fins : préfère les textures légères pour ne pas les alourdir.";
    if (chim !== "non") coiff += " Cheveux " + ({ couleur: "colorés", deco: "décolorés", lissage: "lissés" })[chim] + " : protecteur thermique systématique, et chaleur au minimum.";

    var tips = { gras: "Contre les racines grasses : touche-les le moins possible dans la journée, et garde tes soins loin du cuir chevelu.",
      secheresse: "Contre la sécheresse : un masque une fois par semaine, et de l'eau tiède plutôt que très chaude.",
      casse: "Contre la casse : démêle seulement sous l'après-shampoing, aux doigts ou avec un peigne à dents larges, des pointes vers les racines.",
      volume: "Pour le volume : applique tes soins à partir de la mi-longueur, et sèche la tête à l'envers.",
      frisottis: "Contre les frisottis : essore avec un tee-shirt en coton plutôt qu'une serviette éponge, et touche le moins possible tes cheveux pendant le séchage.",
      blancs: "Pour les cheveux blancs : ils sont souvent plus secs, un soin nourrissant sur les longueurs les rend plus doux et plus brillants. Si tu veux les couvrir, fais toujours le test d'allergie 48 heures avant.",
      chute: "Perdre 50 à 100 cheveux par jour est normal. Si tu en perds nettement plus pendant plusieurs semaines, ou en plaques, parles-en à ton médecin : une routine ne règle pas une chute." }[souci];
    var cuirTxt = { ok: "", gras: "", sec: "Ton cuir chevelu tiraille : évite l'eau très chaude et les shampoings trop décapants.",
      pellicules: "Si tes pellicules persistent malgré un shampoing adapté, ou s'accompagnent de rougeurs, demande conseil à ton pharmacien ou à ton médecin.",
      alerte: "Des démangeaisons fortes ou des plaques qui durent ne relèvent pas d'une routine : parle-en à ton médecin ou à un dermatologue avant de changer de produits." }[cuir];

    // Guides proposés : texture, problème principal, cuir chevelu si différent, soin, porosité
    var liens = [[G.page, "Ton guide", "Cheveux " + G.nom, G.texte]];
    var pb = PB[souci];
    if (souci === "frisottis" && (g === "frises" || g === "crepus")) pb = ["/routine-cheveux-crepus/", "La routine crépus et frisés", "Le jour de lavage pas à pas."];
    if (souci === "frisottis" && g === "raides") pb = ["/cheveux-secs/", "Cheveux secs", "Les frisottis viennent souvent de longueurs assoiffées."];
    liens.push([pb[0], "Ton souci principal", pb[1], pb[2]]);
    if (cuir !== "ok" && PB[cuir] && PB[cuir][0] !== pb[0]) liens.push([PB[cuir][0], "Ton cuir chevelu", PB[cuir][1], PB[cuir][2]]);
    if ((ep === "fin" || ep === "epais") && pb[0] !== "/cheveux-fins/") liens.push(["/cheveux-fins/", "Cheveux " + (ep === "fin" ? "fins" : "épais"), "Fins ou épais", "Ce que ton épaisseur change pour tes soins."]);
    var shamp = chim === "lissage" ? ["/shampoing-apres-lissage-bresilien/", "Shampoings après lissage"]
      : g === "boucles" || g === "ondules" && cuir !== "gras" ? ["/meilleur-shampoing-cheveux-boucles/", "Shampoings pour boucles"]
      : g === "frises" || g === "crepus" ? ["/shampoing-cheveux-crepus-frises/", "Shampoings crépus et frisés"]
      : ["/meilleur-shampoing/", "Quel shampoing choisir"];
    liens.push([shamp[0], "Sélection", shamp[1], "Les produits que je te conseille de regarder."]);
    liens.push(["/porosite-cheveux/", "Porosité " + poro, "Ta porosité", "Ce qu'elle change pour tes soins."]);
    liens = liens.slice(0, 6);
    var cartes = liens.map(function (l) { return '<a class="lcard" href="' + l[0] + '"><span class="k">' + esc(l[1]) + "</span><h3>" + esc(l[2]) + "</h3><p>" + esc(l[3]) + "</p></a>"; }).join("");

    function prodsHtml() {
      if (!window.CC) return "";
      var tags = [];
      if (chim === "lissage") tags.push("lissage");
      if (cuir === "gras" || cuir === "pellicules" || cuir === "sec") tags.push(cuir === "sec" ? "sensible" : cuir);
      if (chim === "couleur" || chim === "deco") tags.push(chim === "deco" ? "abimes" : "couleur");
      if (souci === "blancs") tags.push("blancs");
      tags.push(g === "frises" ? "crepus" : g, ep === "fin" ? "fins" : ep === "epais" ? "epais" : "equilibre");
      if (souci === "secheresse" || souci === "casse") tags.push(souci === "casse" ? "abimes" : "sec");
      var oblig = chim === "lissage" ? "lissage" : cuir === "pellicules" ? "pellicules" : null;
      var sh = window.CC.top(tags, { n: 2, oblig: oblig });
      var soin = window.CC.top(tags.concat(["sec"]), { cats: ["masque", "soin"], n: 1 });
      return "<h3>Trois produits pour ton profil</h3>" + window.CC.cartes(sh.concat(soin));
    }
    var cuirChip = { ok: "Cuir chevelu équilibré", gras: "Cuir chevelu gras", sec: "Cuir chevelu sec", pellicules: "Pellicules", alerte: "Cuir chevelu à faire examiner" }[cuir];
    var alerte = [cuir === "alerte" ? cuirTxt : "", souci === "chute" ? tips : ""].filter(Boolean).join(" ");
    var h = '<div class="qfade"><div class="res-top"><p class="kicker" style="justify-content:center">Ton résultat</p><p class="res-type">' + type + "</p>" +
      '<h2 style="margin:0">Tu as probablement les cheveux ' + G.nom + "</h2>" +
      '<ul class="res-chips"><li>Type ' + type + "</li><li>Cheveux " + ({ fin: "fins", moyen: "moyens", epais: "épais" })[ep] + "</li><li>" + cuirChip + "</li><li>Porosité " + poro + "</li></ul></div>" +
      '<p class="qhelp" style="text-align:center">C\'est une estimation à partir de tes réponses, pas un diagnostic. Beaucoup de têtes mélangent deux types : c\'est normal.</p>' +
      (alerte ? '<p class="res-alert" role="note">' + esc(alerte) + "</p>" : "") +
      "<h3>Ta routine conseillée en 4 étapes</h3><ol class=\"res-routine\">" +
      "<li><b>Laver</b>" + esc(lavage) + "</li><li><b>Nourrir</b>" + esc(soin) + "</li><li><b>Hydrater</b>" + esc(hydra) + "</li><li><b>Coiffer</b>" + esc(coiff) + "</li></ol>" +
      (souci !== "chute" ? '<p class="astuce" style="margin:0"><strong>Le conseil du carnet :</strong> ' + esc(tips) + (cuir !== "alerte" && cuirTxt ? " " + esc(cuirTxt) : "") + "</p>" : "") +
      '<div class="res-links">' + cartes + "</div>" +
      prodsHtml() +
      // Offre : LE guide du type détecté (cheveux raides et fins -> guide des cheveux fins), puis le pack
      (window.CC ? window.CC.capture("quiz-type") + window.CC.offre(g === "raides" && ep === "fin" ? "fins" : g) : '<div class="res-cta"><p class="ctat">Pour aller plus loin</p><p><a href="/guide-produits-cheveux-pdf/">Les guides PDF des meilleurs produits pour ton type de cheveux</a></p></div>') +
      '<p style="text-align:center;margin-top:16px"><button type="button" class="qback" id="qredo">Refaire le test</button></p></div>';
    body.innerHTML = h; if (window.cc_evt) cc_evt('quiz-termine');
    var t = body.querySelector("h2"); t.setAttribute("tabindex", "-1"); t.focus({ preventScroll: true });
    root.scrollIntoView({ behavior: "smooth", block: "start" });
    document.getElementById("qredo").addEventListener("click", function () { rep = {}; i = 0; show(); });
  }
  show();
})();
