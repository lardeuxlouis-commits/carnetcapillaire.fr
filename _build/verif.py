#!/usr/bin/env python3
"""Contrôles : 1 H1, title < 60, description, canonical, JSON-LD valide, liens internes, tirets, mots interdits."""
import os, re, json, glob, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, "site")
pages = {("/" + os.path.relpath(os.path.dirname(f), OUT) + "/").replace("/./", "/"): f for f in glob.glob(OUT + "/**/index.html", recursive=True)}
INTERDITS = re.compile(r"\b(guérit|guérir|soigne(?!nt pas| pas)|stoppe la chute|fait repousser|garanti)\b", re.I)
pb = 0
for p, f in sorted(pages.items()):
    h = open(f, encoding="utf-8").read()
    t = html.unescape(re.search(r"<title>(.*?)</title>", h).group(1))
    d = re.search(r'<meta name="description" content="([^"]*)"', h)
    n1 = len(re.findall(r"<h1[ >]", h))
    for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h): json.loads(s)
    txt = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", h, flags=re.S)
    vis = html.unescape(re.sub(r"<[^>]+>", " ", txt))
    main = re.search(r"<main.*?</main>", txt, re.S).group(0)
    mots = len(html.unescape(re.sub(r"<[^>]+>", " ", main)).split())
    err = []
    if n1 != 1: err.append(f"{n1} h1")
    if len(t) >= 60: err.append(f"title {len(t)}")
    if not d or not (110 <= len(html.unescape(d.group(1))) <= 160): err.append("description")
    if '<link rel="canonical"' not in h and '<meta name="robots" content="noindex">' not in h: err.append("canonical")
    if re.search("[—–]", vis): err.append("tiret long")
    m = INTERDITS.findall(vis)
    if m: err.append(f"mots {set(m)}")
    for href in re.findall(r'href="(/[^"#?]*)', h):
        if href.endswith("/") and href not in pages: err.append(f"lien cassé {href}")
        elif not href.endswith("/") and not os.path.exists(OUT + href): err.append(f"fichier {href}")
    pb += bool(err)
    print(f"{p:42} {len(t):2} car. {mots:5} mots  {'OK' if not err else ' | '.join(sorted(set(err)))}")
print(len(pages), "pages,", pb, "avec problème")

# --- Contrôle SEO global : mot-clé unique, JSON-LD par type, canonical, sitemap, robots, maillage, orphelines ---
DOMAIN = "https://carnetcapillaire.fr"
ATTENDU = {"/": {"WebSite"}, "/quiz-type-de-cheveux/": {"WebApplication", "FAQPage", "BreadcrumbList"},
           "/tests-cheveux/": {"ItemList", "BreadcrumbList"}, "/contact/": {"BreadcrumbList"}, "/mentions-legales/": {"BreadcrumbList"},
           "/guide-produits-cheveux-pdf/": {"Product", "BreadcrumbList", "FAQPage"}}
SIMUL = {"/meilleur-shampoing/", "/cuir-chevelu-qui-gratte/", "/soins-cheveux/"}
kws, entrants, seo_pb = {}, {p: set() for p in pages}, 0
for p, f in pages.items():
    h = open(f, encoding="utf-8").read()
    if '<meta name="robots" content="noindex">' in h:  # /merci/, /bienvenue/ : hors sitemap, sans mot-clé, jamais liées
        entrants.pop(p, None); continue
    kw = re.search(r"<!-- Mot-clé cible : (.*?) \|", h)
    k = html.unescape(kw.group(1)).split(" (")[0].split(" / ")[0].split(" + ")[0].strip().lower() if kw else None
    types = {json.loads(s).get("@type") for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h)}
    att = ATTENDU.get(p, {"Article", "BreadcrumbList"}) | ({"WebApplication"} if p in SIMUL else set())
    err = []
    if not k: err.append("mot-clé absent")
    elif k in kws: err.append(f"mot-clé en double avec {kws[k]}")
    else: kws[k] = p
    if not att <= types: err.append(f"JSON-LD manquant {att - types}")
    if f'<link rel="canonical" href="{DOMAIN}{p}">' not in h: err.append("canonical faux")
    main = re.search(r"<main.*?</main>", h, re.S).group(0)
    for href in set(re.findall(r'href="(/[^"#?]*/)"', main)):
        if href != p and href in entrants: entrants[href].add(p)
    if err: seo_pb += 1; print("SEO", p, " | ".join(err))
sm = open(OUT + "/sitemap.xml").read()
manque = [p for p in entrants if f"<loc>{DOMAIN}{p}</loc>" not in sm]
if manque: seo_pb += 1; print("SEO sitemap incomplet", manque)
rb = open(OUT + "/robots.txt").read()
if "GPTBot" not in rb or "ClaudeBot" not in rb or f"Sitemap: {DOMAIN}/sitemap.xml" not in rb: seo_pb += 1; print("SEO robots.txt incomplet")
orph = [p for p, s in entrants.items() if not s and p not in ("/", "/mentions-legales/", "/contact/")]
if orph: seo_pb += 1; print("SEO pages sans lien entrant dans le contenu", orph)
print(f"SEO : {len(kws)} mots-clés uniques, sitemap {len(entrants) - len(manque)}/{len(entrants)} (hors noindex), robots IA ok, "
      f"liens entrants contextuels min {min(len(s) for p, s in entrants.items() if p != '/')}, {seo_pb} problème(s)")

# --- Guides PDF par type : noindex hors sitemap, canonical vers le sélecteur, branchements, prix, sources des PDF ---
OF = json.load(open(os.path.join(ROOT, "_build", "offres.json"), encoding="utf-8"))
PT, PP = f"{OF['prix_type']} {OF['devise']}", f"{OF['prix_pack']} {OF['devise']}"
SEL = "/guide-produits-cheveux-pdf/"
g_pb = []
for p, f in pages.items():
    h = open(f, encoding="utf-8").read()
    if '<meta name="robots" content="noindex">' in h:
        if f"<loc>{DOMAIN}{p}</loc>" in sm: g_pb.append(f"{p} noindex mais dans le sitemap")
        if "<!-- Mot-clé cible" in h: g_pb.append(f"{p} noindex avec un mot-clé cible")
    vis_h = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<!--.*?-->", " ", h, flags=re.S)))
    if re.search(r"\b14 €|14,00 €", vis_h): g_pb.append(f"{p} ancien prix 14 € encore affiché")
sel = open(pages[SEL], encoding="utf-8").read()
LCT = bool(OF.get("lancement"))
if (not LCT and OF["pack"]["stripe"] not in sel) or PP not in sel: g_pb.append("sélecteur : bouton du pack ou prix du pack absent")
for t in OF["types"]:
    gp = f"/guide/{t['slug']}/"
    if gp not in pages: g_pb.append(f"page de vente absente {gp}"); continue
    h = open(pages[gp], encoding="utf-8").read()
    if '<meta name="robots" content="noindex">' not in h: g_pb.append(f"{gp} doit être noindex")
    if '<link rel="canonical"' in h: g_pb.append(f"{gp} : noindex seul attendu, pas de canonical")
    for k in ((PT, "Bientôt disponible") if LCT else (f"#stripe-guide-{t['id']}", "#stripe-pack", PT, PP)):
        if k not in h: g_pb.append(f"{gp} : {k} absent")
    if f'href="{gp}"' not in sel: g_pb.append(f"sélecteur : carte {t['id']} absente")
    tp = open(pages[f"/{t['slug']}/"], encoding="utf-8").read()
    if f'href="{gp}"' not in tp: g_pb.append(f"/{t['slug']}/ : encart vers son guide absent")
js = open(OUT + "/simulateurs.js", encoding="utf-8").read()
if "window.CC_OFFRES=" not in js or PT not in js: g_pb.append("simulateurs.js : offres non injectées")
# Sources des PDF (hors dépôt) : mêmes règles que le site, et 15 à 20 pages par guide
for src in sorted(glob.glob(os.path.join(ROOT, "_guide", "types", "*.md"))) + [os.path.join(ROOT, "_guide", "guide-produits-cheveux.md")]:
    if not os.path.exists(src): continue
    txt = re.sub(r"<!--.*?-->", " ", open(src, encoding="utf-8").read(), flags=re.S)
    if re.search("[—–]", txt): g_pb.append(f"{os.path.basename(src)} : tiret long")
    m = INTERDITS.findall(txt)
    if m: g_pb.append(f"{os.path.basename(src)} : mots {set(m)}")
    pdf = src[:-3] + ".pdf"
    if "/types/" in src and os.path.exists(pdf):
        try:
            import fitz
            n = len(fitz.open(pdf))
            if not 15 <= n <= 20: g_pb.append(f"{os.path.basename(pdf)} : {n} pages (cible 15 à 20)")
        except ImportError:
            pass
# Mode lancement : aucun lien « # » mort en ligne (achat, affiliés factices, réseaux, contact), aucun formulaire e-mail
if LCT:
    for f in glob.glob(OUT + "/**/*.html", recursive=True) + glob.glob(OUT + "/*.js"):
        h = open(f, encoding="utf-8").read()
        for k in ('href="#affilie', 'href="#stripe', 'href="#todo', 'data-capture=', 'class="cap-pop"'):
            if k in h: g_pb.append(f"lancement : {k} dans {os.path.relpath(f, OUT)}")
for x in g_pb: print("GUIDES", x)
print(f"GUIDES : {len(OF['types'])} pages de vente noindex seul, hors sitemap, {'MODE LANCEMENT, ' if LCT else ''}prix {PT} / {PP} depuis offres.json, {len(g_pb)} problème(s)")
import sys
sys.exit(1 if (pb or seo_pb or g_pb) else 0)
