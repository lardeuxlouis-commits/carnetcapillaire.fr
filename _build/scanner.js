/* Carnet capillaire : scanner de composition et score /100 (page /composition-shampoing/).
   Ce qui part du navigateur, et seulement ça :
   - le code-barres ou le nom tapé, envoyés à la base du carnet (serveur du site : partages + copie d'Open Beauty Facts, aucun compte, aucune IP gardée)
     et aux API publiques Open Beauty Facts / Open Products Facts / Open Food Facts pour trouver le produit ;
   - la composition, SEULEMENT si l'utilisatrice coche « Partager cette composition » (code-barres, nom, marque, liste INCI : rien de personnel).
   Le profil (type de cheveux, cuir chevelu) reste dans le navigateur (localStorage, try/catch). La photo est lue sur l'appareil (Tesseract.js) et n'est jamais envoyée.
   Règles et pondérations du score : _build/ingredients.json (blocs regles, categories, score), injecté par le build dans window.CC_INGR. Méthode publique : /methode-score/.
   Librairies chargées seulement au clic : zxing-cpp WebAssembly (/lib/, si pas de BarcodeDetector natif, donc sur iPhone) et Tesseract.js (photo). */
(function () {
  "use strict";

  /* ===================== 1. Cœur : lecture et analyse d'une liste INCI (sans DOM) ===================== */
  function creerMoteur(DB) {
    function sansAccents(s) { return String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, ""); }
    function norm(s) {
      return sansAccents(s).toLowerCase().replace(/[’'`]/g, " ").replace(/[*°+†‡§¹²³]/g, " ")
        .replace(/\s*([\/-])\s*/g, "$1").replace(/\s+/g, " ").replace(/^[\s.,;:-]+|[\s.,;:-]+$/g, "");
    }
    function squash(s) { return norm(s).replace(/[^a-z0-9]/g, ""); }

    // Dictionnaire des noms connus (règles + ingrédients courants), clé « écrasée » pour tolérer espaces, tirets et ponctuation
    var DICT = {}, LISTE = [], SYN = {};
    function ajoute(n) { var k = squash(n); if (k && !DICT[k]) { DICT[k] = norm(n); LISTE.push(k); } }
    DB.regles.forEach(function (r) { (r.noms || []).forEach(ajoute); });
    (DB.communs || []).forEach(ajoute);
    Object.keys(DB.synonymes || {}).forEach(function (k) { SYN[squash(k)] = norm(DB.synonymes[k]); ajoute(DB.synonymes[k]); });
    DB.regles.forEach(function (r) {
      r._motifs = (r.motifs || []).map(function (m) { return new RegExp(m); });
      r._exclut = (r.exclut || []).map(function (m) { return new RegExp(m); });
      r._noms = {}; (r.noms || []).forEach(function (n) { r._noms[squash(n)] = 1; });
    });

    function lev(a, b, max) { // distance d'édition, arrêt anticipé au-delà de max
      if (Math.abs(a.length - b.length) > max) return max + 1;
      var prev = [], cur, i, j;
      for (j = 0; j <= b.length; j++) prev[j] = j;
      for (i = 1; i <= a.length; i++) {
        cur = [i]; var best = i;
        for (j = 1; j <= b.length; j++) {
          cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
          if (cur[j] < best) best = cur[j];
        }
        if (best > max) return max + 1;
        prev = cur;
      }
      return prev[b.length];
    }
    function seuil(n) { return n < 6 ? 0 : n <= 10 ? 1 : n <= 18 ? 2 : 3; }

    // Rapproche un nom lu (souvent abîmé par l'OCR) d'un nom connu : synonyme, exact, puis distance d'édition courte
    function reconnait(nom) {
      var k = squash(nom);
      if (!k) return null;
      if (SYN[k]) return { nom: SYN[k], d: 0 };
      if (DICT[k]) return { nom: DICT[k], d: 0 };
      var max = seuil(k.length);
      if (!max) return null;
      var best = null, bd = max + 1;
      for (var i = 0; i < LISTE.length; i++) {
        var d = lev(k, LISTE[i], Math.min(max, bd - 1));
        if (d < bd) { bd = d; best = LISTE[i]; }
      }
      return best && bd <= max ? { nom: DICT[best], d: bd } : null;
    }

    // Un ingrédient : nom principal, sans le contenu entre parenthèses ; on essaie aussi chaque partie séparée par « / »
    function lireIngredient(brut) {
      var b = String(brut).replace(/\[[^\]]*\]/g, " ").trim();
      var sansPar = norm(b.replace(/\([^()]*\)/g, " ").replace(/[()]/g, " "));
      var dansPar = (b.match(/\(([^)]*)\)/g) || []).map(function (x) { return norm(x.slice(1, -1)); });
      if (!squash(sansPar) && !dansPar.length) return null;
      var essais = [sansPar].concat(sansPar.indexOf("/") >= 0 ? sansPar.split("/") : [], dansPar);
      for (var i = 0; i < essais.length; i++) {
        var r = reconnait(essais[i]);
        if (r) return { brut: b, nom: r.nom, corrige: r.d > 0, d: r.d, connu: true };
      }
      var n = sansPar || dansPar[0];
      return { brut: b, nom: n.split("/")[0], connu: false };
    }

    // Repère le bloc INCI dans un texte (collé ou lu sur une photo) et le découpe en ingrédients
    var ENTETE = /(ingr[eé]dients?|ingredientes|ingredienti|zutaten|inci|composition)\s*[:.;\-]?/gi;
    var MOTS_FR = /\b(de|du|des|la|le|les|pour|est|avec|sans|une|un|votre|vos|nos|notre|plus|dans|sur|par|bouteille|flacon|cheveux|produit|issus?|origine|naturelle|agriculture|biologique|recyclable|yeux|enfants|contact|utiliser|appliquer)\b/g;
    var FONCTIONS = /\s+(eau|agents? lavants?|hydratants?|emollients?|conditionneurs?|nacrants?|regulateur du ph|chelatants?|conservateurs?|parfum|extrait d.*|epaississants?|antioxydants?|colorants?|tensioactifs?|solvants?|parfums?)$/;

    function nettoyerOCR(t) {
      return String(t || "").replace(/\r/g, "")
        .replace(/([A-Za-z])-\s*\n\s*([a-z])/g, "$1$2")      // césure en minuscules : on recolle
        .replace(/([A-Z0-9])-\s*\n\s*([A-Z])/g, "$1-$2")      // tiret d'un nom INCI coupé en fin de ligne : on garde le tiret
        .replace(/[|]/g, " ").replace(/[«»"]/g, " ").replace(/[ \t]+/g, " ");
    }

    function decouper(texte) {
      var t = nettoyerOCR(texte);
      // Après l'en-tête « Ingrédients : » s'il existe (le premier qui est suivi d'une liste)
      // On garde l'en-tête le plus prometteur : suivi de « : » et de nombreuses virgules ou lignes courtes
      var m, debut = -1, meilleur = 0; ENTETE.lastIndex = 0;
      while ((m = ENTETE.exec(t))) {
        var apres = t.slice(m.index + m[0].length, m.index + m[0].length + 240);
        var sc = (apres.match(/,/g) || []).length + (apres.match(/\n/g) || []).length + (/[:]/.test(m[0]) ? 4 : 0) + (/^[A-Z]{2,}$/.test(m[1]) ? 2 : 0) - (apres.match(MOTS_FR) || []).length;
        if (sc > meilleur) { meilleur = sc; debut = m.index + m[0].length; }
      }
      if (debut >= 0) t = t.slice(debut);
      t = t.replace(/(\+\/-|\+\/−|±)?\s*(may contain|peut contenir|puede contener)\s*:?/gi, ",");
      var lignes = t.split("\n").map(function (l) { return l.trim(); }).filter(Boolean);
      // Recolle les lignes qui coupent une parenthèse
      for (var i = 0; i < lignes.length - 1; i++) {
        var o = (lignes[i].match(/\(/g) || []).length, f = (lignes[i].match(/\)/g) || []).length;
        if (o <= f) continue;
        for (var k2 = i + 1; k2 <= i + 2 && k2 < lignes.length; k2++) if (lignes[k2].indexOf(")") >= 0 && lignes[k2].indexOf("(") < 0) break;
        if (k2 <= i + 2 && k2 < lignes.length) { lignes[i] = lignes.slice(i, k2 + 1).join(" "); lignes.splice(i + 1, k2 - i); }
      }
      var virgules = (t.match(/[,;•·]/g) || []).length;
      var parLigne = lignes.length >= 3 && virgules < lignes.length / 2; // liste « un ingrédient par ligne » (fréquent sur les flacons bio)
      var morceaux = parLigne ? lignes : lignes.join(" ").split(/\s*[,;•·]\s*|\s+-\s+(?=[A-Za-z])/);
      var out = [], inconnus = 0;
      for (var j = 0; j < morceaux.length; j++) {
        var x = morceaux[j], fin = false;
        var phrase = x.match(/^(.*?[a-z0-9)\]])\.\s+(\S.*)$/i); // une phrase commence après le point : fin de la liste
        if (phrase && !/denat$/i.test(phrase[1])) { x = phrase[1]; fin = true; }
        x = x.replace(/\.$/, "").trim();
        if (!x) { if (fin) break; continue; }
        var nmots = (norm(x).match(MOTS_FR) || []).length;
        var ing = lireIngredient(x);
        if (nmots >= 2 && out.length && !ing.connu) { // une phrase en français : fin de la liste, sauf si elle finit par un ingrédient (texte parasite collé)
          var mm = norm(x).split(" "), sauve = null;
          for (var q = 1; q < mm.length && !sauve; q++) { var s2 = lireIngredient(mm.slice(q).join(" ")); if (s2 && (s2.connu || regleDe(s2.nom, false).length)) sauve = s2; }
          if (!sauve) break;
          ing = sauve;
        }
        if (!parLigne && ing && !ing.connu) { // bruit d'OCR en début de morceau (« oh PERSEA GRATISSIMA OIL ») : on retire jusqu'à 3 mots
          var mw = norm(x).split(" ");
          for (var z = 1; z <= 3 && z < mw.length; z++) { var s3 = lireIngredient(mw.slice(z).join(" ")); if (s3 && s3.connu) { s3.brut = x; ing = s3; break; } }
        }
        if (parLigne && ing && !ing.connu) { // « COCAMIDOPROPYL BETAINE* AGENT LAVANT » : on garde le plus long début reconnu
          var mots = norm(x.replace(/\([^)]*\)/g, " ")).replace(FONCTIONS, "").split(" ");
          for (var n = mots.length; n >= 1; n--) { var r = lireIngredient(mots.slice(0, n).join(" ")); if (r && r.connu) { r.brut = x; ing = r; break; } }
          if (!ing.connu) ing.nom = norm(x.replace(/\([^)]*\)/g, " ")).replace(FONCTIONS, "");
        }
        if (ing && squash(ing.nom).length >= 2) {
          out.push(ing);
          inconnus = ing.connu ? 0 : inconnus + 1;
          if (inconnus >= 4 && out.length > 6) { out.splice(out.length - 4, 4); break; }
        }
        if (fin && out.length >= 3) break;
      }
      while (out.length && !out[out.length - 1].connu && out.length > 3 && !/oil|extract|butter|acid|ate$|ide$/.test(out[out.length - 1].nom)) out.pop();
      return out;
    }

    function regleDe(nom, multi) {
      var k = squash(nom), res = [];
      for (var i = 0; i < DB.regles.length; i++) {
        var r = DB.regles[i];
        if (!!r.multi !== multi) continue;
        var ok = r._noms[k] || r._motifs.some(function (re) { return re.test(nom); });
        if (ok && r._exclut.some(function (re) { return re.test(nom); }) && !r._noms[k]) ok = false;
        if (ok) { res.push(r); if (!multi) break; }
      }
      return res;
    }

    function analyser(liste, profil) {
      var parRegle = {}, ordre = [];
      liste.forEach(function (ing, i) {
        ing.rang = i + 1;
        ing.regles = regleDe(ing.nom, false).concat(regleDe(ing.nom, true));
        ing.regles.forEach(function (r) {
          if (!parRegle[r.id]) { parRegle[r.id] = { r: r, ings: [] }; ordre.push(r.id); }
          parRegle[r.id].ings.push(ing);
        });
      });
      var points = [];
      ordre.forEach(function (id) {
        var g = parRegle[id], r = g.r, pr = r.profil || {};
        if (r.si_absent && r.si_absent.some(function (x) { return parRegle[x]; })) return;
        var premier = g.ings[0].rang;
        [["texture", profil.texture], ["cuir", profil.cuir], ["ep", profil.fin ? "fin" : ""]].forEach(function (dim) {
          if (!dim[1] || !pr[dim[0]]) return;
          Object.keys(pr[dim[0]]).forEach(function (cles) {
            if (cles.split(",").indexOf(dim[1]) < 0) return;
            var p = pr[dim[0]][cles];
            if (p[2] && premier > p[2]) return; // l'effet ne compte que si l'ingrédient est haut placé dans la liste
            points.push({ niveau: p[0], texte: p[1], regle: r, ings: g.ings });
          });
        });
      });
      var c = { ok: 0, prudence: 0, peu: 0 }, pire = {}, RANG = { info: 0, ok: 1, prudence: 2, peu: 3 };
      points.forEach(function (p) { var id = p.regle.id; if (!pire[id] || RANG[p.niveau] > RANG[pire[id]]) pire[id] = p.niveau; });
      Object.keys(pire).forEach(function (id) { if (c[pire[id]] !== undefined) c[pire[id]]++; }); // une règle compte une fois, à son niveau le plus réservé
      var verdict = (c.peu >= 2 || (c.peu >= 1 && c.ok === 0)) ? "peu" : (c.peu >= 1 || c.prudence > c.ok) ? "prudence" : "ok";
      var a = function (id) { return !!parRegle[id]; };
      var nb = function (id) { return parRegle[id] ? parRegle[id].ings.length : 0; };
      var badges = [];
      badges.push(a("sulfate") ? ["Contient des sulfates", "neutre"] : a("sulfonate") ? ["Sans sulfate, mais tensioactif fort", "neutre"] : a("doux") ? ["Sans sulfate", "vert"] : null);
      badges.push(a("silicone") ? ["Contient des silicones", "neutre"] : a("silicone_soluble") ? ["Silicones solubles seulement", "neutre"] : ["Sans silicone", "vert"]);
      if (a("proteine")) badges.push(nb("proteine") >= 2 || parRegle.proteine.ings[0].rang <= 8 ? ["Riche en protéines", "neutre"] : ["Contient des protéines", "neutre"]);
      if (a("huile") || a("beurre")) badges.push(["Avec huiles ou beurres", "vert"]);
      if (a("humectant")) badges.push(["Avec humectants", "vert"]);
      if (a("cationique")) badges.push(["Avec agents démêlants", "vert"]);
      badges.push(a("parfum") || a("huile_essentielle") ? ["Parfumé", "neutre"] : ["Sans parfum", "vert"]);
      if (a("allergene")) badges.push([nb("allergene") + (nb("allergene") > 1 ? " allergènes parfumants déclarés" : " allergène parfumant déclaré"), "neutre"]);
      if (a("alcool_sec") && parRegle.alcool_sec.ings[0].rang <= 5) badges.push(["Alcool volatil en tête de liste", "neutre"]);
      if (a("antipelliculaire")) badges.push(["Actif antipelliculaire", "neutre"]);
      if (a("retire")) badges.push(["Ancienne formule probable", "alerte"]);
      return { liste: liste, groupes: ordre.map(function (id) { return parRegle[id]; }), points: points, verdict: verdict, compte: c,
        badges: badges.filter(Boolean), reconnus: liste.filter(function (x) { return x.connu || x.regles.length; }).length };
    }

    /* --- Catégorie du produit : étiquettes Open Beauty Facts, puis nom, sinon shampoing (le carnet parle de cheveux) --- */
    var CAT_TAGS = [["apres", /conditioner|apres-shampo|demelant/], ["masque", /hair-mask|masques?-capillaire|masque/], ["huile", /hair-oil|huile-capillaire|leave-in|sans-rincage/],
      ["shampoing", /shampoo|shampoing|shampooing/], ["gel_douche", /shower|douche|body-wash|bath/], ["savon", /soap|savon/], ["creme", /cream|creme|lotion|body-milk|lait|moisturi|balm|baume/]];
    var CAT_NOM = [["shampoing", /2 ?en ?1|2 ?in ?1|shampoo?ing douche|shampoing demelant|shampooing demelant/], ["apres", /apres[ -]?shamp|conditioner|acondicionador|balsamo/], ["masque", /masque|mask|mascarilla|maschera|hair food/],
      ["gel_douche", /douche|shower|ducha|doccia|bain moussant|bath/], ["shampoing", /shamp|champu/], ["apres", /demelant|detangl/],
      ["creme", /micell|demaquill|make-?up|concealer|fond de teint|deodor|anti-?transpir|solaire|sun|spf|lingette|wipe|visage|face|corps|body|mains|hand|levres|lip|vergetures|cellulite|dentifr|tooth/],
      ["huile", /huile|oil|aceite|serum|sans rincage|leave[ -]?in|spray|creme coiffante|gel coiffant|curl/], ["savon", /savon|soap|jabon|pain surgras/], ["creme", /creme|cream|lait|lotion|baume|balm/]];
    function categorie(p, liste) {
      var tags = String(p && (p.categories || "") || "").toLowerCase(), nom = norm((p && ((p.nom || "") + " " + (p.marque || ""))) || ""), i;
      for (i = 0; i < CAT_NOM.length; i++) if (CAT_NOM[i][1].test(nom)) return CAT_NOM[i][0];
      for (i = 0; i < CAT_TAGS.length; i++) if (CAT_TAGS[i][1].test(tags)) return CAT_TAGS[i][0];
      var lave = false;
      if (liste) for (i = 0; i < Math.min(liste.length, 6); i++) regleDe(liste[i].nom, false).forEach(function (r) { if (r.id === "saponifie" && i < 4) lave = "savon"; else if (/^lavant/.test(r.groupe) && !lave) lave = "shampoing"; });
      return lave || (liste ? "creme" : "shampoing");
    }

    /* --- Score /100 (bloc « score » de la base, méthode publiée sur /methode-score/) --- */
    function facteur(rang) { var P = DB.score.position; for (var i = 0; i < P.length; i++) if (rang <= P[i][0]) return P[i][1]; return P[P.length - 1][1]; }
    function scorer(A, profil, cat) {
      var S = DB.score, C = (DB.categories || {})[cat] || { capillaire: true, lave: true };
      var mode = C.capillaire && profil && profil.texture && profil.cuir ? "compat" : "douceur";
      var par = {}; A.groupes.forEach(function (g) { par[g.r.id] = g; });
      var lignes = [], bonus = 0, malus = 0;
      if (mode === "compat") {
        A.points.forEach(function (p) {
          if (!C.lave && /^lavant/.test(p.regle.groupe)) return; // les remarques sur le lavage ne valent que pour un produit qui lave
          var v = (S.profil[p.niveau] || 0) * facteur(p.ings[0].rang);
          if (v > 0) { v = Math.min(v, S.profil.plafond_bonus - bonus); bonus += v; }
          else if (v < 0) { v = Math.max(v, S.profil.plafond_malus - malus); malus += v; }
          v = Math.round(v);
          if (v) lignes.push({ label: p.regle.label, pts: v, txt: p.texte, type: "profil" });
        });
      }
      S.criteres.forEach(function (c) {
        var g = par[c.regle], v = c[mode];
        if (!g || !v) return;
        if (c.sans && c.sans.some(function (x) { return par[x]; })) return;
        var n = g.ings.length, r = g.ings[0].rang, lab = c.label;
        if (c.par_ingredient) { v = v < 0 ? Math.max(c.max, v * n) : Math.min(c.max, v * n); lab += " (" + n + ")"; }
        else {
          if (c.rang_max && r > c.rang_max) return;
          if (c.noms && mode === "douceur") g.ings.forEach(function (i) { if (c.noms[i.nom] != null && c.noms[i.nom] < v) v = c.noms[i.nom]; });
          if (c.position) { v = v * facteur(r); lab += ", n°" + r + " de la liste"; }
        }
        v = Math.round(v);
        if (v) lignes.push({ label: lab, pts: v, type: "formule" });
      });
      var total = S.base; lignes.forEach(function (l) { total += l.pts; });
      total = Math.max(0, Math.min(100, Math.round(total)));
      var pal = "rouge"; for (var k = 0; k < S.paliers.length; k++) if (total >= S.paliers[k][0]) { pal = S.paliers[k][1]; break; }
      return { score: total, mode: mode, palier: pal, libelle: S.libelles[mode][pal], lignes: lignes, base: S.base, cat: cat, capillaire: !!C.capillaire };
    }

    /* --- Ressemblance de deux noms de produits (fiche approchante) : part des mots communs --- */
    var VIDES = /^(de|du|des|la|le|les|l|d|a|au|aux|et|en|pour|with|and|the|for|ml|x)$/;
    function mots(s) { return norm(s).replace(/[^a-z0-9 ]/g, " ").split(" ").filter(function (w) { return w.length > 1 && !VIDES.test(w) && !/^\d+(ml)?$/.test(w); }); }
    function ressemblance(a, b) {
      var A1 = mots(a), B1 = mots(b); if (!A1.length || !B1.length) return 0;
      var commun = A1.filter(function (w) { return B1.indexOf(w) >= 0; }).length;
      return commun / Math.max(A1.length, B1.length);
    }

    return { norm: norm, squash: squash, lev: lev, reconnait: reconnait, decouper: decouper, analyser: analyser, nettoyerOCR: nettoyerOCR,
      categorie: categorie, scorer: scorer, ressemblance: ressemblance };
  }

  function eanValide(c) { // clé de contrôle GTIN (EAN-8, UPC-A, EAN-13, GTIN-14)
    if (!/^\d{8}$|^\d{12,14}$/.test(c)) return false;
    var s = 0, n = c.length;
    for (var i = 0; i < n - 1; i++) s += +c[n - 2 - i] * (i % 2 ? 1 : 3);
    return (10 - s % 10) % 10 === +c[n - 1];
  }

  if (typeof module !== "undefined" && module.exports) { creerMoteur.eanValide = eanValide; module.exports = creerMoteur; return; } // tests sous Node

  /* ===================== 2. Interface ===================== */
  var root = document.getElementById("scanner");
  if (!root || !window.CC_INGR) return;
  var DB = window.CC_INGR, M = creerMoteur(DB);
  var OBF = "https://world.openbeautyfacts.org", OPF = "https://world.openproductsfacts.org", OFF = "https://world.openfoodfacts.org";
  var API = "https://187-124-173-12.sslip.io/scan"; // base du carnet (VPS) : partages des utilisatrices + copie locale d'Open Beauty Facts
  var ZW_JS = "/lib/zxing-reader.js?v=3.1.7", ZW_WASM = "/lib/zxing_reader.wasm"; // zxing-cpp en WebAssembly, auto-hébergé
  var TESS = "https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js";
  var K = "cc_profil";
  var FORCE_WASM = /[?&]lecteur=wasm\b/.test(location.search); // test : simule un iPhone (pas de BarcodeDetector)
  function $(s, el) { return (el || root).querySelector(s); }
  function $$(s, el) { return Array.prototype.slice.call((el || root).querySelectorAll(s)); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function evt(n) { if (window.cc_evt) window.cc_evt(n); }
  function lire() { try { return JSON.parse(localStorage.getItem(K) || "null"); } catch (e) { return null; } }
  function ecrire(v) { try { localStorage.setItem(K, JSON.stringify(v)); } catch (e) {} }

  var TEXTURES = { raides: "Raides", ondules: "Ondulés", boucles: "Bouclés", frises: "Frisés", crepus: "Crépus" };
  var CUIRS = { equilibre: "Équilibré", gras: "Gras", sec: "Sec ou sensible", pellicules: "Pellicules" };
  var CATS = DB.categories;
  var profil = lire() || {};
  if (!TEXTURES[profil.texture]) profil.texture = "";
  if (!CUIRS[profil.cuir]) profil.cuir = "";
  var dernier = null; // { liste, produit, cat, origine, texte }
  var codeAttente = "", produitAttente = null; // code-barres scanné ou tapé, et fiche sans ingrédients (nom seul)

  // --- Profil en 2 clics ---
  var boxP = $("#scan-profil");
  function dessineProfil() {
    var src = profil.src === "quiz" ? '<p class="small scan-src">Repris de ton résultat au quiz. Tu peux le changer.</p>' : "";
    boxP.innerHTML = '<fieldset><legend>Tes cheveux</legend><div class="chips">' +
      Object.keys(TEXTURES).map(function (k) { return '<button type="button" class="chip" data-t="' + k + '" aria-pressed="' + (profil.texture === k) + '">' + TEXTURES[k] + "</button>"; }).join("") +
      '</div></fieldset><fieldset><legend>Ton cuir chevelu</legend><div class="chips">' +
      Object.keys(CUIRS).map(function (k) { return '<button type="button" class="chip" data-c="' + k + '" aria-pressed="' + (profil.cuir === k) + '">' + CUIRS[k] + "</button>"; }).join("") +
      '</div></fieldset><label class="scan-fin"><input type="checkbox" id="scan-fin"' + (profil.fin ? " checked" : "") + "> Mes cheveux sont fins</label>" + src;
    $$("[data-t]", boxP).forEach(function (b) { b.addEventListener("click", function () { profil.texture = b.getAttribute("data-t"); majProfil(); }); });
    $$("[data-c]", boxP).forEach(function (b) { b.addEventListener("click", function () { profil.cuir = b.getAttribute("data-c"); majProfil(); }); });
    $("#scan-fin", boxP).addEventListener("change", function (e) { profil.fin = e.target.checked; majProfil(); });
  }
  function majProfil() {
    profil.src = "scanner";
    ecrire(profil); dessineProfil();
    if (dernier) rendre(dernier.liste, dernier.produit, true);
  }
  dessineProfil();

  // --- Onglets ---
  var tabs = $$('[role="tab"]');
  function onglet(id, focus) {
    tabs.forEach(function (t) {
      var on = t.getAttribute("aria-controls") === id;
      t.setAttribute("aria-selected", on); t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      if (on && focus) t.focus();
    });
    if (id !== "p-code") stopCamera();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { onglet(t.getAttribute("aria-controls")); });
    t.addEventListener("keydown", function (e) {
      var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (d) { e.preventDefault(); onglet(tabs[(i + d + tabs.length) % tabs.length].getAttribute("aria-controls"), true); }
    });
  });

  var etat = $("#scan-etat"), res = $("#scan-res");
  function message(html, type) { etat.innerHTML = html ? '<p class="scan-msg ' + (type || "") + '">' + html + "</p>" : ""; }

  // --- Chargement de scripts externes, seulement au clic ---
  var charges = {};
  function script(src, sri) {
    if (charges[src]) return charges[src];
    charges[src] = new Promise(function (ok, ko) {
      var s = document.createElement("script"); s.src = src; s.async = true;
      if (sri) { s.integrity = sri; s.crossOrigin = "anonymous"; } else if (/^https:/.test(src)) s.crossOrigin = "anonymous";
      s.onload = ok; s.onerror = function () { delete charges[src]; ko(new Error("chargement")); };
      document.head.appendChild(s);
    });
    return charges[src];
  }

  /* ---------- (a) Lecture du code-barres ----------
     Android/Chrome : BarcodeDetector natif. iPhone/Safari (pas de BarcodeDetector) et le reste : zxing-cpp compilé en WebAssembly
     (lit 2 fois plus de photos réelles de flacons que ZXing JS, testé le 22/11/2026). Rotation 90° gérée, zone de visée lue en pleine résolution. */
  var lecteurP = null;
  var FORMATS = ["EAN13", "EAN8", "UPCA", "UPCE"];
  function propre(c) { c = String(c || "").replace(/\D/g, ""); if (c.length === 12) c = "0" + c; return window.CC_EAN_OK(c) ? c : null; }
  function lecteur() {
    if (!lecteurP) lecteurP = natif().catch(wasm).catch(function (e) { lecteurP = null; throw e; });
    return lecteurP;
  }
  function natif() {
    if (FORCE_WASM || !("BarcodeDetector" in window)) return Promise.reject(new Error("absent"));
    return window.BarcodeDetector.getSupportedFormats().then(function (f) {
      if (f.indexOf("ean_13") < 0) throw new Error("format");
      var d = new window.BarcodeDetector({ formats: ["ean_13", "ean_8", "upc_a", "upc_e"].filter(function (x) { return f.indexOf(x) >= 0; }) });
      return { nom: "natif", lire: function (src) { return d.detect(src).then(function (r) { for (var i = 0; i < r.length; i++) { var c = propre(r[i].rawValue); if (c) return c; } return null; }); } };
    });
  }
  function wasm() {
    return script(ZW_JS).then(function () {
      var Z = window.ZXingWASM;
      return Z.prepareZXingModule({ overrides: { locateFile: function (p, pre) { return /\.wasm$/.test(p) ? ZW_WASM : pre + p; } }, fireImmediately: true }).then(function () {
        var cv = document.createElement("canvas"), cx = cv.getContext("2d", { willReadFrequently: true }), tour = 0;
        function zone(src, sx, sy, sw, sh, max) {
          var s = Math.min(1, max / Math.max(sw, sh)), w = Math.max(1, Math.round(sw * s)), h = Math.max(1, Math.round(sh * s));
          cv.width = w; cv.height = h; cx.drawImage(src, sx, sy, sw, sh, 0, 0, w, h);
          return Z.readBarcodes(cx.getImageData(0, 0, w, h), { formats: FORMATS, tryHarder: true, tryRotate: true, tryInvert: false, maxNumberOfSymbols: 1 })
            .then(function (r) { for (var i = 0; i < r.length; i++) { var c = propre(r[i].text); if (c) return c; } return null; });
        }
        return { nom: "wasm", lire: function (src, photo) {
          var w = src.videoWidth || src.naturalWidth || src.width, h = src.videoHeight || src.naturalHeight || src.height;
          if (!w || !h) return Promise.resolve(null);
          if (photo) // photo fixe : image entière en grand, puis plus petite, puis le centre
            return zone(src, 0, 0, w, h, 2400).then(function (c) { return c || zone(src, 0, 0, w, h, 1280); })
              .then(function (c) { return c || zone(src, w * 0.15, h * 0.15, w * 0.7, h * 0.7, 2000); });
          // vidéo : une image sur deux, l'image entière réduite ; l'autre, la zone de visée en pleine définition (petit code-barres tenu à 20 cm)
          return tour++ % 2 ? zone(src, w * 0.08, h * 0.2, w * 0.84, h * 0.6, 1600) : zone(src, 0, 0, w, h, 1280);
        } };
      });
    });
  }
  window.CC_EAN_OK = eanValide;

  var video = $("#scan-video"), camBox = $("#scan-cam"), flux = null, boucle = null, aide = null, cams = [], camIdx = -1, torche = false;
  function stopCamera() {
    if (boucle) { clearTimeout(boucle); boucle = null; }
    if (aide) { clearTimeout(aide); aide = null; }
    if (flux) { flux.getTracks().forEach(function (t) { t.stop(); }); flux = null; }
    if (video) video.srcObject = null;
    if (camBox) camBox.hidden = true;
    var b = $("#scan-go"); if (b) b.hidden = false;
  }
  $("#scan-stop").addEventListener("click", function () { stopCamera(); message(""); });
  function contraintes() {
    var v = { width: { ideal: 1920 }, height: { ideal: 1080 } };
    if (camIdx >= 0 && cams[camIdx]) v.deviceId = { exact: cams[camIdx].deviceId }; else v.facingMode = { ideal: "environment" };
    return { video: v, audio: false };
  }
  function demarrer() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      message("Ton navigateur ne donne pas accès à la caméra en direct. Utilise « Photographier le code-barres », ou tape les chiffres juste en dessous.", "warn"); return;
    }
    if (!flux) message("Ton navigateur va te demander l'accès à la caméra. Elle sert seulement à lire le code-barres : aucune image n'est enregistrée ni envoyée.");
    if (flux) { flux.getTracks().forEach(function (t) { t.stop(); }); flux = null; }
    var pret = lecteur(); // le lecteur se charge pendant que la caméra s'allume
    navigator.mediaDevices.getUserMedia(contraintes()).then(function (s) {
      flux = s; video.srcObject = s; video.setAttribute("playsinline", ""); video.muted = true;
      camBox.hidden = false; $("#scan-go").hidden = true;
      return video.play();
    }).then(function () {
      reglages();
      message("Vise le code-barres dans le cadre, à 15 ou 20 cm. Il peut être horizontal ou vertical.");
      evt("scanner-camera");
      if (aide) clearTimeout(aide);
      aide = setTimeout(function () { if (flux) message("Ça ne lit pas ? Recule un peu (le téléphone fait la mise au point à 15 cm minimum), évite les reflets" + ($("#scan-torch").hidden ? "" : ", allume la lampe") + ", ou <strong>photographie le code-barres</strong> avec le bouton sous la caméra.", "warn"); }, 12000);
      return pret;
    }).then(function (L) {
      if (!L || !flux) return;
      var essai = function () {
        if (!flux) return;
        if (video.readyState < 2) { boucle = setTimeout(essai, 150); return; }
        L.lire(video, false).then(function (code) {
          if (code && flux) trouve(code, "camera-" + L.nom);
          else boucle = setTimeout(essai, L.nom === "natif" ? 180 : 40);
        }).catch(function () { boucle = setTimeout(essai, 300); });
      };
      essai();
    }).catch(function (e) {
      stopCamera();
      if (e && e.message === "chargement") message("Le lecteur de code-barres n'a pas pu se charger (connexion ?). Tape les chiffres à la main, juste en dessous.", "warn");
      else message("Pas d'accès à la caméra" + (e && e.name === "NotAllowedError" ? " (autorisation refusée, tu peux la redonner dans les réglages du navigateur)" : "") + ". Utilise « Photographier le code-barres », ou tape les chiffres juste en dessous.", "warn");
    });
  }
  function reglages() { // mise au point continue, lampe, zoom et choix de la caméra, seulement si l'appareil les propose
    var t = flux && flux.getVideoTracks()[0], caps = t && t.getCapabilities ? t.getCapabilities() : {};
    if (caps.focusMode && caps.focusMode.indexOf("continuous") >= 0) t.applyConstraints({ advanced: [{ focusMode: "continuous" }] }).catch(function () {});
    var bt = $("#scan-torch"); bt.hidden = !caps.torch; torche = false; bt.setAttribute("aria-pressed", "false");
    var z = $("#scan-zoom"), zb = $("#scan-zoom-box");
    if (caps.zoom && caps.zoom.max > caps.zoom.min) { zb.hidden = false; z.min = caps.zoom.min; z.max = Math.min(caps.zoom.max, 5); z.step = caps.zoom.step || 0.1; z.value = (t.getSettings && t.getSettings().zoom) || caps.zoom.min; }
    else zb.hidden = true;
    if (navigator.mediaDevices.enumerateDevices) navigator.mediaDevices.enumerateDevices().then(function (d) {
      cams = d.filter(function (x) { return x.kind === "videoinput" && !/front|avant|facetime|user/i.test(x.label); });
      $("#scan-switch").hidden = cams.length < 2;
    }).catch(function () {});
  }
  $("#scan-torch").addEventListener("click", function () {
    var t = flux && flux.getVideoTracks()[0]; if (!t) return;
    torche = !torche; this.setAttribute("aria-pressed", String(torche));
    t.applyConstraints({ advanced: [{ torch: torche }] }).catch(function () {});
  });
  $("#scan-zoom").addEventListener("input", function () { var t = flux && flux.getVideoTracks()[0]; if (t) t.applyConstraints({ advanced: [{ zoom: +this.value }] }).catch(function () {}); });
  $("#scan-switch").addEventListener("click", function () { if (cams.length < 2) return; camIdx = (camIdx + 1) % cams.length; demarrer(); });
  $("#scan-go").addEventListener("click", function () { camIdx = -1; demarrer(); });

  // Photo du code-barres : l'appareil photo natif fait une mise au point bien meilleure que la vidéo (utile sur iPhone)
  $("#scan-photo-code").addEventListener("change", function (e) {
    var f = e.target.files && e.target.files[0]; e.target.value = "";
    if (!f) return;
    stopCamera(); res.innerHTML = "";
    message("Lecture du code-barres sur ta photo… Elle reste sur ton appareil.");
    Promise.all([lecteur(), image(f)]).then(function (r) { return r[0].lire(r[1], true).then(function (c) { URL.revokeObjectURL(r[1].src); return c; }); }).then(function (code) {
      if (code) { evt("scanner-photo-code-ok"); trouve(code, "photo"); }
      else { evt("scanner-photo-code-rate"); message("Je ne trouve pas de code-barres net sur cette photo. Reprends-la avec le code-barres entier, bien éclairé, sans reflet, ou tape les chiffres juste en dessous.", "warn"); }
    }).catch(function () { message("La photo n'a pas pu être lue. Tape les chiffres sous le code-barres juste en dessous.", "warn"); });
  });
  function image(f) {
    return new Promise(function (ok, ko) { var img = new Image(); img.onload = function () { ok(img); }; img.onerror = ko; img.src = URL.createObjectURL(f); });
  }
  function trouve(code, via) {
    stopCamera(); if (navigator.vibrate) navigator.vibrate(60);
    $("#scan-ean").value = code; chercherCode(code);
  }

  /* ---------- (b) Recherche en cascade d'un code-barres ----------
     1. base du carnet (partages + copie d'Open Beauty Facts, qui interroge aussi Open Food Facts et Open Products Facts),
     2. Open Beauty Facts en direct, 3. avec le nom seul : fiche approchante par nom et marque,
     4. préfixe du code-barres : marque probable et ses produits, 5. photo de l'étiquette ou collage. */
  var CHAMPS = "code,product_name,product_name_fr,generic_name_fr,brands,image_front_small_url,ingredients_text,ingredients_text_fr,ingredients_text_en,categories_tags";
  function getJSON(u, ms) {
    var ctl = "AbortController" in window ? new AbortController() : null, t = ctl && setTimeout(function () { ctl.abort(); }, ms || 12000);
    return fetch(u, ctl ? { signal: ctl.signal } : {}).then(function (r) { clearTimeout(t); if (r.status === 404) return null; if (!r.ok) throw new Error("http"); return r.json(); });
  }
  function nomOK(n) { n = String(n || "").trim(); return /[a-zà-ÿ]{2}/i.test(n) ? n : ""; } // « 0 », « - » : pas un nom
  function nomOBF(p) { return nomOK(p.product_name_fr) || nomOK(p.product_name) || nomOK(p.generic_name_fr); }
  function inciOBF(p) { return p.ingredients_text_fr || p.ingredients_text || p.ingredients_text_en || ""; }
  function fiche(o, source) { // fiche unique, quelle que soit la base
    if (!o) return null;
    if (o.ean !== undefined) return { code: o.ean, nom: nomOK(o.nom), marque: o.marque || "", image: o.image || "", inci: o.inci || "", categories: o.categories || "", source: source || o.source || "carnet", licence: o.licence || "" };
    return { code: o.code, nom: nomOBF(o), marque: (o.brands || "").split(",")[0].trim(), image: o.image_front_small_url || "", inci: inciOBF(o), categories: (o.categories_tags || []).join(","), source: source || "obf-live", licence: "ODbL Open Beauty Facts" };
  }
  function aInci(f) { return !!(f && M.decouper(f.inci).length >= 3); }
  function liveOFX(base, c, src) { return getJSON(base + "/api/v2/product/" + encodeURIComponent(c) + ".json?fields=" + CHAMPS, 9000).then(function (d) { return d && d.status === 1 && d.product ? fiche(d.product, src) : null; }).catch(function () { return null; }); }
  function vps(chemin) { return getJSON(API + chemin, 7000).catch(function () { return "panne"; }); }

  $("#scan-form-code").addEventListener("submit", function (e) {
    e.preventDefault();
    var c = $("#scan-ean").value.replace(/\D/g, "");
    if (c.length === 12) c = "0" + c;
    if (c.length < 8 || c.length > 14) { message("Un code-barres compte 8 ou 13 chiffres en général (sous les barres). Vérifie et réessaie.", "warn"); $("#scan-ean").focus(); return; }
    if (!eanValide(c)) { message("Ce code ne semble pas complet : vérifie les chiffres sous les barres (le dernier sert de contrôle).", "warn"); $("#scan-ean").focus(); return; }
    chercherCode(c);
  });
  function chercherCode(c) {
    codeAttente = c; produitAttente = { code: c, nom: "", marque: "", source: "code" };
    message("Recherche du produit " + esc(c) + "…"); res.innerHTML = "";
    var obf = liveOFX(OBF, c, "obf-live");
    vps("/produit/" + c).then(function (d) {
      var v = d && d !== "panne" ? fiche(d) : null;
      if (aInci(v)) return v;
      return obf.then(function (o) {
        if (aInci(o)) return o;
        if (d !== "panne") return v || o;
        // base du carnet injoignable : on tente nous-mêmes Open Products Facts et Open Food Facts
        return Promise.all([liveOFX(OPF, c, "opf-live"), liveOFX(OFF, c, "off-live")]).then(function (r) { return aInci(r[0]) ? r[0] : aInci(r[1]) ? r[1] : v || o || r[0] || r[1]; });
      });
    }).then(function (f) {
      if (aInci(f)) { evt("scanner-code-ok-" + String(f.source).split("-")[0]); message(""); return analyserFiche(f, false); }
      if (f && f.nom) { produitAttente = f; return approchante(f); }
      return voisins(c);
    }).catch(function () { message("La recherche ne répond pas pour l'instant. Réessaie dans un moment, ou photographie la liste d'ingrédients.", "warn"); });
  }
  function rechercheNom(q) { // base du carnet d'abord (rapide), Open Beauty Facts en secours
    return vps("/recherche?n=24&q=" + encodeURIComponent(q)).then(function (d) {
      if (d && d !== "panne" && d.produits && d.produits.length) return d.produits.map(function (x) { return fiche(x); });
      return getJSON(OBF + "/cgi/search.pl?search_terms=" + encodeURIComponent(q) + "&search_simple=1&action=process&json=1&page_size=24&fields=" + CHAMPS, 12000)
        .then(function (o) { return ((o && o.products) || []).filter(function (p) { return p.code; }).map(function (p) { return fiche(p, "obf-live"); }); });
    });
  }
  // Nom connu mais pas les ingrédients : on cherche la fiche la plus ressemblante, de la même marque
  function approchante(f) {
    var q = ((f.marque || "") + " " + f.nom).trim();
    message("<strong>" + esc(f.nom) + "</strong> est connu, mais sans sa liste d'ingrédients. Je cherche une fiche approchante…");
    rechercheNom(q).then(function (ps) {
      var mq = M.norm(f.marque || ""), kf = M.categorie({ nom: f.nom, marque: "", categories: f.categories });
      var cands = ps.filter(function (p) { return aInci(p) && p.code !== f.code && (!mq || M.ressemblance(p.marque, f.marque) > 0 || M.norm(p.nom).indexOf(mq) >= 0) && M.categorie(p, M.decouper(p.inci)) === kf; })
        .map(function (p) { return { p: p, s: M.ressemblance(f.nom, p.nom) }; }).sort(function (a, b) { return b.s - a.s; });
      if (cands.length && cands[0].s >= 0.5) {
        var best = cands[0].p; best.approchante = { de: f }; evt("scanner-code-approchant");
        message(""); analyserFiche(best, false, cands.slice(1, 5).map(function (x) { return x.p; }));
        return;
      }
      if (cands.length) return choix("<strong>" + esc(f.nom) + "</strong>" + (f.marque ? " (" + esc(f.marque) + ")" : "") + " est connu, mais sans sa liste d'ingrédients. C'est l'un de ceux-ci ? Sinon, photographie la liste au dos.", cands.slice(0, 8).map(function (x) { return x.p; }), f);
      bascule("<strong>" + esc(f.nom) + "</strong> est connu, mais sans sa liste d'ingrédients.");
    }).catch(function () { bascule("<strong>" + esc(f.nom) + "</strong> est connu, mais sans sa liste d'ingrédients."); });
  }
  // Code-barres inconnu partout : le préfixe dit souvent la marque. On propose ses produits de la même famille.
  function voisins(c) {
    vps("/voisins/" + c + "?n=24").then(function (d) {
      if (!d || d === "panne" || !d.produits || !d.produits.length) { evt("scanner-code-absent"); return bascule("Ce code-barres (" + esc(c) + ") n'est encore dans aucune base."); }
      var ps = d.produits.map(function (x) { return fiche(x); }).filter(aInci).filter(function (p) { var k = M.categorie(p); return CATS[k] && !/dentifr|toothpaste|maquill|makeup|mascara|vernis|deodor|solaire|sun/.test(M.norm(p.nom + " " + p.categories)); });
      if (!ps.length) { evt("scanner-code-absent"); return bascule("Ce code-barres (" + esc(c) + ") n'est encore dans aucune base."); }
      evt("scanner-code-voisins");
      var sur = d.confiance >= 0.6 && d.marque_probable;
      choix("Ce code-barres n'est encore dans aucune base." + (sur ? " D'après son préfixe, c'est sans doute un produit <strong>" + esc(d.marque_probable) + "</strong>." : "") +
        " Si tu reconnais ton produit ci-dessous, choisis-le (vérifie quand même sur ton flacon). Sinon, <strong>photographie la liste d'ingrédients</strong>.", ps.slice(0, 10), { code: c, nom: "", marque: sur ? d.marque_probable : "" });
    });
  }
  function itemsHTML(ps) {
    return ps.map(function (p, i) {
      return '<li><button type="button" class="scan-item" data-i="' + i + '">' +
        (p.image ? '<img src="' + esc(p.image) + '" alt="" width="44" height="44" loading="lazy">' : '<span class="ph0" aria-hidden="true"></span>') +
        '<span><b>' + esc(p.nom || "Produit sans nom") + "</b><small>" + esc(p.marque || "Marque inconnue") + (aInci(p) ? "" : " · ingrédients absents") + "</small></span></button></li>";
    }).join("");
  }
  function choix(txt, ps, origine) {
    message(txt, "warn");
    etat.insertAdjacentHTML("beforeend", '<ul class="scan-choix" aria-label="Produits proches">' + itemsHTML(ps) + '</ul><p><button type="button" class="btn btn-o" data-vers="p-photo">Aucun : je photographie la liste</button></p>');
    $$(".scan-choix .scan-item", etat).forEach(function (b) {
      b.addEventListener("click", function () { var p = ps[+b.getAttribute("data-i")]; p.approchante = { de: origine, choisi: true }; evt("scanner-choix-voisin"); message(""); analyserFiche(p, false); });
    });
    $("[data-vers]", etat).addEventListener("click", function () { bascule("Pas de souci."); });
  }
  // Produit absent : bascule vers la photo, avec le collage en second choix
  function bascule(txt) {
    onglet("p-photo", true);
    message(txt + " <strong>Photographie la liste d'ingrédients</strong> au dos du flacon ci-dessous, ou " +
      '<button type="button" class="lien" data-vers="p-coller">colle-la</button> si tu l\'as sous les yeux sur un site. Tu pourras ensuite la partager pour les prochaines personnes qui scanneront ce produit.', "warn");
    var b = $("[data-vers]", etat); if (b) b.addEventListener("click", function () { onglet("p-coller", true); $("#scan-inci").focus(); });
  }

  // --- Recherche par nom ou marque ---
  $("#scan-form-nom").addEventListener("submit", function (e) {
    e.preventDefault();
    var q = $("#scan-q").value.trim(), out = $("#scan-liste");
    if (q.length < 3) { message("Tape au moins 3 lettres : la marque et le nom du produit, par exemple « elseve total repair ».", "warn"); return; }
    message("Recherche de « " + esc(q) + " »…"); out.innerHTML = "";
    rechercheNom(q).then(function (ps) {
      ps.sort(function (a, b) { return aInci(b) - aInci(a); });
      if (!ps.length) { evt("scanner-nom-vide"); return bascule("Aucun produit trouvé pour « " + esc(q) + " »."); }
      message(ps.length + " produit" + (ps.length > 1 ? "s" : "") + " trouvé" + (ps.length > 1 ? "s" : "") + ". Choisis le tien.");
      ps = ps.slice(0, 12); out.innerHTML = itemsHTML(ps);
      $$(".scan-item", out).forEach(function (b) {
        b.addEventListener("click", function () {
          var p = ps[+b.getAttribute("data-i")];
          if (!aInci(p)) { codeAttente = p.code || ""; produitAttente = p; return bascule("<strong>" + esc(p.nom) + "</strong> est connu, mais sans sa liste d'ingrédients."); }
          evt("scanner-nom-ok"); message(""); analyserFiche(p, false);
        });
      });
    }).catch(function () { message("La recherche ne répond pas pour l'instant. Réessaie, ou photographie la liste d'ingrédients.", "warn"); });
  });

  // --- Photo de la liste d'ingrédients : OCR dans le navigateur ---
  var prog = $("#scan-prog");
  $("#scan-photo").addEventListener("change", function (e) {
    var f = e.target.files && e.target.files[0];
    if (!f) return;
    res.innerHTML = ""; prog.hidden = false; prog.value = 0;
    message("Chargement du lecteur de texte (environ 4 Mo, une seule fois)… La photo reste sur ton appareil.");
    var etapes = { "loading tesseract core": "Chargement du lecteur", "initializing tesseract": "Préparation", "loading language traineddata": "Chargement du français et de l'anglais", "initializing api": "Préparation", "recognizing text": "Lecture du texte" };
    Promise.all([script(TESS), preparer(f)]).then(function (r) {
      return window.Tesseract.createWorker(["fra", "eng"], 1, { logger: function (m) {
        if (m.status === "recognizing text") { prog.value = 40 + m.progress * 60; message("Lecture du texte : " + Math.round(m.progress * 100) + " %"); }
        else if (etapes[m.status]) { prog.value = Math.min(40, (prog.value || 0) + 5 * (m.progress || 0.2)); message(etapes[m.status] + "…"); }
      } }).then(function (w) { return w.recognize(r[1]).then(function (o) { w.terminate(); return o.data.text; }); });
    }).then(function (texte) {
      prog.hidden = true; evt("scanner-photo");
      var liste = M.decouper(texte);
      onglet("p-coller");
      var zone = $("#scan-inci");
      zone.value = liste.length >= 3 ? liste.map(function (x) { return x.connu ? x.nom.toUpperCase() : x.brut; }).join(", ") : M.nettoyerOCR(texte).trim();
      if (liste.length < 3) { message("Je n'ai pas réussi à lire la liste. Reprends la photo de plus près, bien à plat et sans reflet, ou tape les premiers ingrédients ci-dessous.", "warn"); zone.focus(); return; }
      message("Voici le texte lu sur ta photo (" + liste.length + " ingrédients). Vérifie-le et corrige si besoin, puis relance l'analyse.");
      rendre(liste, produitAttente, false, "ocr", zone.value);
    }).catch(function () {
      prog.hidden = true;
      message("La lecture de la photo n'a pas marché (connexion ou image illisible). Tu peux coller ou taper la liste dans l'onglet « Coller la liste ».", "warn");
    });
    e.target.value = "";
  });
  function preparer(f) { // redimensionne et passe en niveaux de gris : lecture plus rapide et plus fiable
    return new Promise(function (ok, ko) {
      var img = new Image(), u = URL.createObjectURL(f);
      img.onload = function () {
        var max = Math.max(img.width, img.height), s = max > 2600 ? 2600 / max : max < 1200 ? 1200 / max : 1;
        var cv = document.createElement("canvas"); cv.width = Math.round(img.width * s); cv.height = Math.round(img.height * s);
        var cx = cv.getContext("2d"); cx.filter = "grayscale(1) contrast(1.25)"; cx.drawImage(img, 0, 0, cv.width, cv.height);
        URL.revokeObjectURL(u); ok(cv);
      };
      img.onerror = function () { URL.revokeObjectURL(u); ko(new Error("image")); };
      img.src = u;
    });
  }

  // --- (c) Liste collée ---
  $("#scan-form-inci").addEventListener("submit", function (e) {
    e.preventDefault();
    var t = $("#scan-inci").value;
    if (M.decouper(t).length < 3) { message("Colle la liste complète des ingrédients (au moins trois, séparés par des virgules), par exemple « Aqua, Sodium Laureth Sulfate, Glycerin… ».", "warn"); return; }
    message(""); evt("scanner-inci");
    rendre(M.decouper(t), produitAttente, false, dernier && dernier.origine === "ocr" ? "ocr" : "collage", t);
  });

  function analyserFiche(f, silencieux, autres) { rendre(M.decouper(f.inci), f, silencieux, "base", f.inci, autres); }

  /* ---------- Résultat : score /100, détail du calcul, composition ---------- */
  var NIV = { ok: ["Point positif", "+"], prudence: ["À surveiller", "!"], peu: ["Peu adapté", "×"], info: ["Bon à savoir", "i"] };
  var SOURCES = { partage: "Composition partagée par une utilisatrice du carnet", obf: "Fiche Open Beauty Facts", "obf-live": "Fiche Open Beauty Facts", opf: "Fiche Open Products Facts", "opf-live": "Fiche Open Products Facts", off: "Fiche Open Food Facts", "off-live": "Fiche Open Food Facts" };
  function lienSource(p) {
    var s = String(p.source || ""), b = /^opf/.test(s) ? OPF : /^off/.test(s) ? OFF : /^obf/.test(s) ? OBF : "";
    return SOURCES[s] ? (b && p.code ? '<a href="' + b + "/product/" + esc(p.code) + '" rel="noopener" target="_blank">' + SOURCES[s] + "</a>" : SOURCES[s]) : "";
  }
  function rendre(liste, p, silencieux, origine, texte, autres) {
    var cat = dernier && dernier.liste === liste && dernier.cat ? dernier.cat : M.categorie(p, liste);
    dernier = { liste: liste, produit: p, cat: cat, origine: origine || (dernier && dernier.origine), texte: texte != null ? texte : dernier && dernier.texte, autres: autres || (dernier && dernier.liste === liste ? dernier.autres : null) };
    origine = dernier.origine;
    var A = M.analyser(liste, profil), C = CATS[cat], S = M.scorer(A, profil, cat);
    var complet = profil.texture && profil.cuir;
    var h = '<div class="scan-out">';
    if (p && (p.nom || p.marque)) h += '<div class="scan-prod">' + (p.image ? '<img src="' + esc(p.image) + '" alt="Photo du produit ' + esc(p.nom) + '" width="72" height="72">' : "") +
      '<div><p class="marque">' + esc(p.marque || "") + '</p><h3>' + esc(p.nom || "Produit sans nom") + '</h3><p class="small">' + (p.code ? "Code " + esc(p.code) : "") +
      (origine === "base" && lienSource(p) ? " · " + lienSource(p) : origine === "ocr" ? " · liste lue sur ta photo" : origine === "collage" ? " · liste collée" : "") + "</p></div></div>";
    if (p && p.approchante && origine === "base") {
      var de = p.approchante.de || {};
      h += '<div class="scan-appro" role="note"><p><strong>' + (p.approchante.choisi ? "Fiche choisie dans la liste" : "Fiche approchante") + ", vérifie sur ton flacon.</strong> " +
        (de.code ? "Le code-barres " + esc(de.code) + (de.nom ? " (" + esc(de.nom) + ")" : "") + " n'a pas encore sa liste d'ingrédients dans les bases. " : "") +
        "Voici l'analyse de « " + esc(p.nom) + " », un produit au nom proche. Les formules changent selon les versions et les pays : si la liste au dos est différente, " +
        '<button type="button" class="lien" data-vers="p-photo">photographie-la</button> pour une analyse exacte.</p></div>';
    }
    if (A.groupes.some(function (g) { return g.r.id === "retire"; }))
      h += '<div class="scan-appro" role="note"><p><strong>Ancienne formule probable.</strong> Cette liste contient un ingrédient qui n\'est plus autorisé dans les cosmétiques vendus dans l\'UE : la fiche décrit sans doute une version précédente du produit. Le score porte sur cette liste : vérifie celle de ton flacon.</p></div>';
    // Pastille du score
    var titre = S.mode === "compat" ? "Score de compatibilité avec tes cheveux" : "Score de douceur de la formule";
    var pour = S.mode === "compat" ? "Pour des cheveux " + TEXTURES[profil.texture].toLowerCase() + (profil.fin ? " et fins" : "") + ", cuir chevelu " + CUIRS[profil.cuir].toLowerCase() :
      S.capillaire ? "Le même pour tout le monde. Choisis ton type de cheveux et ton cuir chevelu en haut du scanner pour voir ta compatibilité." : "Le même pour tout le monde : il décrit la douceur de la formule pour la peau.";
    h += '<div class="score s-' + S.palier + '" role="status"><div class="score-n" aria-hidden="true"><b>' + S.score + '</b><span>/100</span></div><div>' +
      '<p class="kicker">' + titre + '</p><p class="vt"><span class="sr">' + S.score + " sur 100 : </span>" + esc(S.libelle) + '</p><p class="small">' + esc(pour) + "</p></div></div>";
    // Type de produit : détecté, modifiable (replié sous le score)
    h += '<details class="scan-cat"' + (p ? "" : " open") + '><summary>Type de produit : <b>' + esc(C.nom) + "</b>" + (p ? " (détecté)" : "") + ' <span class="lien">changer</span></summary><div class="chips" role="group" aria-label="Type de produit">' + Object.keys(CATS).map(function (k) {
      return '<button type="button" class="chip" data-cat="' + k + '" aria-pressed="' + (k === cat) + '">' + esc(CATS[k].nom) + "</button>"; }).join("") + "</div></details>";
    h += '<details class="fam score-det"><summary><b>Comment ce score est calculé</b> <span>' + (S.lignes.length + 1) + " lignes</span></summary><ul class=\"score-l\"><li><span class=\"pt\">" + S.base + "</span> Point de départ, pour toutes les formules</li>" +
      S.lignes.map(function (l) { return '<li><span class="pt ' + (l.pts > 0 ? "plus" : "moins") + '">' + (l.pts > 0 ? "+" : "−") + Math.abs(l.pts) + "</span> " + esc(l.label) + (l.type === "profil" ? " <small>(selon ton profil)</small>" : "") + "</li>"; }).join("") +
      '<li class="tot"><span class="pt">' + S.score + "</span> Score, ramené entre 0 et 100</li></ul>" +
      '<p class="small">Score indicatif basé uniquement sur la liste d\'ingrédients, pas sur les quantités, qui ne figurent pas sur l\'étiquette. Il ne juge pas la marque et ne remplace pas un avis médical. ' +
      (S.capillaire ? "Le même produit peut avoir un score différent selon le profil : c'est voulu. " : "") + '<a href="/methode-score/">La méthode complète</a></p></details>';
    h += '<p class="small">' + A.liste.length + " ingrédients lus, " + A.reconnus + " reconnus par la base du carnet.</p>";
    h += '<ul class="badges">' + A.badges.map(function (b) { return '<li class="b-' + b[1] + '">' + esc(b[0]) + "</li>"; }).join("") + "</ul>";
    var pts = A.points.filter(function (x) { return C.lave || !/^lavant/.test(x.regle.groupe); }).sort(function (a, b) { return "peu prudence ok info".indexOf(a.niveau) - "peu prudence ok info".indexOf(b.niveau); });
    if (C.capillaire && complet && pts.length) {
      h += "<h3>Point par point, pour ton profil</h3><ul class=\"pts-scan\">" + pts.map(function (x) {
        return '<li class="n-' + x.niveau + '"><span class="ico" aria-hidden="true">' + NIV[x.niveau][1] + '</span><span><b>' + NIV[x.niveau][0] + " · " + esc(x.regle.label) + "</b> (" +
          esc(x.ings.slice(0, 3).map(function (i) { return i.nom; }).join(", ")) + (x.ings.length > 3 ? "…" : "") + ")<br>" + esc(x.texte) + "</span></li>";
      }).join("") + "</ul>";
    } else if (C.capillaire && complet) h += "<p>Aucun ingrédient de cette liste ne pose de question particulière pour ton profil.</p>";
    h += "<h3>Ce qu'il y a dedans</h3><div class=\"fams\">" + A.groupes.map(function (g) {
      var notes = g.r.notes ? g.ings.map(function (i) { return g.r.notes[i.nom] ? "<li>" + esc(i.nom) + " : " + esc(g.r.notes[i.nom]) + "</li>" : ""; }).join("") : "";
      return '<details class="fam f-' + esc(g.r.groupe) + '"><summary><b>' + esc(g.r.label) + "</b> <span>" + g.ings.length + "</span></summary><p>" + esc(g.r.fait) + "</p>" +
        "<p class=\"small\">" + g.ings.map(function (i) { return esc(i.nom) + " (n°" + i.rang + ")"; }).join(", ") + "</p>" + (notes ? "<ul class=\"small\">" + notes + "</ul>" : "") + "</details>";
    }).join("") + "</div>";
    h += '<details class="fam"><summary><b>La liste complète, dans l\'ordre</b> <span>' + A.liste.length + "</span></summary><ol class=\"inci-l\">" + A.liste.map(function (i) {
      return "<li>" + esc(i.nom) + (i.regles.length ? ' <small>' + esc(i.regles.map(function (r) { return r.label; }).join(", ")) + "</small>" : !i.connu ? ' <small>non classé</small>' : "") +
        (i.corrige ? ' <small class="corr">lu « ' + esc(i.brut) + ' », corrigé</small>' : "") + "</li>";
    }).join("") + "</ol><p class=\"small\">Les ingrédients sont classés du plus présent au moins présent. Sous 1 %, l'ordre est libre (règlement CE 1223/2009, article 19).</p></details>";
    if (dernier.autres && dernier.autres.length) h += '<details class="fam"><summary><b>Pas le bon produit ? Fiches proches</b> <span>' + dernier.autres.length + '</span></summary><ul class="scan-choix scan-autres">' + itemsHTML(dernier.autres) + "</ul></details>";
    // Partage de la composition (seulement si elle vient de l'utilisatrice, avec un code-barres, et avec son accord explicite)
    if ((dernier.origine === "ocr" || dernier.origine === "collage") && dernier.texte) {
      var pp = p || {};
      h += '<form class="scan-share" id="scan-share" novalidate><h3>Aide les prochaines personnes</h3><p class="small">Ce produit n\'avait pas sa composition dans les bases. Si tu la partages, la prochaine personne qui scannera ce code-barres aura son analyse tout de suite.</p>' +
        '<div class="share-g"><label>Code-barres<input name="ean" inputmode="numeric" autocomplete="off" value="' + esc(pp.code || codeAttente || "") + '" required></label>' +
        '<label>Marque<input name="marque" autocomplete="off" maxlength="120" value="' + esc(pp.marque || "") + '"></label>' +
        '<label>Nom du produit<input name="nom" autocomplete="off" maxlength="120" value="' + esc(pp.nom || "") + '" required></label></div>' +
        '<label class="scan-fin"><input type="checkbox" name="ok"> Partager cette composition pour aider les autres</label>' +
        '<p class="small">Seuls le code-barres, la marque, le nom et la liste d\'ingrédients sont envoyés. Aucune photo, aucune donnée personnelle. <a href="/mentions-legales/#confidentialite">Confidentialité</a></p>' +
        '<button class="btn btn-o" type="submit">Partager la composition</button><p class="share-msg" aria-live="polite"></p></form>';
    }
    h += '<p class="small scan-mention">' + (origine === "base" && p && p.licence ? "Données " + esc(p.licence.replace("ODbL ", "")) + " (licence ODbL), ingrédients à vérifier sur l'emballage. " : "Ingrédients à vérifier sur l'emballage. ") +
      "Repères : règlement cosmétique européen 1223/2009, liste des allergènes à déclarer, base CosIng de la Commission européenne. " + '<a href="#sources-scan">Les sources</a></p>';
    if (window.CC && complet && C.capillaire) {
      var tags = [];
      if (profil.cuir === "pellicules" || profil.cuir === "gras") tags.push(profil.cuir);
      if (profil.cuir === "sec") tags.push("sensible", "sec");
      tags.push(profil.texture === "frises" ? "crepus" : profil.texture);
      if (profil.fin) tags.push("fins");
      if (profil.cuir === "equilibre") tags.push("equilibre");
      var cats = cat === "masque" ? ["masque"] : cat === "shampoing" ? ["shampoing"] : ["soin", "masque"];
      var alt = window.CC.top(tags, { n: 3, cats: cats, oblig: cat === "shampoing" && profil.cuir === "pellicules" ? "pellicules" : null });
      if (alt.length < 3) alt = alt.concat(window.CC.top(tags, { n: 3 - alt.length, cats: cats, excl: alt.map(function (x) { return x.id; }) }));
      var guide = profil.texture === "raides" && profil.fin ? "fins" : profil.texture;
      var quoi = cat === "masque" ? "masques" : cat === "shampoing" ? "shampoings" : "soins";
      h += '<section class="scan-alt" aria-labelledby="scan-alt-t"><h3 id="scan-alt-t">' + (alt.length === 3 ? "Trois " : "Des ") + quoi + ' pensés pour ton profil</h3>' +
        '<p class="small">Choisis dans le catalogue des tests du carnet, selon ton type de cheveux et ton cuir chevelu. Ce n\'est pas un jugement du produit analysé. <a href="/classement-shampoings/">Le classement des shampoings par type de cheveux</a></p>' +
        window.CC.cartes(alt) + "</section>" + window.CC.offre(guide);
    }
    h += '<p class="scan-redo"><a class="btn btn-o" href="/quiz-type-de-cheveux/">Faire le quiz complet</a> <button type="button" class="btn btn-o" id="scan-again">Analyser un autre produit</button></p></div>';
    res.innerHTML = h;
    $$("[data-cat]", res).forEach(function (b) { b.addEventListener("click", function () { dernier.cat = b.getAttribute("data-cat"); rendre(dernier.liste, dernier.produit, true); var c = $('[data-cat="' + dernier.cat + '"]', res); if (c) { c.closest("details").open = true; c.focus(); } }); });
    $$(".scan-autres .scan-item", res).forEach(function (b) { b.addEventListener("click", function () { var q = dernier.autres[+b.getAttribute("data-i")], de = p && p.approchante; q.approchante = de ? { de: de.de, choisi: true } : null; analyserFiche(q, false); }); });
    var bv = $(".scan-appro [data-vers]", res); if (bv) bv.addEventListener("click", function () { codeAttente = (p.approchante.de || {}).code || codeAttente; produitAttente = p.approchante.de || null; onglet("p-photo", true); root.scrollIntoView({ behavior: "smooth" }); });
    var fs = $("#scan-share", res); if (fs) fs.addEventListener("submit", partager);
    $("#scan-again", res).addEventListener("click", function () { dernier = null; produitAttente = null; codeAttente = ""; res.innerHTML = ""; message(""); root.scrollIntoView({ behavior: "smooth" }); onglet("p-code", true); });
    if (!silencieux) { evt("scanner-analyse"); evt("scanner-score-" + S.palier); var t = $(".score .vt", res); if (t) { t.setAttribute("tabindex", "-1"); t.focus({ preventScroll: true }); } res.scrollIntoView({ behavior: "smooth", block: "start" }); }
  }

  // Lien direct depuis le classement : /composition-shampoing/?ean=… lance la recherche
  (function () { var m = location.search.match(/[?&]ean=(\d{8,14})\b/); if (m && eanValide(m[1])) { $("#scan-ean").value = m[1]; chercherCode(m[1]); } })();

  function partager(e) {
    e.preventDefault();
    var f = e.target, out = $(".share-msg", f), ean = f.ean.value.replace(/\D/g, "");
    if (ean.length === 12) ean = "0" + ean;
    if (!f.ok.checked) { out.textContent = "Coche la case pour accepter de partager la composition."; f.ok.focus(); return; }
    if (!eanValide(ean)) { out.textContent = "Le code-barres ne semble pas complet : vérifie les chiffres sous les barres."; f.ean.focus(); return; }
    if (f.nom.value.trim().length < 2) { out.textContent = "Indique le nom du produit, comme sur le flacon."; f.nom.focus(); return; }
    var corps = { ean: ean, nom: f.nom.value.trim().slice(0, 120), marque: f.marque.value.trim().slice(0, 120), inci: String(dernier.texte).replace(/[<>]/g, " ").trim().slice(0, 4000),
      categorie: dernier.cat, source: dernier.origine === "ocr" ? "ocr" : "collage", consentement: true };
    out.textContent = "Envoi…";
    fetch(API + "/produit", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corps) }).then(function (r) {
      if (r.status === 201) { evt("scanner-partage"); f.querySelector("button").disabled = true; out.textContent = "Merci ! La composition est partagée : la prochaine personne qui scannera ce code-barres aura son analyse."; return; }
      out.textContent = r.status === 429 ? "Tu as déjà beaucoup partagé aujourd'hui : réessaie plus tard. Merci !" : "Le partage n'a pas été accepté : vérifie le code-barres et la liste (au moins trois ingrédients séparés par des virgules).";
    }).catch(function () { out.textContent = "Le partage n'a pas pu être envoyé (connexion ?). Réessaie dans un moment."; });
  }
})();
