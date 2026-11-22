#!/usr/bin/env python3
"""Charge les fiches « carnet-enrichi » (relevées sur les fiches des marques et des distributeurs) dans scan.db, table enrichi.

Entrée : un fichier JSONL (une fiche par ligne : ean, nom, marque, gamme, type, format, inci, categories, url_source, site, date, note).
La table vit dans scan.db (pas dans obf.db) : elle survit à l'import hebdomadaire d'Open Beauty Facts.
Une fiche OBF avec une INCI au moins aussi complète reste prioritaire : l'arbitrage se fait à la lecture (server.resoudre_local),
donc une fiche OBF complétée plus tard reprend automatiquement la main.
Usage (sur le VPS) : runuser -u scanobf -- python3 /opt/scan/charger_enrichi.py fiches.jsonl [--dir /var/lib/scan] [--remplacer]
  --remplacer : vide la table avant chargement (sinon insertion / mise à jour par EAN)
"""
import argparse, json, os, re, sqlite3, sys, unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def plat(s):
    s = unicodedata.normalize("NFD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn").lower()).strip()


def gtin_ok(ean):
    if not re.fullmatch(r"\d{13}", ean):
        return False
    s = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(ean[:12]))
    return (10 - s % 10) % 10 == int(ean[12])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichier"); ap.add_argument("--dir", default=os.environ.get("SCAN_DIR", "/var/lib/scan"))
    ap.add_argument("--remplacer", action="store_true")
    a = ap.parse_args()
    os.environ["SCAN_DIR"] = a.dir
    import server  # crée la table si besoin (même schéma que le service)
    server.DIR, server.DB_SCAN, server.DB_OBF = a.dir, os.path.join(a.dir, "scan.db"), os.path.join(a.dir, "obf.db")
    server.init()
    c = sqlite3.connect(server.DB_SCAN, timeout=30)
    cols = {r[1] for r in c.execute("PRAGMA table_info(enrichi)")}
    if "cherche" not in cols:
        c.execute("ALTER TABLE enrichi ADD COLUMN cherche TEXT")
    if a.remplacer:
        c.execute("DELETE FROM enrichi")
    n = rej = 0
    for l in open(a.fichier, encoding="utf-8"):
        f = json.loads(l)
        ean, inci = str(f.get("ean", "")), (f.get("inci") or "").strip()
        if not gtin_ok(ean) or len(inci) < 40 or not str(f.get("url_source", "")).startswith("https://"):
            rej += 1; continue
        c.execute("""INSERT OR REPLACE INTO enrichi(ean,nom,marque,gamme,type,format,inci,categories,url_source,site,date,note,cherche)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (ean, f.get("nom", "")[:200], f.get("marque", "")[:80], f.get("gamme", "")[:80], f.get("type", ""), f.get("format", "")[:40],
                   inci[:6000], f.get("categories", ""), f["url_source"][:500], f.get("site", "")[:80], f.get("date", ""), f.get("note", "")[:500],
                   plat(" ".join([f.get("marque", ""), f.get("nom", ""), f.get("gamme", "")]))))
        n += 1
    c.commit()
    tot = c.execute("SELECT COUNT(*) FROM enrichi").fetchone()[0]
    c.close()
    print(f"chargées {n}, rejetées {rej}, total table enrichi {tot}")


if __name__ == "__main__":
    main()
