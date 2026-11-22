#!/usr/bin/env python3
"""Base produits du scanner de carnetcapillaire.fr (/composition-shampoing/). Stdlib uniquement (http.server + sqlite3).

Derrière Caddy : https://187-124-173-12.sslip.io/scan/...  ->  127.0.0.1:8083 (service systemd « scan », utilisateur scanobf)
  GET  /scan/produit/<ean>          fiche d'un code-barres (8 à 14 chiffres), cascade :
                                    1. partages des utilisatrices (INCI la plus fréquente, puis la plus récente)
                                    2. dump local Open Beauty Facts / Open Products Facts avec INCI, ou fiche « carnet-enrichi »
                                       (relevée sur les fiches des marques et distributeurs, table enrichi de scan.db) si OBF
                                       n'a pas d'INCI ou une INCI nettement plus courte (< 80 % de la fiche enrichie)
                                    3. API en direct OBF, Open Food Facts, OPF (cache 14 jours, positif et négatif)
                                    4. nom seul : dump sans INCI, cache, puis UPCitemdb (quota gratuit ~100/jour, coupe-circuit sur 429)
                                    200 {ean, nom, marque, inci, categories, image, source, licence} ; 404 {"status": 0}
                                    source = partage | obf | opf | carnet-enrichi | obf-live | off | opf-live | nom-obf | nom-off | nom-opf | upcitemdb
  GET  /scan/recherche?q=..&n=12    recherche par nom / marque (FTS5, sans accents), produits avec INCI d'abord, n <= 24
                                    200 {"produits": [{ean, nom, marque, inci, categories, image, source, licence}]}
  POST /scan/produit                {ean, nom, marque, inci, categorie, source: "ocr"|"collage", consentement: true}
                                    (8 Ko max, clé GTIN vérifiée, 10 par heure et 30 par jour par IP) -> 201 {"ok": true}
  GET  /scan/voisins/<ean>?n=12    EAN inconnu : marque devinée par le préfixe GS1 (9 à 6 chiffres, >= 3 produits)
                                    200 {marque_probable, prefixe, confiance (0-1), produits: [fiches avec INCI, même préfixe puis même marque, par proximité de l'EAN]}
  GET  /scan/top?n=60               EAN les plus consultés ayant une INCI : {"produits": [{ean, nom, marque, inci, categories, source, n}]}
  GET  /scan/sante                  {ok, nb_obf, nb_partages, nb_enrichi, date_import}

Données : /var/lib/scan/obf.db (dump, remplacé chaque dimanche 4 h par import_obf.py) et /var/lib/scan/scan.db
(partages, vues agrégées par EAN, cache des API externes). Aucune IP ni donnée personnelle n'est écrite :
la limite de débit garde en mémoire un hachage salé de l'IP (sel aléatoire à chaque démarrage).
Données Open Beauty Facts / Open Food Facts / Open Products Facts sous licence ODbL.
"""
from __future__ import annotations

import argparse, concurrent.futures, hashlib, json, os, re, secrets, sqlite3, threading, time, unicodedata, urllib.error, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DIR = os.environ.get("SCAN_DIR", "/var/lib/scan")
DB_OBF, DB_SCAN = os.path.join(DIR, "obf.db"), os.path.join(DIR, "scan.db")
ORIGINES = {"https://carnetcapillaire.fr", "https://www.carnetcapillaire.fr", "http://localhost:8090", "http://127.0.0.1:8090"}
UA = "CarnetCapillaire-scan/1.0 (https://carnetcapillaire.fr ; lardeuxlouis@gmail.com)"
LICENCE = {"obf": "ODbL Open Beauty Facts", "opf": "ODbL Open Products Facts", "obf-live": "ODbL Open Beauty Facts",
           "off": "ODbL Open Food Facts", "opf-live": "ODbL Open Products Facts", "nom-obf": "ODbL Open Beauty Facts",
           "nom-off": "ODbL Open Food Facts", "nom-opf": "ODbL Open Products Facts", "carnet-enrichi": ""}
LIVE = [("obf-live", "https://world.openbeautyfacts.org"), ("off", "https://world.openfoodfacts.org"), ("opf-live", "https://world.openproductsfacts.org")]
CHAMPS = "code,product_name,product_name_fr,generic_name_fr,brands,ingredients_text_fr,ingredients_text,ingredients_text_en,categories_tags,image_front_small_url"
CACHE_JOURS = 14
SEL = secrets.token_bytes(16)
_verrou = threading.Lock()
_debit: dict[str, list[float]] = {}          # hachage IP -> horodatages (POST)
_lect: dict[str, list[float]] = {}           # hachage IP -> horodatages (recherches externes)
_upc = {"jour": "", "n": 0, "bloque_jusqu": 0.0}
UPC_MAX_JOUR = 90


def plat(s):
    s = unicodedata.normalize("NFD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn").lower()).strip()


def gtin_ok(ean: str) -> bool:
    if not re.fullmatch(r"\d{8}|\d{12,14}", ean):
        return False
    corps, cle = ean[:-1], int(ean[-1])
    s = sum(int(d) * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(corps)))
    return (10 - s % 10) % 10 == cle


def scan_db():
    c = sqlite3.connect(DB_SCAN, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def obf_db():
    if not os.path.exists(DB_OBF):
        return None
    c = sqlite3.connect(f"file:{DB_OBF}?mode=ro", uri=True, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def init():
    os.makedirs(DIR, exist_ok=True)
    c = scan_db()
    c.executescript("""
      PRAGMA journal_mode=WAL;
      CREATE TABLE IF NOT EXISTS partages(id INTEGER PRIMARY KEY, ean TEXT, nom TEXT, marque TEXT, inci TEXT, categorie TEXT, source TEXT, date TEXT);
      CREATE INDEX IF NOT EXISTS partages_ean ON partages(ean);
      CREATE TABLE IF NOT EXISTS vues(ean TEXT PRIMARY KEY, n INTEGER, derniere_date TEXT);
      CREATE TABLE IF NOT EXISTS enrichi(ean TEXT PRIMARY KEY, nom TEXT, marque TEXT, gamme TEXT, type TEXT, format TEXT, inci TEXT,
                                         categories TEXT, url_source TEXT, site TEXT, date TEXT, note TEXT, cherche TEXT);
      CREATE TABLE IF NOT EXISTS cache_ext(ean TEXT, source TEXT, trouve INTEGER, nom TEXT, marque TEXT, inci TEXT, categories TEXT, image TEXT, date REAL,
                                           PRIMARY KEY(ean, source));
    """)
    c.commit(); c.close()


def fiche(ean, nom, marque, inci, categories, image, source, url_source=""):
    f = {"ean": ean, "nom": nom or "", "marque": marque or "", "inci": inci or "", "categories": categories or "",
         "image": image or "", "source": source, "licence": LICENCE.get(source, "")}
    if url_source:
        f["url_source"] = url_source
    return f


def depuis_enrichi(c, ean):
    r = c.execute("SELECT * FROM enrichi WHERE ean=?", (ean,)).fetchone()
    if not r or not r["inci"]:
        return None
    return fiche(ean, r["nom"], r["marque"], r["inci"], r["categories"] or r["type"], "", "carnet-enrichi", r["url_source"])


# --- Cascade, sans réseau (aussi utilisée par /scan/top) ---
def depuis_partages(c, ean):
    rows = c.execute("SELECT nom, marque, inci, categorie, date FROM partages WHERE ean=? ORDER BY date DESC", (ean,)).fetchall()
    if not rows:
        return None
    freq: dict[str, list] = {}
    for r in rows:
        k = re.sub(r"[^a-z0-9]", "", plat(r["inci"]))
        freq.setdefault(k, []).append(r)
    meilleur = max(freq.values(), key=lambda l: (len(l), l[0]["date"]))[0]
    nom = meilleur["nom"] or next((r["nom"] for r in rows if r["nom"]), "")
    marque = meilleur["marque"] or next((r["marque"] for r in rows if r["marque"]), "")
    return fiche(ean, nom, marque, meilleur["inci"], meilleur["categorie"], "", "partage")


def depuis_local(ean):
    o = obf_db()
    if not o:
        return None
    try:
        r = o.execute("SELECT * FROM obf WHERE ean=?", (ean,)).fetchone()
    finally:
        o.close()
    return r


def depuis_cache(c, ean, avec_inci):
    lim = time.time() - CACHE_JOURS * 86400
    for src in ("obf-live", "off", "opf-live", "upcitemdb"):
        r = c.execute("SELECT * FROM cache_ext WHERE ean=? AND source=? AND date>? AND trouve=1", (ean, src, lim)).fetchone()
        if r:
            if avec_inci and r["inci"]:
                return fiche(ean, r["nom"], r["marque"], r["inci"], r["categories"], r["image"], src)
            if not avec_inci and r["nom"]:
                s = {"obf-live": "nom-obf", "off": "nom-off", "opf-live": "nom-opf"}.get(src, src)
                return fiche(ean, r["nom"], r["marque"], "", r["categories"], r["image"], s)
    return None


def resoudre_local(c, ean):
    """Tout ce qui ne demande pas de réseau. Renvoie (fiche avec INCI | None, fiche nom seul | None)."""
    p = depuis_partages(c, ean)
    r = depuis_local(ean)
    if p:
        if not p["nom"] and r is not None:
            p["nom"], p["marque"] = r["nom"], r["marque"]
        return p, None
    e = depuis_enrichi(c, ean)
    if r is not None and r["inci"] and not (e and len(r["inci"]) < 0.8 * len(e["inci"])):
        return fiche(ean, r["nom"], r["marque"], r["inci"], r["categories"], r["image"], r["base"]), None
    if e:
        if r is not None and r["image"]:
            e["image"] = r["image"]
        return e, None
    f = depuis_cache(c, ean, True)
    if f:
        return f, None
    nom = None
    if r is not None and r["nom"]:
        nom = fiche(ean, r["nom"], r["marque"], "", r["categories"], r["image"], "nom-" + r["base"])
    return None, nom or depuis_cache(c, ean, False)


# --- Réseau ---
def get_json(url, timeout=7):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def live_un(src, base, ean):
    try:
        d = get_json(f"{base}/api/v2/product/{ean}.json?fields={CHAMPS}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return src, None, True
        return src, None, False
    except Exception:
        return src, None, False
    if d.get("status") != 1 or not d.get("product"):
        return src, None, True
    p = d["product"]
    nom = p.get("product_name_fr") or p.get("product_name") or p.get("generic_name_fr") or ""
    inci = p.get("ingredients_text_fr") or p.get("ingredients_text") or p.get("ingredients_text_en") or ""
    if src == "off" and inci and not re.search(r"aqua|water|glycerin|sodium|parfum|fragrance|cetearyl|dimethicone|betaine", inci, re.I):
        inci = ""  # ingrédients alimentaires : on ne garde que le nom
    return src, {"nom": nom.strip(), "marque": (p.get("brands") or "").split(",")[0].strip(), "inci": inci.strip(),
                 "categories": ",".join(p.get("categories_tags") or []), "image": p.get("image_front_small_url") or ""}, True


def upcitemdb(ean):
    with _verrou:
        jour = time.strftime("%Y-%m-%d")
        if _upc["jour"] != jour:
            _upc.update(jour=jour, n=0)
        if _upc["n"] >= UPC_MAX_JOUR or time.time() < _upc["bloque_jusqu"]:
            return None, False
        _upc["n"] += 1
    try:
        d = get_json(f"https://api.upcitemdb.com/prod/trial/lookup?upc={ean}")
    except urllib.error.HTTPError as e:
        if e.code == 429:
            reset = e.headers.get("X-RateLimit-Reset")
            with _verrou:
                _upc["bloque_jusqu"] = float(reset) if reset and reset.isdigit() and float(reset) > time.time() else time.time() + 3600
        return None, False
    except Exception:
        return None, False
    it = (d.get("items") or [None])[0]
    if not it or not it.get("title"):
        return None, True
    return {"nom": it.get("title", "")[:200], "marque": (it.get("brand") or "")[:120], "inci": "",
            "categories": it.get("category") or "", "image": (it.get("images") or [""])[0]}, True


def cacher(c, ean, src, data, definitif):
    if not definitif:
        return
    d = data or {}
    c.execute("INSERT OR REPLACE INTO cache_ext VALUES(?,?,?,?,?,?,?,?,?)",
              (ean, src, 1 if data else 0, d.get("nom", ""), d.get("marque", ""), d.get("inci", ""),
               d.get("categories", ""), d.get("image", ""), time.time()))


def deja_cache(c, ean, src):
    r = c.execute("SELECT date FROM cache_ext WHERE ean=? AND source=?", (ean, src)).fetchone()
    return bool(r) and r["date"] > time.time() - CACHE_JOURS * 86400


def resoudre(ean, reseau=True):
    c = scan_db()
    try:
        complet, nom = resoudre_local(c, ean)
        if complet or not reseau:
            return complet or nom
        a_faire = [(s, b) for s, b in LIVE if not deja_cache(c, ean, s)]
        if a_faire:
            with concurrent.futures.ThreadPoolExecutor(3) as ex:
                res = list(ex.map(lambda sb: live_un(sb[0], sb[1], ean), a_faire))
            for src, data, definitif in res:
                cacher(c, ean, src, data, definitif)
            c.commit()
            complet, nom2 = resoudre_local(c, ean)
            if complet:
                return complet
            nom = nom or nom2
        if nom:
            return nom
        if not deja_cache(c, ean, "upcitemdb"):
            data, definitif = upcitemdb(ean)
            cacher(c, ean, "upcitemdb", data, definitif)
            c.commit()
            if data:
                return fiche(ean, data["nom"], data["marque"], "", data["categories"], data["image"], "upcitemdb")
        return None
    finally:
        c.close()


def compter_vue(ean):
    c = scan_db()
    try:
        c.execute("INSERT INTO vues VALUES(?,1,?) ON CONFLICT(ean) DO UPDATE SET n=n+1, derniere_date=excluded.derniere_date",
                  (ean, time.strftime("%Y-%m-%d")))
        c.commit()
    finally:
        c.close()


def rechercher(q, n):
    mots = [m for m in re.findall(r"[a-z0-9]+", plat(q)) if len(m) >= 2][:6]
    if not mots:
        return []
    out, vus = [], set()
    c = scan_db()
    try:
        motif = "%" + "%".join(mots) + "%"
        for r in c.execute("SELECT ean, MAX(date) d FROM partages WHERE lower(nom || ' ' || marque) LIKE ? GROUP BY ean ORDER BY d DESC LIMIT 10", (motif,)):
            f = depuis_partages(c, r["ean"])
            if f and f["nom"]:
                out.append(f); vus.add(f["ean"])
        if len(out) < n:
            cond = " AND ".join(["cherche LIKE ?"] * len(mots))  # cherche = plat(marque nom gamme), écrit par charger_enrichi.py
            for r in c.execute("SELECT ean FROM enrichi WHERE " + cond + " LIMIT ?", [f"%{m}%" for m in mots] + [n]):
                if r["ean"] not in vus:
                    f, _ = resoudre_local(c, r["ean"])
                    if f:
                        out.append(f); vus.add(r["ean"])
    finally:
        c.close()
    o = obf_db()
    if o:
        try:
            sql = """SELECT o.* FROM obf_fts f JOIN obf o ON o.id=f.rowid WHERE obf_fts MATCH ?
                     ORDER BY (o.inci != '') DESC, (o.pays LIKE '%en:france%') DESC, f.rank LIMIT 200"""
            rows = o.execute(sql, (" ".join('"' + m + '"*' for m in mots),)).fetchall()  # tous les mots
            if len(rows) < n and len(mots) > 1:  # sinon : au moins un mot, les plus proches d'abord (rang BM25)
                ids = {r["id"] for r in rows}
                plus = o.execute("""SELECT o.* FROM obf_fts f JOIN obf o ON o.id=f.rowid WHERE obf_fts MATCH ?
                                    ORDER BY f.rank LIMIT 200""", (" OR ".join('"' + m + '"*' for m in mots),)).fetchall()
                rows = list(rows) + sorted([r for r in plus if r["id"] not in ids], key=lambda r: not r["inci"])[:max(0, 3 * n)]
        except sqlite3.OperationalError:
            rows = []
        finally:
            o.close()
        for r in rows:
            if r["ean"] in vus or not r["nom"]:
                continue
            vus.add(r["ean"])
            out.append(fiche(r["ean"], r["nom"], r["marque"], r["inci"], r["categories"], r["image"], r["base"] if r["inci"] else "nom-" + r["base"]))
    return out[:n]


def voisins(ean, n):
    """EAN inconnu : marque devinée par le préfixe GS1 (le plus long de 9 à 6 chiffres partagé par au moins 3 produits)."""
    o, c = obf_db(), scan_db()
    try:
        for L in range(min(9, len(ean) - 1), 5, -1):
            p = ean[:L]
            bornes = (p, p + ":")  # ":" suit "9" : tous les EAN qui commencent par p (index de la colonne ean)
            rows = [dict(r) for r in o.execute("SELECT ean, nom, marque, inci, categories, image, base FROM obf WHERE ean >= ? AND ean < ?", bornes)] if o else []
            rows += [dict(r) | {"image": "", "base": "partage", "categories": r["categorie"]} for r in
                     c.execute("SELECT ean, nom, marque, inci, categorie FROM partages WHERE ean >= ? AND ean < ?", bornes)]
            deja_vu = {r["ean"] for r in rows}
            rows += [dict(r) | {"image": "", "base": "carnet-enrichi"} for r in
                     c.execute("SELECT ean, nom, marque, inci, categories FROM enrichi WHERE ean >= ? AND ean < ?", bornes) if r["ean"] not in deja_vu]
            rows = [r for r in rows if r["ean"] != ean]
            if len(rows) < 3:
                continue
            compte: dict[str, list] = {}
            for r in rows:
                k = plat(r["marque"])
                if k:
                    compte.setdefault(k, []).append(r["marque"])
            if not compte:
                continue
            k, formes = max(compte.items(), key=lambda kv: len(kv[1]))
            marque = max(set(formes), key=formes.count)
            confiance = round(len(formes) / sum(len(v) for v in compte.values()), 2)
            vus, out = set(), []
            def ajoute(r, base):
                if r["ean"] in vus or not r["inci"] or not r["nom"] or r["ean"] == ean:
                    return
                vus.add(r["ean"])
                out.append((abs(int(r["ean"]) - int(ean)), fiche(r["ean"], r["nom"], r["marque"], r["inci"], r["categories"], r["image"], base)))
            for r in rows:
                if plat(r["marque"]) == k:
                    ajoute(r, r["base"])
            res = [f for _, f in sorted(out, key=lambda x: x[0])]
            out, deja = [], len(res)
            if len(res) < n and o:
                for r in o.execute("SELECT ean, nom, marque, inci, categories, image, base FROM obf WHERE inci != '' AND marque LIKE ?", (marque[:3] + "%",)):
                    if plat(r["marque"]) == k:
                        ajoute(dict(r), r["base"])
                res += [f for _, f in sorted(out, key=lambda x: x[0])]
            return {"marque_probable": marque, "prefixe": p, "confiance": confiance, "produits": res[:n]}
        return None
    finally:
        c.close()
        if o:
            o.close()


def top(n):
    c = scan_db()
    out = []
    try:
        for v in c.execute("SELECT ean, n FROM vues WHERE n>=1 ORDER BY n DESC, derniere_date DESC LIMIT 2000").fetchall():
            f, _ = resoudre_local(c, v["ean"])
            if f and f["inci"]:
                out.append({k: f[k] for k in ("ean", "nom", "marque", "inci", "categories", "source")} | {"n": v["n"]})
                if len(out) >= n:
                    break
    finally:
        c.close()
    return out


def sante():
    c = scan_db()
    try:
        np = c.execute("SELECT COUNT(*) FROM partages").fetchone()[0]
        ne = c.execute("SELECT COUNT(*) FROM enrichi").fetchone()[0]
    finally:
        c.close()
    o, nb, date = obf_db(), 0, ""
    if o:
        try:
            nb = o.execute("SELECT COUNT(*) FROM obf").fetchone()[0]
            r = o.execute("SELECT v FROM meta WHERE k='date_import'").fetchone()
            date = r[0] if r else ""
        finally:
            o.close()
    return {"ok": True, "nb_obf": nb, "nb_partages": np, "nb_enrichi": ne, "date_import": date}


def limite(table, cle, regles):
    """regles = [(fenêtre en s, max)]. True si la requête passe."""
    t = time.time()
    with _verrou:
        l = [x for x in table.get(cle, []) if t - x < max(f for f, _ in regles)]
        if any(sum(1 for x in l if t - x < f) >= m for f, m in regles):
            table[cle] = l
            return False
        l.append(t)
        table[cle] = l
        if len(table) > 50000:
            table.clear()
        return True


def propre(s, lmax):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    if len(s) > lmax or re.search(r"[<>]", s):
        raise ValueError
    return s


def partager(d):
    if not isinstance(d, dict) or d.get("consentement") is not True:
        return 400, {"ok": False, "erreur": "consentement"}
    try:
        ean = re.sub(r"\D", "", str(d.get("ean") or ""))
        if not gtin_ok(ean):
            return 400, {"ok": False, "erreur": "ean"}
        nom, marque = propre(d.get("nom"), 120), propre(d.get("marque"), 120)
        inci = propre(d.get("inci"), 4000)
        cat = propre(d.get("categorie"), 40)
        src = d.get("source")
    except ValueError:
        return 400, {"ok": False, "erreur": "texte"}
    if src not in ("ocr", "collage"):
        return 400, {"ok": False, "erreur": "source"}
    if len(inci) < 20 or inci.count(",") < 3:
        return 400, {"ok": False, "erreur": "inci"}
    c = scan_db()
    try:
        c.execute("INSERT INTO partages(ean,nom,marque,inci,categorie,source,date) VALUES(?,?,?,?,?,?,?)",
                  (ean, nom, marque, inci, cat, src, time.strftime("%Y-%m-%d %H:%M:%S")))
        c.commit()
    finally:
        c.close()
    return 201, {"ok": True}


class H(BaseHTTPRequestHandler):
    server_version = "scan"
    sys_version = ""

    def log_message(self, fmt, *args):  # pas d'IP dans les journaux
        pass

    def ip_hash(self):
        ip = (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[0].strip()
        return hashlib.sha256(SEL + ip.encode()).hexdigest()[:20]

    def envoie(self, code, obj, cache=0):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.send_header("Cache-Control", f"public, max-age={cache}" if cache else "no-store")
        o = self.headers.get("Origin")
        if o in ORIGINES:
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Max-Age", "86400")
        self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(b)

    def do_OPTIONS(self):
        self.envoie(204 if self.headers.get("Origin") in ORIGINES else 403, {})

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        try:
            m = re.fullmatch(r"/scan/produit/(\d{8,14})", u.path)
            if m:
                ean = m.group(1)
                if not limite(_lect, self.ip_hash(), [(3600, 300)]):
                    return self.envoie(429, {"status": 0, "erreur": "trop de requêtes"})
                if (q.get("compter") or ["1"])[0] != "0":  # ?compter=0 : appels du build du site, hors popularité
                    compter_vue(ean)
                f = resoudre(ean)
                return self.envoie(200, f, 300) if f else self.envoie(404, {"status": 0})
            m = re.fullmatch(r"/scan/voisins/(\d{8,14})", u.path)
            if m:
                n = max(1, min(24, int((q.get("n") or ["12"])[0] or 12)))
                v = voisins(m.group(1), n)
                return self.envoie(200, v, 300) if v else self.envoie(404, {"status": 0})
            if u.path == "/scan/recherche":
                n = max(1, min(24, int((q.get("n") or ["12"])[0] or 12)))
                return self.envoie(200, {"produits": rechercher((q.get("q") or [""])[0][:120], n)}, 300)
            if u.path == "/scan/top":
                n = max(1, min(200, int((q.get("n") or ["60"])[0] or 60)))
                return self.envoie(200, {"produits": top(n)})
            if u.path == "/scan/sante":
                return self.envoie(200, sante())
            return self.envoie(404, {"status": 0})
        except ValueError:
            return self.envoie(400, {"status": 0})
        except Exception:
            return self.envoie(500, {"status": 0})

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/scan/produit":
            return self.envoie(404, {"ok": False})
        try:
            ln = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            ln = -1
        if ln <= 0 or ln > 8192:
            return self.envoie(413 if ln > 8192 else 400, {"ok": False, "erreur": "taille"})
        try:
            d = json.loads(self.rfile.read(ln).decode("utf-8"))
        except Exception:
            return self.envoie(400, {"ok": False, "erreur": "json"})
        if not isinstance(d, dict) or d.get("consentement") is not True:
            return self.envoie(400, {"ok": False, "erreur": "consentement"})
        if not limite(_debit, self.ip_hash(), [(3600, 10), (86400, 30)]):
            return self.envoie(429, {"ok": False, "erreur": "trop de partages, réessaie plus tard"})
        code, obj = partager(d)
        return self.envoie(code, obj)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["serve"])
    ap.add_argument("--port", type=int, default=8083)
    a = ap.parse_args()
    init()
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
