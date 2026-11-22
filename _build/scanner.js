/* Carnet capillaire : scanner de composition (page /composition-shampoing/).
   100 % dans le navigateur. Rien n'est envoyé au site ni enregistré, sauf :
   - le code-barres ou le nom tapé, envoyés à l'API publique Open Beauty Facts pour trouver le produit ;
   - ton profil (type de cheveux, cuir chevelu), gardé dans ton navigateur (localStorage, try/catch) pour ne pas te le redemander.
   La photo de la liste d'ingrédients est lue sur ton appareil (Tesseract.js) : elle ne quitte pas ton téléphone.
   Base de règles : _build/ingredients.json, injectée par le build dans window.CC_INGR.
   Librairies chargées seulement au clic : ZXing (code-barres, si BarcodeDetector n'existe pas) et Tesseract.js (photo). */
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

    return { norm: norm, squash: squash, lev: lev, reconnait: reconnait, decouper: decouper, analyser: analyser, nettoyerOCR: nettoyerOCR };
  }

  if (typeof module !== "undefined" && module.exports) { module.exports = creerMoteur; return; } // tests sous Node

  /* ===================== 2. Interface ===================== */
  var root = document.getElementById("scanner");
  if (!root || !window.CC_INGR) return;
  var M = creerMoteur(window.CC_INGR);
  var OBF = "https://world.openbeautyfacts.org";
  var ZXING = "https://cdn.jsdelivr.net/npm/@zxing/library@0.21.3/umd/index.min.js";
  var ZXING_SRI = "sha384-BzBxP10ZE72aitqj5UMmUsbKFliP/DZqA8Wq+BNNhlIJDGoEd1tpkMYXOg9+n6sB";
  var TESS = "https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js";
  var K = "cc_profil";
  function $(s, el) { return (el || root).querySelector(s); }
  function $$(s, el) { return Array.prototype.slice.call((el || root).querySelectorAll(s)); }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function evt(n) { if (window.cc_evt) window.cc_evt(n); }
  function lire() { try { return JSON.parse(localStorage.getItem(K) || "null"); } catch (e) { return null; } }
  function ecrire(v) { try { localStorage.setItem(K, JSON.stringify(v)); } catch (e) {} }

  var TEXTURES = { raides: "Raides", ondules: "Ondulés", boucles: "Bouclés", frises: "Frisés", crepus: "Crépus" };
  var CUIRS = { equilibre: "Équilibré", gras: "Gras", sec: "Sec ou sensible", pellicules: "Pellicules" };
  var profil = lire() || {};
  if (!TEXTURES[profil.texture]) profil.texture = "";
  if (!CUIRS[profil.cuir]) profil.cuir = "";
  var dernier = null; // { liste, produit }

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
      var s = document.createElement("script"); s.src = src; s.async = true; s.crossOrigin = "anonymous";
      if (sri) s.integrity = sri;
      s.onload = ok; s.onerror = function () { delete charges[src]; ko(new Error("chargement")); };
      document.head.appendChild(s);
    });
    return charges[src];
  }

  // --- (a) Caméra et code-barres ---
  var video = $("#scan-video"), camBox = $("#scan-cam"), flux = null, boucle = null;
  function stopCamera() {
    if (boucle) { clearTimeout(boucle); boucle = null; }
    if (flux) { flux.getTracks().forEach(function (t) { t.stop(); }); flux = null; }
    if (camBox) camBox.hidden = true;
    var b = $("#scan-go"); if (b) b.hidden = false;
  }
  $("#scan-stop").addEventListener("click", function () { stopCamera(); message(""); });
  $("#scan-go").addEventListener("click", function () {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      message("Ton navigateur ne donne pas accès à la caméra. Tape le code-barres juste en dessous, ou photographie la liste d'ingrédients.", "warn"); return;
    }
    message("Ton navigateur va te demander l'accès à la caméra. Elle sert seulement à lire le code-barres : aucune image n'est enregistrée ni envoyée.");
    navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 } }, audio: false }).then(function (s) {
      flux = s; video.srcObject = s; camBox.hidden = false; $("#scan-go").hidden = true;
      return video.play();
    }).then(function () {
      message("Vise le code-barres, bien à plat, à 10 ou 15 cm.");
      evt("scanner-camera");
      return detecteur();
    }).then(function (lireImage) {
      if (!lireImage || !flux) return;
      var essai = function () {
        if (!flux) return;
        lireImage().then(function (code) {
          if (code && flux) { stopCamera(); if (navigator.vibrate) navigator.vibrate(60); $("#scan-ean").value = code; chercherCode(code); }
          else boucle = setTimeout(essai, 250);
        }).catch(function () { boucle = setTimeout(essai, 400); });
      };
      essai();
    }).catch(function (e) {
      stopCamera();
      if (e && e.message === "chargement") message("Le lecteur de code-barres n'a pas pu se charger (connexion ?). Tape le code à la main, juste en dessous.", "warn");
      else message("Pas d'accès à la caméra" + (e && e.name === "NotAllowedError" ? " (autorisation refusée)" : "") + ". Tu peux taper le code-barres juste en dessous, ou photographier la liste d'ingrédients.", "warn");
    });
  });
  function detecteur() { // BarcodeDetector natif si possible, sinon ZXing chargé maintenant
    var formats = ["ean_13", "ean_8", "upc_a", "upc_e"];
    if ("BarcodeDetector" in window) {
      return window.BarcodeDetector.getSupportedFormats().then(function (f) {
        if (f.indexOf("ean_13") < 0) throw new Error("format");
        var d = new window.BarcodeDetector({ formats: formats.filter(function (x) { return f.indexOf(x) >= 0; }) });
        return function () { return d.detect(video).then(function (r) { return r.length ? r[0].rawValue : null; }); };
      }).catch(function () { return zxing(); });
    }
    return zxing();
  }
  function zxing() {
    return script(ZXING, ZXING_SRI).then(function () {
      var Z = window.ZXing, hints = new Map();
      hints.set(Z.DecodeHintType.POSSIBLE_FORMATS, [Z.BarcodeFormat.EAN_13, Z.BarcodeFormat.EAN_8, Z.BarcodeFormat.UPC_A, Z.BarcodeFormat.UPC_E]);
      hints.set(Z.DecodeHintType.TRY_HARDER, true);
      var r = new Z.MultiFormatReader(); r.setHints(hints);
      var cv = document.createElement("canvas"), cx = cv.getContext("2d", { willReadFrequently: true }), tour = 0;
      return function () { // une image sur deux tournée d'un quart de tour : code-barres horizontal ou vertical
        var w = video.videoWidth, h = video.videoHeight;
        if (!w) return Promise.resolve(null);
        var s = Math.min(1, 960 / Math.max(w, h)), rot = tour++ % 2 === 1;
        cv.width = (rot ? h : w) * s; cv.height = (rot ? w : h) * s;
        cx.setTransform(1, 0, 0, 1, 0, 0);
        if (rot) { cx.translate(cv.width, 0); cx.rotate(Math.PI / 2); }
        cx.drawImage(video, 0, 0, w * s, h * s);
        try { return Promise.resolve(r.decode(new Z.BinaryBitmap(new Z.HybridBinarizer(new Z.HTMLCanvasElementLuminanceSource(cv)))).getText()); }
        catch (e) { return Promise.resolve(null); }
      };
    });
  }

  // --- (b) Code tapé, et requêtes Open Beauty Facts ---
  var CHAMPS = "code,product_name,product_name_fr,generic_name_fr,brands,image_front_small_url,ingredients_text,ingredients_text_fr,ingredients_text_en,categories_tags";
  function getJSON(u) {
    var ctl = "AbortController" in window ? new AbortController() : null, t = ctl && setTimeout(function () { ctl.abort(); }, 12000);
    return fetch(u, ctl ? { signal: ctl.signal } : {}).then(function (r) { clearTimeout(t); if (r.status === 404) return { status: 0 }; if (!r.ok) throw new Error("http"); return r.json(); });
  }
  function nomDe(p) { return p.product_name_fr || p.product_name || p.generic_name_fr || "Produit sans nom"; }
  function inciDe(p) { return p.ingredients_text_fr || p.ingredients_text || p.ingredients_text_en || ""; }
  $("#scan-form-code").addEventListener("submit", function (e) {
    e.preventDefault();
    var c = $("#scan-ean").value.replace(/\D/g, "");
    if (c.length < 8 || c.length > 14) { message("Un code-barres compte 8 ou 13 chiffres en général (sous les barres). Vérifie et réessaie.", "warn"); $("#scan-ean").focus(); return; }
    chercherCode(c);
  });
  function chercherCode(c) {
    message("Recherche du produit " + esc(c) + " dans Open Beauty Facts…"); res.innerHTML = "";
    getJSON(OBF + "/api/v2/product/" + encodeURIComponent(c) + ".json?fields=" + CHAMPS).then(function (d) {
      if (!d || d.status !== 1 || !d.product) { evt("scanner-code-absent"); return bascule("Ce code-barres (" + esc(c) + ") n'est pas encore dans Open Beauty Facts."); }
      var p = d.product, inci = inciDe(p);
      if (M.decouper(inci).length < 3) { evt("scanner-code-sans-inci"); return bascule((p.product_name_fr || p.product_name ? "<strong>" + esc(nomDe(p)) + "</strong> est bien" : "Ce produit est bien") + " dans Open Beauty Facts, mais sans sa liste d'ingrédients.", p); }
      evt("scanner-code-ok"); message("");
      analyserTexte(inci, p);
    }).catch(function () { message("La base Open Beauty Facts ne répond pas pour l'instant. Réessaie dans un moment, ou photographie la liste d'ingrédients.", "warn"); });
  }
  // Produit absent : bascule automatique vers la photo, avec le collage en second choix
  function bascule(txt, p) {
    onglet("p-photo", true);
    message(txt + " Pas de souci : <strong>photographie la liste d'ingrédients</strong> au dos du flacon ci-dessous, ou " +
      '<button type="button" class="lien" data-vers="p-coller">colle-la</button> si tu l\'as sous les yeux sur un site.', "warn");
    var b = $("[data-vers]", etat); if (b) b.addEventListener("click", function () { onglet("p-coller", true); $("#scan-inci").focus(); });
    produitAttente = p || null;
  }
  var produitAttente = null;

  // --- Recherche par nom ou marque ---
  $("#scan-form-nom").addEventListener("submit", function (e) {
    e.preventDefault();
    var q = $("#scan-q").value.trim(), out = $("#scan-liste");
    if (q.length < 3) { message("Tape au moins 3 lettres : la marque et le nom du produit, par exemple « elseve total repair ».", "warn"); return; }
    message("Recherche de « " + esc(q) + " »…"); out.innerHTML = "";
    getJSON(OBF + "/cgi/search.pl?search_terms=" + encodeURIComponent(q) + "&search_simple=1&action=process&json=1&page_size=24&fields=" + CHAMPS).then(function (d) {
      var ps = (d.products || []).filter(function (p) { return p.code; });
      ps.sort(function (a, b) { return (M.decouper(inciDe(b)).length >= 3) - (M.decouper(inciDe(a)).length >= 3); });
      if (!ps.length) { evt("scanner-nom-vide"); return bascule("Aucun produit trouvé pour « " + esc(q) + " ». Il n'est peut-être pas encore dans Open Beauty Facts."); }
      message(ps.length + " produit" + (ps.length > 1 ? "s" : "") + " trouvé" + (ps.length > 1 ? "s" : "") + ". Choisis le tien.");
      out.innerHTML = ps.slice(0, 12).map(function (p, i) {
        var ok = M.decouper(inciDe(p)).length >= 3;
        return '<li><button type="button" class="scan-item" data-i="' + i + '">' +
          (p.image_front_small_url ? '<img src="' + esc(p.image_front_small_url) + '" alt="" width="44" height="44" loading="lazy">' : '<span class="ph0" aria-hidden="true"></span>') +
          '<span><b>' + esc(nomDe(p)) + "</b><small>" + esc(p.brands || "Marque inconnue") + (ok ? "" : " · ingrédients absents") + "</small></span></button></li>";
      }).join("");
      $$(".scan-item", out).forEach(function (b) {
        b.addEventListener("click", function () {
          var p = ps[+b.getAttribute("data-i")];
          if (M.decouper(inciDe(p)).length < 3) return bascule("<strong>" + esc(nomDe(p)) + "</strong> est dans Open Beauty Facts, mais sans sa liste d'ingrédients.", p);
          evt("scanner-nom-ok"); message(""); analyserTexte(inciDe(p), p);
        });
      });
    }).catch(function () { message("La recherche Open Beauty Facts ne répond pas pour l'instant. Réessaie, ou photographie la liste d'ingrédients.", "warn"); });
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
      // Texte proposé à la relecture : le nom reconnu (corrigé) quand on le connaît, sinon le texte tel qu'il a été lu
      zone.value = liste.length >= 3 ? liste.map(function (x) { return x.connu ? x.nom.toUpperCase() : x.brut; }).join(", ") : M.nettoyerOCR(texte).trim();
      if (liste.length < 3) { message("Je n'ai pas réussi à lire la liste. Reprends la photo de plus près, bien à plat et sans reflet, ou tape les premiers ingrédients ci-dessous.", "warn"); zone.focus(); return; }
      message("Voici le texte lu sur ta photo (" + liste.length + " ingrédients). Vérifie-le et corrige si besoin, puis lance l'analyse.");
      rendre(liste, produitAttente, false); // on analyse la liste lue (avec les corrections signalées) ; « Analyser » relance sur le texte corrigé à la main
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
    message(""); evt("scanner-inci"); analyserTexte(t, produitAttente, "coller");
  });

  function analyserTexte(t, p) { rendre(M.decouper(t), p || null, false); }

  // --- Résultat ---
  var NIV = { ok: ["Point positif", "+"], prudence: ["À surveiller", "!"], peu: ["Peu adapté", "×"], info: ["Bon à savoir", "i"] };
  var VERD = { ok: "Plutôt adapté à ton profil", prudence: "À utiliser avec précaution", peu: "Peu adapté à ton profil" };
  function rendre(liste, p, silencieux) {
    dernier = { liste: liste, produit: p };
    var A = M.analyser(liste, profil);
    var complet = profil.texture && profil.cuir;
    var h = '<div class="scan-out">';
    if (p) h += '<div class="scan-prod">' + (p.image_front_small_url ? '<img src="' + esc(p.image_front_small_url) + '" alt="Photo du produit ' + esc(nomDe(p)) + '" width="72" height="72">' : "") +
      '<div><p class="marque">' + esc(p.brands || "") + '</p><h3>' + esc(nomDe(p)) + '</h3><p class="small">Code ' + esc(p.code) + ' · <a href="' + OBF + "/product/" + esc(p.code) + '" rel="noopener" target="_blank">Fiche Open Beauty Facts</a></p></div></div>';
    h += '<p class="small">' + A.liste.length + " ingrédients lus, " + A.reconnus + " reconnus par la base du carnet.</p>";
    if (complet) {
      h += '<div class="verdict v-' + A.verdict + '" role="status"><p class="kicker">Pour des cheveux ' + esc(TEXTURES[profil.texture].toLowerCase()) + (profil.fin ? " et fins" : "") +
        ", cuir chevelu " + esc(CUIRS[profil.cuir].toLowerCase()) + '</p><p class="vt">' + VERD[A.verdict] + "</p>" +
        '<p class="small">Une lecture de la composition, pas un avis sur la marque ni une note. Les quantités exactes ne figurent pas sur l\'étiquette.</p></div>';
    } else {
      h += '<div class="verdict v-info" role="status"><p class="vt">Choisis ton type de cheveux et ton cuir chevelu</p><p class="small">En haut du scanner, en 2 clics : l\'analyse de compatibilité s\'affichera ici.</p></div>';
    }
    h += '<ul class="badges">' + A.badges.map(function (b) { return '<li class="b-' + b[1] + '">' + esc(b[0]) + "</li>"; }).join("") + "</ul>";
    var pts = A.points.slice().sort(function (a, b) { return "peu prudence ok info".indexOf(a.niveau) - "peu prudence ok info".indexOf(b.niveau); });
    if (complet && pts.length) {
      h += "<h3>Point par point, pour ton profil</h3><ul class=\"pts-scan\">" + pts.map(function (x) {
        return '<li class="n-' + x.niveau + '"><span class="ico" aria-hidden="true">' + NIV[x.niveau][1] + '</span><span><b>' + NIV[x.niveau][0] + " · " + esc(x.regle.label) + "</b> (" +
          esc(x.ings.slice(0, 3).map(function (i) { return i.nom; }).join(", ")) + (x.ings.length > 3 ? "…" : "") + ")<br>" + esc(x.texte) + "</span></li>";
      }).join("") + "</ul>";
    } else if (complet) h += "<p>Aucun ingrédient de cette liste ne pose de question particulière pour ton profil.</p>";
    // Ce qu'il y a dedans, par famille
    h += "<h3>Ce qu'il y a dedans</h3><div class=\"fams\">" + A.groupes.map(function (g) {
      var notes = g.r.notes ? g.ings.map(function (i) { return g.r.notes[i.nom] ? "<li>" + esc(i.nom) + " : " + esc(g.r.notes[i.nom]) + "</li>" : ""; }).join("") : "";
      return '<details class="fam f-' + esc(g.r.groupe) + '"><summary><b>' + esc(g.r.label) + "</b> <span>" + g.ings.length + "</span></summary><p>" + esc(g.r.fait) + "</p>" +
        "<p class=\"small\">" + g.ings.map(function (i) { return esc(i.nom) + " (n°" + i.rang + ")"; }).join(", ") + "</p>" + (notes ? "<ul class=\"small\">" + notes + "</ul>" : "") + "</details>";
    }).join("") + "</div>";
    h += '<details class="fam"><summary><b>La liste complète, dans l\'ordre</b> <span>' + A.liste.length + "</span></summary><ol class=\"inci-l\">" + A.liste.map(function (i) {
      return "<li>" + esc(i.nom) + (i.regles.length ? ' <small>' + esc(i.regles.map(function (r) { return r.label; }).join(", ")) + "</small>" : !i.connu ? ' <small>non classé</small>' : "") +
        (i.corrige ? ' <small class="corr">lu « ' + esc(i.brut) + ' », corrigé</small>' : "") + "</li>";
    }).join("") + "</ol><p class=\"small\">Les ingrédients sont classés du plus présent au moins présent. Sous 1 %, l'ordre est libre (règlement CE 1223/2009, article 19).</p></details>";
    h += '<p class="small scan-mention">' + (p ? "Données <a href=\"https://world.openbeautyfacts.org/\" rel=\"noopener\" target=\"_blank\">Open Beauty Facts</a> (licence ODbL), ingrédients à vérifier sur l'emballage. " : "Ingrédients à vérifier sur l'emballage. ") +
      "Repères : règlement cosmétique européen 1223/2009, liste des allergènes à déclarer, base CosIng de la Commission européenne. " + '<a href="#sources-scan">Les sources</a></p>';
    // Conversion : 3 alternatives du catalogue, guide PDF du type, quiz
    if (window.CC && complet) {
      var tags = [];
      if (profil.cuir === "pellicules" || profil.cuir === "gras") tags.push(profil.cuir);
      if (profil.cuir === "sec") tags.push("sensible", "sec");
      tags.push(profil.texture === "frises" ? "crepus" : profil.texture);
      if (profil.fin) tags.push("fins");
      if (profil.cuir === "equilibre") tags.push("equilibre");
      var alt = window.CC.top(tags, { n: 3, oblig: profil.cuir === "pellicules" ? "pellicules" : null });
      if (alt.length < 3) alt = alt.concat(window.CC.top(tags, { n: 3 - alt.length, excl: alt.map(function (x) { return x.id; }) }));
      var guide = profil.texture === "raides" && profil.fin ? "fins" : profil.texture;
      h += '<section class="scan-alt" aria-labelledby="scan-alt-t"><h3 id="scan-alt-t">Trois shampoings pensés pour ton profil</h3>' +
        '<p class="small">Choisis dans le catalogue des tests du carnet, selon ton type de cheveux et ton cuir chevelu. Ce n\'est pas un jugement du produit analysé.</p>' +
        window.CC.cartes(alt) + "</section>" + window.CC.offre(guide);
    }
    h += '<p class="scan-redo"><a class="btn btn-o" href="/quiz-type-de-cheveux/">Faire le quiz complet</a> <button type="button" class="btn btn-o" id="scan-again">Analyser un autre produit</button></p></div>';
    res.innerHTML = h;
    $("#scan-again", res).addEventListener("click", function () { dernier = null; produitAttente = null; res.innerHTML = ""; message(""); root.scrollIntoView({ behavior: "smooth" }); onglet("p-code", true); });
    if (!silencieux) { evt("scanner-analyse"); var t = $(".verdict .vt", res); if (t) { t.setAttribute("tabindex", "-1"); t.focus({ preventScroll: true }); } res.scrollIntoView({ behavior: "smooth", block: "start" }); }
  }
})();
