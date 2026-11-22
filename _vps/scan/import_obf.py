#!/usr/bin/env python3
"""Import des dumps CSV Open Beauty Facts (+ Open Products Facts, partie hygiène/beauté) dans /var/lib/scan/obf.db.

Données sous licence ODbL (Open Database License), (c) contributeurs Open Beauty Facts / Open Products Facts :
https://world.openbeautyfacts.org/ ; attribution conservée dans la réponse de l'API (champ "licence").

Construit d'abord /var/lib/scan/obf.db.tmp puis remplace obf.db atomiquement (os.replace) :
le service continue de répondre pendant l'import. Lancé par cron le dimanche à 4 h.
Usage : python3 import_obf.py [--dir /var/lib/scan] [--obf fichier.csv.gz] [--opf fichier.csv.gz]
"""
import argparse, csv, gzip, os, re, sqlite3, sys, time, unicodedata, urllib.request

URLS = {"obf": "https://static.openbeautyfacts.org/data/en.openbeautyfacts.org.products.csv.gz",
        "opf": "https://static.openproductsfacts.org/data/en.openproductsfacts.org.products.csv.gz"}
UA = "CarnetCapillaire-scan/1.0 (https://carnetcapillaire.fr ; lardeuxlouis@gmail.com)"
# Dans Open Products Facts (tout objet), on ne garde que l'hygiène et la beauté
BEAUTE = re.compile(r"beaut|cosmet|hygien|shampo|soap|savon|shower|douche|hair|cheveu|body|skin|cream|creme|deodor|toilet|bath|bain|lotion|soin|care", re.I)


def plat(s):
    s = unicodedata.normalize("NFD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn").lower()).strip()


GROUPES = re.compile(r"^(l.?or[eé]al|l.?oreal consumer|unilever|procter|p&g|henkel|beiersdorf|johnson|colgate|coty|reckitt|sanofi|pierre fabre|naos|"
                     r"edgewell|kao|shiseido|est[eé]e lauder|lvmh|l.?occitane groupe)", re.I)


def marques(r):
    m = (r.get("brands") or r.get("brands_en") or "").strip()
    if not m and r.get("brands_tags"):
        m = ",".join(t.split(":")[-1].replace("-", " ").title() for t in r["brands_tags"].split(","))
    l = [x.strip() for x in m.split(",") if x.strip()]
    return [x.replace("-", " ").title() if re.fullmatch(r"[a-z0-9-]+", x) else x for x in l]  # « garnier-fructis » -> « Garnier Fructis »


def marque_de(r):
    """La marque du flacon plutôt que le groupe : « L'Oréal, Garnier » -> Garnier."""
    l = marques(r)
    propres = [x for x in l if not GROUPES.match(x)]
    return (propres[-1] if propres else (l[0] if l else ""))[:120]


def lignes(chemin):
    csv.field_size_limit(sys.maxsize)
    with gzip.open(chemin, "rt", encoding="utf-8", errors="replace", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            yield r


def telecharge(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="/var/lib/scan")
    ap.add_argument("--obf"); ap.add_argument("--opf")
    a = ap.parse_args()
    fichiers = {}
    for base in ("obf", "opf"):
        f = getattr(a, base)
        if not f:
            f = os.path.join(a.dir, f"dump-{base}.csv.gz")
            telecharge(URLS[base], f)
        fichiers[base] = f
    tmp, final = os.path.join(a.dir, "obf.db.tmp"), os.path.join(a.dir, "obf.db")
    if os.path.exists(tmp):
        os.remove(tmp)
    c = sqlite3.connect(tmp)
    c.executescript("""
      PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;
      CREATE TABLE obf(id INTEGER PRIMARY KEY, ean TEXT UNIQUE, nom TEXT, marque TEXT, inci TEXT, categories TEXT,
                       pays TEXT, image TEXT, maj INTEGER, base TEXT);
      CREATE VIRTUAL TABLE obf_fts USING fts5(texte, content='', tokenize='unicode61 remove_diacritics 2');
      CREATE TABLE meta(k TEXT PRIMARY KEY, v TEXT);
    """)
    stats = {}
    for base in ("obf", "opf"):
        n = ni = nf = 0
        for r in lignes(fichiers[base]):
            ean = re.sub(r"\D", "", r.get("code") or "")
            if not 8 <= len(ean) <= 14:
                continue
            nom = (r.get("product_name") or r.get("generic_name") or "").strip()[:200]
            inci = (r.get("ingredients_text") or "").strip()[:6000]
            cats = (r.get("categories_tags") or "").strip()
            if base == "opf" and not BEAUTE.search(cats + " " + nom):
                continue
            pays = (r.get("countries_tags") or "").strip()
            try:
                maj = int(r.get("last_modified_t") or 0)
            except ValueError:
                maj = 0
            cur = c.execute("INSERT OR IGNORE INTO obf(ean,nom,marque,inci,categories,pays,image,maj,base) VALUES(?,?,?,?,?,?,?,?,?)",
                            (ean, nom, marque_de(r), inci, cats, pays, (r.get("image_small_url") or "")[:300], maj, base))
            if cur.rowcount:
                n += 1; ni += bool(inci); nf += "en:france" in pays
                txt = plat(nom + " " + " ".join(marques(r)))
                if txt:
                    c.execute("INSERT INTO obf_fts(rowid, texte) VALUES(?,?)", (cur.lastrowid, txt))
        stats[base] = (n, ni, nf)
    c.execute("INSERT INTO meta VALUES('date_import', ?)", (time.strftime("%Y-%m-%d %H:%M"),))
    for base, (n, ni, nf) in stats.items():
        c.execute("INSERT INTO meta VALUES(?, ?)", (f"nb_{base}", f"{n}|{ni}|{nf}"))
    c.commit(); c.close()
    os.chmod(tmp, 0o644)
    os.replace(tmp, final)
    for base, (n, ni, nf) in stats.items():
        print(f"{base}: {n} produits, {ni} avec INCI, {nf} vendus en France")


if __name__ == "__main__":
    main()
