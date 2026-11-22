#!/usr/bin/env python3
"""Données du classement /classement-shampoings/ : compositions (INCI) des shampoings du catalogue + produits les plus scannés.
Lancé par publier.sh AVANT le build (réseau) ; le build ne lit que _build/classement.json (aucun appel réseau au build).
- Catalogue : pour chaque shampoing de simulateurs.js, la fiche la plus ressemblante (même marque, mots du nom) dans la base du carnet
  (copie d'Open Beauty Facts sur le VPS, licence ODbL). On garde la fiche seulement si la ressemblance est suffisante ; sinon le produit
  n'est pas classé (jamais d'INCI inventée). Les choix déjà faits restent en cache ; FIXE permet d'imposer un EAN vérifié à la main.
- Plus scannés : /scan/top (compteur agrégé par code-barres, aucune donnée personnelle)."""
import json, os, re, sys, unicodedata, urllib.request, urllib.parse

B = os.path.dirname(os.path.abspath(__file__))
API = "https://187-124-173-12.sslip.io/scan"
OUT = os.path.join(B, "classement.json")
# id catalogue -> EAN de la fiche Open Beauty Facts retenue après relecture de son nom ET de sa liste INCI (22/11/2026).
# Pas d'appariement automatique : il se trompait (shampoing antipelliculaire pris pour le purifiant, pommade pour la crème lavante…).
# Écartés faute de fiche sûre : Argile Extraordinaire purifiant, Klorane (ortie, mangue, avoine, lin, centaurée, galanga), Ducray, Furterer,
# Kérastase, Cattier, La Roche-Posay, Method for Curls, Bouclème, Cantu, OGX, Moroccanoil, Christophe Robin.
FIXE = {"notino-garnier-ultra-doux-avocat-karite": "3600542571951", "amazon-elseve-color-vive-shampooing": "3600522401032",
        "notino-elseve-color-vive-violet": "3600523682751", "notino-elseve-fibralogy-shampoing": "3600522497035",
        "lookfantastic-sheamoisture-coconut-hibiscus": "0764302314325", "amazon-head-shoulders-classic": "8006540687505"}
POP = "https://world.openbeautyfacts.org/api/v2/search?countries_tags=en:france&categories_tags=en:shampoos&sort_by=unique_scans_n&page_size=100&fields=code,product_name,brands,ingredients_text,unique_scans_n"
VIDES = set("de du des la le les l d a au aux et en pour with and the for ml x shampoing shampooing shampoo bain".split())


def get(path):
    req = urllib.request.Request(API + path, headers={"Origin": "https://carnetcapillaire.fr", "User-Agent": "CarnetCapillaire-build/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception as e:
        print("  réseau :", path, e, file=sys.stderr)
        return None


def mots(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    return [w for w in re.findall(r"[a-z0-9]+", s) if len(w) > 1 and w not in VIDES and not re.fullmatch(r"\d+(ml)?", w)]


def ressemblance(a, b):
    A, Bm = set(mots(a)), set(mots(b))
    return len(A & Bm) / max(len(A), len(Bm)) if A and Bm else 0


def catalogue():
    js = open(os.path.join(B, "simulateurs.js"), encoding="utf-8").read()
    return [dict(id=m.group(1), c=m.group(2), m=m.group(3), nom=m.group(4)) for m in
            re.finditer(r'\{ id: "([^"]+)", c: "(\w+)", m: "([^"]+)", nom: "([^"]+)"', js)]


def main():
    old = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {"catalogue": {}, "top": []}
    cat = {}
    for p in catalogue():
        if p["id"] not in FIXE:
            continue
        d = get("/produit/" + FIXE[p["id"]] + "?compter=0")
        if d and d.get("inci"):
            cat[p["id"]] = {"ean": d["ean"], "fiche": d["nom"], "marque": d["marque"], "inci": d["inci"], "source": d["source"]}
        elif p["id"] in old["catalogue"]:
            cat[p["id"]] = old["catalogue"][p["id"]]
    # Shampoings les plus scannés en France sur Open Beauty Facts (popularité publique, licence ODbL)
    pop = []
    try:
        req = urllib.request.Request(POP, headers={"User-Agent": "CarnetCapillaire-build/1.0 (lardeuxlouis@gmail.com)"})
        for f in json.load(urllib.request.urlopen(req, timeout=60)).get("products", []):
            if (f.get("ingredients_text") or "").count(",") >= 4 and f.get("product_name"):
                pop.append({"ean": f["code"], "nom": f["product_name"], "marque": (f.get("brands") or "").split(",")[0].strip(), "inci": f["ingredients_text"], "scans": f.get("unique_scans_n") or 0})
    except Exception as e:
        print("  réseau OBF :", e, file=sys.stderr); pop = old.get("populaires", [])
    t = get("/top?n=60")
    top = [x for x in (t or {}).get("produits", []) if x.get("inci")] if t else old.get("top", [])
    json.dump({"_note": "Généré par _build/classement_data.py, ne pas éditer à la main. Données Open Beauty Facts (ODbL) et partages des utilisatrices.",
               "catalogue": cat, "populaires": pop, "top": top}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"classement.json : {len(cat)} shampoings du catalogue, {len(pop)} populaires sur Open Beauty Facts, {len(top)} scannés sur le carnet")


if __name__ == "__main__":
    main()
