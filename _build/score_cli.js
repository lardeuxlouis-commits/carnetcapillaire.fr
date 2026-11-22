/* Calcul des scores au build (classement) avec EXACTEMENT le moteur du navigateur (scanner.js + ingredients.json).
   Entrée (stdin) : {"produits":[{id, nom, marque, categories, inci}], "profils":{clé:{texture,cuir,fin}}}
   Sortie (stdout) : {id: {cat, reconnus, n, retire, scores:{clé:{score,palier,libelle}}}} */
const creer = require("./scanner.js"), DB = require("./ingredients.json"), M = creer(DB);
let s = ""; process.stdin.on("data", d => s += d).on("end", () => {
  const E = JSON.parse(s), out = {};
  for (const p of E.produits) {
    const L = M.decouper(p.inci || ""); if (L.length < 3) continue;
    const cat = M.categorie(p, L), A0 = M.analyser(M.decouper(p.inci), {});
    const r = { cat, n: L.length, reconnus: A0.reconnus, retire: A0.groupes.some(g => g.r.id === "retire"), scores: {} };
    for (const [k, pr] of Object.entries(E.profils)) {
      const S = M.scorer(M.analyser(M.decouper(p.inci), pr), pr, cat);
      r.scores[k] = { score: S.score, palier: S.palier, libelle: S.libelle };
    }
    out[p.id] = r;
  }
  process.stdout.write(JSON.stringify(out));
});
