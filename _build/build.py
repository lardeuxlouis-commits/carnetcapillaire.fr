#!/usr/bin/env python3
"""Générateur statique de Carnet capillaire, site éditorial (tous les types de cheveux, des raides aux crépus).

contenu/*.json -> site/ (HTML statique, aucun framework).
Lancer : python3 _build/build.py   puis   cd site && python3 -m http.server 8090

En ligne sur https://carnetcapillaire.fr (GitHub Pages, branche gh-pages) : publier avec ./publier.sh
MODE LANCEMENT : "lancement": true dans _build/offres.json (voir la note à côté) ; false = Stripe, Brevo et affiliés réactivés.
"""
import json, glob, os, re, html, shutil, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "_build")
OUT = os.path.join(ROOT, "site")
DOMAIN = "https://carnetcapillaire.fr"
SITE = "Carnet capillaire"
AUTRICE = "Carnet capillaire"  # signature éditoriale discrète (pas de page auteur, choix de Louis le 22/11/2026)
LANCEMENT = "2026-11-22"
# TODO réseaux : comptes Instagram et TikTok de Carnet capillaire, à créer
INSTAGRAM = "#todo-instagram"
TIKTOK = "#todo-tiktok"

E = lambda s: html.escape(str(s or ""), quote=True)
PAGES = {}  # slug -> données JSON (rempli dans main)

# Offres payantes (guides PDF par type + pack) : prix et produits dans _build/offres.json, SEUL endroit (TODO validation Louis)
OFFRES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "offres.json"), encoding="utf-8"))
TYPES_G = {t["id"]: t for t in OFFRES["types"]}
GUIDE_SLUG = {t["slug"]: t["id"] for t in OFFRES["types"]}  # page type -> guide
# MODE LANCEMENT (un seul réglage : "lancement" dans offres.json) : pas d'achat, pas de formulaire e-mail, pas de lien affilié factice
MODE_LANCEMENT = bool(OFFRES.get("lancement"))
BIENTOT = '<span class="bientot" aria-disabled="true">Bientôt disponible</span>'


# Fiches relevées mais qui ne correspondent pas au produit recommandé (bouton masqué en mode lancement)
DIRECTS_EXCLUS = {"loly-perfect-match"}  # l'URL relevée est celle de l'après-shampoing Pink Paradise, pas du shampoing Perfect Match


def urls_directes():
    """id -> URL directe de la fiche produit chez le marchand, relevée dans _affiliation/a-brancher.md (colonne « URL produit »).
    Seulement les vraies fiches : pas les pages de recherche, ni les produits « non vendu ici »."""
    f = os.path.join(ROOT, "_affiliation", "a-brancher.md")
    out = {}
    if not os.path.exists(f):
        return out
    for l in open(f, encoding="utf-8"):
        m = re.match(r"\|\s*`([a-z0-9-]+)`\s*\|[^|]*\|[^|]*\|\s*([^|]*?)\s*\|", l)
        if not m:
            continue
        u = m.group(2).split(" ")[0]
        if re.match(r"https://[^\s()]+$", u) and "recherche" not in m.group(2) and "search" not in u and "/s?k=" not in u:
            out[m.group(1)] = u
    for i in DIRECTS_EXCLUS:
        out.pop(i, None)
    return out


def prix(n):
    return f"{n} {OFFRES['devise']}"


PRIX_TYPE, PRIX_PACK = prix(OFFRES["prix_type"]), prix(OFFRES["prix_pack"])
BUMP = prix(OFFRES["prix_pack"] - OFFRES["prix_type"])  # « Ajoute le pack complet pour 10 € de plus »


def url_guide(tid):
    return f"/guide/{TYPES_G[tid]['slug']}/"


def strip(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", str(s or ""))
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r"\1", s)


def inline(s):
    """Texte : on échappe, puis **gras** et [ancre](slug interne ou https://)."""
    s = E(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

    def lien(m):
        t, cible = m.group(1), m.group(2)
        c = cible.strip("/")
        if c == "" or c in PAGES:
            return f'<a href="{url(c)}">{t}</a>'
        if cible.startswith("https://"):
            return f'<a href="{cible}" rel="noopener" target="_blank">{t}</a>'
        if cible.startswith("#affilie-"):
            return f'<a href="{cible}" rel="sponsored nofollow">{t}</a><!-- TODO affiliation : remplacer {cible} -->'
        return t
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lien, s)


def url(slug):
    return "/" if slug in ("", "accueil") else f"/{slug}/"


def ancre(h2):
    s = strip(h2).lower().translate(str.maketrans("àâäéèêëîïôöùûüç’'", "aaaeeeeiioouuuc  "))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or "section"


# --- Rubriques (navigation, fil d'Ariane, pied de page) -------------------
RUBRIQUES = [
    ("types", "Par type de cheveux", "types-de-cheveux"),
    ("problemes", "Par problème", "problemes-cheveux"),
    ("soins", "Soins et produits", "soins-cheveux"),
]
RUB = {r: (t, hub) for r, t, hub in RUBRIQUES}
RUB["routines"] = ("Routines", "types-de-cheveux")  # les routines sont rangées sous « Par type » dans le menu et le pied de page
FAMILLE = {"types": "types", "routines": "types", "problemes": "problemes", "soins": "soins"}

CSS = open(os.path.join(B, "style.css"), encoding="utf-8").read()
ASSET_V = ""

LOGO_SVG = ('<svg class="mark" viewBox="0 0 48 48" aria-hidden="true"><defs><linearGradient id="ccg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eec0ad"/><stop offset="1" stop-color="#b45f45"/></linearGradient></defs><circle cx="24" cy="24" r="23" fill="url(#ccg)"/><path d="M15.5 9.5C24 8 31.5 12.5 31 19.5c-.4 5.8-7.2 7.4-8.6 11.6-1.2 3.6 1.6 6.4 5.4 6.2-6.6 2.6-11.4-1.4-10.2-6.4 1.3-5.4 9.2-6.4 9.4-11.8.2-4.4-3.6-8-11.5-9.6z" fill="#fff"/><path d="M21 8.6c8.6.4 14.6 5.6 13.4 12.4-.9 5.2-6.8 6.6-7.6 10.4-.6 2.8 1.2 4.6 3.6 4.8" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="1.6" stroke-linecap="round"/></svg>')
LOGO_TXT = '<span>Carnet <b>capillaire</b></span>'

ICO = {
    "insta": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor"/></svg>',
    "tiktok": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 3v11.5a3.5 3.5 0 1 1-3-3.46" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M14 3c.5 3 2.5 5 5.5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
}


def nav_html(actif=None):
    liens = [("types-de-cheveux", "Types", "types"), ("problemes-cheveux", "Problèmes", "problemes"),
             ("soins-cheveux", "Soins", "soins"), ("tests-cheveux", "Tests", "tests"), ("composition-shampoing", "Scanner", "scanner"),
             ("guide-produits-cheveux-pdf", "Guide PDF", "ebook")]
    cur = ' aria-current="page"'
    items = "".join(f'<li><a href="{url(s)}"{cur if actif == k else ""}>{E(t)}</a></li>' for s, t, k in liens)
    return (f'<header class="top"><div class="wrap bar"><a class="logo" href="/" aria-label="{SITE}, accueil">{LOGO_SVG}{LOGO_TXT}</a>'
            f'<details class="menu"><summary aria-label="Ouvrir le menu"><span></span><span></span><span></span></summary>'
            f'<nav aria-label="Menu principal"><ul>{items}</ul></nav></details>'
            f'<nav class="navd" aria-label="Menu principal"><ul>{items}</ul></nav>'
            f'<a class="btn btn-s" href="/tests-cheveux/">Fais le test</a></div></header>')


def social_html(cls="soc"):
    if not INSTAGRAM.startswith("https://") or not TIKTOK.startswith("https://"):
        return ""  # comptes pas encore créés : aucun lien mort en ligne
    return (f'<p class="{cls}"><a href="{INSTAGRAM}" rel="me noopener" aria-label="Carnet capillaire sur Instagram">{ICO["insta"]}<span>Instagram</span></a>'
            f'<a href="{TIKTOK}" rel="me noopener" aria-label="Carnet capillaire sur TikTok">{ICO["tiktok"]}<span>TikTok</span></a></p>')


def footer_html():
    cols = ""
    for r, t, hub in RUBRIQUES:
        liens = "".join(f'<li><a href="{url(s)}">{E(d["court"])}</a></li>' for s, d in sorted(PAGES.items(), key=lambda x: x[1].get("ordre", 50))
                        if FAMILLE.get(d.get("rubrique")) == r and s != hub)
        h = f'<a href="{url(hub)}">{E(t)}</a>' if hub else E(t)
        cols += f'<div><h2>{h}</h2><ul>{liens}</ul></div>'
    return (f'<footer class="foot"><div class="wrap"><div class="fbrand"><a class="logo" href="/">{LOGO_SVG}{LOGO_TXT}</a>'
            f'<p>Le carnet de tous les cheveux, des plus raides aux plus crépus, des plus fins aux plus épais. Des routines simples, des produits choisis avec soin, et zéro promesse miracle.</p>'
            f'{social_html()}</div><div class="fcols">{cols}</div>'
            f'<p class="fnote">Certaines pages contiennent des liens affiliés : si tu achètes via ces liens, le site touche une petite commission, sans surcoût pour toi. '
            f'Les conseils de ce site ne remplacent pas l\'avis d\'un médecin ou d\'un dermatologue.</p>'
            f'<p class="flinks"><a href="/tests-cheveux/">Les tests</a><a href="/guide-produits-cheveux-pdf/">Le guide PDF</a>'
            f'<a href="/contact/">Contact</a><a href="/mentions-legales/">Mentions légales et affiliation</a></p></div></footer>')


def page(title, desc, path, body, schema, actif=None, kw=None, noindex=False, extra_js="", canon=None):
    """canon=False : pas de balise canonical (pages de vente noindex : un seul signal, le noindex)."""
    sans_canon = canon is False
    canon = DOMAIN + (canon or path)
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema)
    kwc = f"<!-- Mot-clé cible : {E(kw[0])} | volume KP France (moyenne 12 mois, relevé 22/11/2026) : {E(kw[1])} -->\n" if kw else ""
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{kwc}<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{robots}{'' if sans_canon else f'<link rel="canonical" href="{canon}">'}
<meta property="og:type" content="{'website' if path == '/' else 'article'}">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}/og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f7f1ea">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Figtree:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css?v={ASSET_V}">
{ld}
<script src="/site.js?v={ASSET_V}" defer></script>{extra_js}
<script data-goatcounter="https://carnetcapillaire.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</head>
<body>
<a class="skip" href="#contenu">Aller au contenu</a>
{nav_html(actif)}
<main id="contenu">
{body}
</main>
{footer_html()}
</body>
</html>"""


# --- Blocs de contenu ----------------------------------------------------
AFFILIE_ENCART = ('<aside class="affil" role="note"><p><strong>Transparence :</strong> cette page contient des liens affiliés. Si tu achètes via ces liens, '
                  'le site touche une petite commission, sans surcoût pour toi. Ça ne change pas les sélections. <a href="/mentions-legales/#affiliation">Comment le site gagne de l\'argent</a></p></aside>')

DERMATO = ("Si ça dure plus de quelques semaines, ou en cas de plaques, de rougeurs, de croûtes, de douleur ou de chute importante, "
           "parle-en à ton médecin ou à un dermatologue. Un cosmétique ne soigne pas.")


SCAN_ENCART = ('<a class="scan-encart" href="/composition-shampoing/"><span class="ico"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
               '<path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2M7 8v8M10 8v8M13 8v8M16.5 8v8"/></svg></span>'
               '<span><b>Scanne ton shampoing actuel</b><span>Code-barres, nom ou photo de l\'étiquette : vois en 30 secondes si sa composition va à tes cheveux. →</span></span></a>')


def cta_quiz(titre=None):
    return ('<aside class="cta-quiz"><div class="arch-deco" aria-hidden="true"></div><div><p class="ctat">'
            + E(titre or "Pas sûre de ton type de cheveux ?") +
            '</p><p>Réponds à 9 questions et repars avec ta texture, ton épaisseur, ton cuir chevelu, ta porosité et une routine en 4 étapes. Gratuit, 2 minutes, rien n\'est enregistré.</p></div>'
            '<a class="btn" href="/quiz-type-de-cheveux/">Faire le quiz</a></aside>')


def cta_ebook(titre=None):
    return ('<aside class="suis ebook-cta"><div><p class="ctat">' + E(titre or "Le guide PDF de ton type de cheveux") + '</p>'
            f'<p>Un guide par type de cheveux : ta routine semaine par semaine et 3 produits par budget, sources citées. {PRIX_TYPE} le guide, {PRIX_PACK} le pack tous types.</p></div>'
            + (f'<div>{BIENTOT}<p class="small"><a href="/guide-produits-cheveux-pdf/">Découvrir les guides</a></p></div></aside>' if MODE_LANCEMENT else
               '<a class="btn" href="/guide-produits-cheveux-pdf/">Choisir mon guide</a></aside>'))


GUIDE_ROUTINES = {"routine-cheveux-boucles": "boucles", "routine-cheveux-crepus": "crepus"}


def cta_guide_type(tid):
    """Encart des pages type (et routines) : LE guide du type, puis le pack."""
    t = TYPES_G[tid]
    return (f'<aside class="suis ebook-cta guide-type"><div><p class="kicker">Guide PDF · {PRIX_TYPE}</p><p class="ctat">Ton guide cheveux {E(t["nom"])}</p>'
            f'<p>{E(t["accroche"])} Ta routine semaine par semaine, 3 produits par budget, les erreurs à éviter et les problèmes des cheveux {E(t["nom"])}.</p>'
            f'<p class="small">Ou <a href="/guide-produits-cheveux-pdf/#pack">le pack complet tous types</a>, {PRIX_PACK}.</p></div>'
            + (f'<div>{BIENTOT}<p class="small"><a href="{url_guide(tid)}">Ce que contient le guide</a></p></div></aside>' if MODE_LANCEMENT else
               f'<a class="btn" href="{url_guide(tid)}">Voir mon guide, {PRIX_TYPE}</a></aside>'))


SIMS = {"shampoing": ("Quel shampoing est fait pour toi ?", "6 questions, 3 produits adaptés, rien n'est enregistré."),
        "cuir": ("Diagnostic cuir chevelu", "6 questions pour y voir clair : gras, sec, pellicules, démangeaisons, et quand consulter."),
        "routine": ("Simulateur de routine et de budget", "Ta routine type et ce qu'elle te coûte vraiment par mois.")}


def sim_html(cle):
    t, s = SIMS[cle]
    return (f'<section class="sim-wrap" id="simulateur" aria-labelledby="sim-t"><p class="kicker">Le test</p><h2 id="sim-t">{E(t)}</h2><p class="sim-sous">{E(s)}</p>'
            f'<div class="quiz sim" data-sim="{cle}"><noscript><p>Ce test a besoin de JavaScript.</p></noscript></div>'
            '<p class="small" style="margin-top:10px">Tes réponses restent dans ton navigateur : rien n\'est envoyé, sauf si tu choisis de recevoir ton résultat par e-mail à la fin.</p></section>')


# Photos générées par IA (droits OK, Louis 22/11/2026), jamais présentées comme Clara ni comme des clientes.
# Source HD : ~/videos-idees/public/clara/site/*.jpg ; versions 480/900 dans _assets/ (format 3:4).
PHOTOS = {"cheveux-raides": ("type-raides", "Femme aux cheveux raides et lisses, vue de profil"),
          "cheveux-ondules": ("type-ondules", "Femme aux cheveux ondulés mi-longs"),
          "cheveux-boucles": ("type-boucles", "Femme aux cheveux bouclés en spirales"),
          "cheveux-crepus": ("type-crepus", "Femme aux cheveux crépus portés au naturel"),
          "cheveux-fins": ("type-fins", "Femme aux cheveux fins et raides, châtain clair"),
          "cheveux-frises": ("type-frises", "Femme aux cheveux frisés en petites spirales"),
          "problemes-cheveux": ("probleme", "Femme qui observe les pointes de ses longueurs")}


def img(nom, alt, sizes="(min-width:900px) 340px, 92vw", lazy=True, cls=""):
    return (f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="/images/{nom}-480.webp" srcset="/images/{nom}-480.webp 480w, /images/{nom}-900.webp 900w" '
            f'sizes="{sizes}" width="900" height="1200" {"loading=" + chr(34) + "lazy" + chr(34) + " " if lazy else "fetchpriority=" + chr(34) + "high" + chr(34) + " "}decoding="async" alt="{E(alt)}">')


PAGE_SLUG = ""
PHOTO_REUSE = {"masque-cheveux": "routine", "meilleur-shampoing-sans-sulfate": "routine", "shampoing-apres-lissage-bresilien": "routine"}


def photo_page(alt, legende=""):
    # Photo d'illustration générée par IA (droits OK) : _assets/<slug>-photo-480/900.webp, sinon rien (pas d'emplacement vide en ligne)
    if PAGE_SLUG not in PHOTOS:
        return ""
    nom = f"{PAGE_SLUG}-photo" if os.path.exists(os.path.join(ROOT, "_assets", f"{PAGE_SLUG}-photo-900.webp")) else PHOTO_REUSE.get(PAGE_SLUG)
    if not nom:
        return ""
    return (f'<figure class="ph-ok">{img(nom, alt, sizes="(min-width:900px) 720px, 92vw")}'
            + (f'<figcaption>{inline(legende)}</figcaption>' if legende else "") + '</figure>')


def photo_ph(alt, legende=""):
    # TODO photo : emplacement réservé à une photo (format conseillé 4:5, WebP < 120 ko)
    return (f'<figure class="ph"><div class="ph-box" role="img" aria-label="{E(alt)}"><span>Photo à venir</span></div>'
            + (f'<figcaption>{inline(legende)}</figcaption>' if legende else "") + '</figure><!-- TODO photo : ' + E(alt) + ' -->')


def bloc_html(b):
    t = b.get("type")
    if t == "p":
        return f"<p>{inline(b.get('texte'))}</p>"
    if t == "h3":
        return f"<h3>{inline(b.get('texte'))}</h3>"
    if t == "liste":
        return "<ul>" + "".join(f"<li>{inline(i)}</li>" for i in b.get("items", [])) + "</ul>"
    if t == "etapes":
        return '<ol class="etapes">' + "".join(f"<li>{inline(i)}</li>" for i in b.get("items", [])) + "</ol>"
    if t == "tableau":
        th = "".join(f'<th scope="col">{inline(h)}</th>' for h in b.get("entetes", []))
        rows = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in b.get("lignes", []))
        cap = f'<caption>{inline(b["legende"])}</caption>' if b.get("legende") else ""
        return f'<div class="tw"><table>{cap}<thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'
    if t == "astuce":
        return (f'<aside class="astuce"><p class="lab">{E(b.get("titre") or "Le conseil du carnet")}</p><p>{inline(b.get("texte"))}</p></aside>'
                '<!-- TODO : relire cette astuce écrite à la première personne -->')
    if t == "attention":
        return f'<aside class="attention" role="note"><p class="lab">{E(b.get("titre") or "À savoir")}</p><p>{inline(b.get("texte") or DERMATO)}</p></aside>'
    if t == "dermato":
        return f'<aside class="attention" role="note"><p class="lab">Quand consulter</p><p>{inline(b.get("texte") or DERMATO)}</p></aside>'
    if t == "photo":
        return photo_page(b.get("alt", "Photo d'illustration"), b.get("legende", ""))
    if t == "video" and not b.get("url"):
        return ""  # vidéo de Clara pas encore tournée : rien en ligne (TODO : ajouter "url" TikTok/Reel dans le JSON)
    if t == "video":
        # TODO vidéo : intégrer la vidéo TikTok/Reel (lite embed, chargée au clic)
        return (f'<figure class="vid"><div class="vid-box"><span class="play" aria-hidden="true"></span><p>{E(b.get("titre", "Vidéo"))}</p>'
                f'<p class="small">Vidéo à venir</p></div></figure><!-- TODO vidéo : {E(b.get("titre", ""))} -->')
    if t == "cta_quiz":
        return cta_quiz(b.get("titre"))
    if t == "produits":
        cards = ""
        for i, p in enumerate(b.get("items", []), 1):
            liens = "".join(
                f'<a class="mlink" href="#affilie-{E(l["id"])}" rel="sponsored nofollow">{E(l["marchand"])}</a><!-- TODO affiliation : lien {E(l["marchand"])} pour {E(p["nom"])} -->'
                for l in p.get("liens", []))
            pts = "".join(f"<li>{inline(x)}</li>" for x in p.get("points", []))
            cards += (f'<article class="prod"><p class="rank">{i:02d}</p><div class="prod-b"><p class="marque">{E(p.get("marque"))}</p>'
                      f'<h3>{E(p["nom"])}</h3><p class="pourqui"><strong>Pour qui :</strong> {inline(p.get("pourqui"))}</p>'
                      f'<ul class="pts">{pts}</ul>'
                      + (f'<p class="lim"><strong>À savoir :</strong> {inline(p["limites"])}</p>' if p.get("limites") else "")
                      + f'<div class="prod-f"><span class="prix" title="Gamme de prix indicative">{E(p.get("prix", ""))}</span><span class="ml">{liens}</span></div>'
                      f'<p class="todo-test">Sélection sur la composition : test en conditions réelles et photo à ajouter avant publication.</p></div></article>'
                      f'<!-- TODO : tester {E(p["nom"])}, vérifier la liste INCI et le prix en boutique, ajouter photo datée -->')
        return f'<div class="prods">{cards}</div>' + comparatif(b.get("items", []))
    return ""


PRIX_TXT = {"€": "moins de 8 € env.", "€€": "8 à 18 € env.", "€€€": "plus de 18 € env."}
MARCHANDS = {"notino": "Notino", "lookfantastic": "Lookfantastic", "amazon": "Amazon", "sephora": "Sephora", "nocibe": "Nocibé", "loly": "Les Secrets de Loly"}


def comparatif(items):
    """Tableau comparatif d'une sélection : produit, pour qui, prix indicatif à vérifier, bouton « Voir le prix » (1er lien affilié)."""
    rows = ""
    for p in items:
        l = (p.get("liens") or [{}])[0]
        if not l.get("id"):
            continue
        m = MARCHANDS.get(l["id"].split("-")[0], l.get("marchand", ""))
        rows += (f'<tr><th scope="row" data-l="Produit"><span class="marque">{E(p.get("marque"))}</span>{E(p["nom"])}</th>'
                 f'<td data-l="Pour qui">{inline(p.get("pourqui"))}</td>'
                 f'<td data-l="Prix"><span class="prix">{E(p.get("prix", ""))}</span> {E(PRIX_TXT.get(p.get("prix"), ""))}<small>à vérifier</small></td>'
                 f'<td><a class="mlink" href="#affilie-{E(l["id"])}" rel="sponsored nofollow" target="_blank">Voir le prix<span class="sr"> de {E(p["nom"])} chez {E(m)}</span></a></td></tr>')
    if not rows:
        return ""
    return ('<div class="tw cmp-w"><table class="cmp"><caption>Le comparatif en un coup d\'œil</caption><thead><tr><th scope="col">Produit</th><th scope="col">Pour qui</th>'
            '<th scope="col">Prix indicatif</th><th scope="col"><span class="sr">Lien</span></th></tr></thead><tbody>' + rows + '</tbody></table></div>'
            '<p class="small">Prix indicatifs relevés en novembre 2026, à vérifier sur la boutique. Liens affiliés, sans surcoût pour toi.</p>')


# --- Chiffres réels du site (calculés au build, jamais saisis à la main) et saison -----------
def catalogue():
    """Catalogue des simulateurs, relu dans simulateurs.js : (id, marque, nom, w, guide, tags)."""
    js = open(os.path.join(B, "simulateurs.js"), encoding="utf-8").read()
    out = []
    for m in re.finditer(r'\{ id: "([^"]+)", c: "(\w+)", m: "([^"]+)", nom: "([^"]+)", p: (\d)(?:, n: 1)?, t: \[([^\]]*)\], w: "([^"]+)", g: "([^"]+)" \}', js):
        out.append({"id": m.group(1), "c": m.group(2), "m": m.group(3), "nom": m.group(4), "p": int(m.group(5)),
                    "t": re.findall(r'"(\w+)"', m.group(6)), "w": m.group(7), "g": m.group(8)})
    return out


def chiffres():
    noms, srcs = set(), set()
    # Dédoublonnage : un même produit est parfois nommé un peu différemment d'une page à l'autre
    STOP = {"shampoing", "shampooing", "masque", "soin", "au", "a", "la", "le", "l", "de", "d", "du", "des", "et", "for", "extra", "doux", "bain",
            "fructis", "elseve", "ultra", "cuir", "chevelu", "gras", "cheveux", "secs", "bio", "nutrition", "seboreducteur", "en", "3", "1", "apres"}
    def norm(marque, nom):
        f = lambda t: t.lower().translate(str.maketrans("àâäéèêëîïôöùûüç", "aaaeeeeiioouuuc"))
        g = re.findall(r"[a-z0-9]+", f(marque))
        g = "loreal" if g[:2] == ["l", "oreal"] or g[0] == "elseve" else g[0]
        return g + "|" + " ".join([t for t in re.findall(r"[a-z0-9]+", f(nom)) if t not in STOP][:3])
    for d in PAGES.values():
        for x in d.get("sources", []):
            if str(x.get("url", "")).startswith("https://"): srcs.add(x["url"])
        for sec in d.get("sections", []):
            for b in sec.get("blocs", []):
                if b.get("type") == "produits":
                    noms.update(norm(p.get("marque", ""), p["nom"]) for p in b.get("items", []))
    noms.update(norm(x["m"], x["nom"]) for x in catalogue())
    guides = sum(1 for d in PAGES.values() if d.get("gabarit") == "article")
    return {"produits": len(noms), "guides": guides, "sources": len(srcs), "maj": dt.date.today()}


MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
SAISONS = {  # mois -> (saison, accroche, liens [(slug, ancre)], étiquettes produits de la sélection du mois)
    "hiver": ([12, 1, 2], "cheveux secs, électriques et cuir chevelu qui tiraille", [("cheveux-secs", "Cheveux secs"), ("cuir-chevelu-qui-gratte", "Cuir chevelu qui tiraille")], ["sec", "sensible", "epais"]),
    "printemps": ([3, 4, 5], "on allège la routine et on fait le point sur la chute", [("chute-de-cheveux-femme", "Chute : ce qui est normal"), ("cheveux-fins", "Cheveux fins")], ["fins", "equilibre", "gras"]),
    "été": ([6, 7, 8], "soleil, sel et chlore : on protège les longueurs", [("cheveux-abimes", "Cheveux abîmés"), ("masque-cheveux", "Le bon masque")], ["abimes", "sec", "couleur"]),
    "automne": ([9, 10, 11], "chauffage qui dessèche et cheveux sur la brosse", [("chute-de-cheveux-femme", "Chute d'automne : ce qui est normal"), ("cheveux-secs", "Cheveux secs")], ["sec", "abimes", "sensible"]),
}


def saison(jour=None):
    jour = jour or dt.date.today()
    for nom, (mois, acc, liens, tags) in SAISONS.items():
        if jour.month in mois:
            return nom, acc, liens, tags


def selection_mois(jour=None):
    """3 produits du catalogue qui changent chaque mois au build : étiquettes de la saison, rotation selon le mois."""
    jour = jour or dt.date.today()
    nom, acc, liens, tags = saison(jour)
    cat = catalogue()
    choix = []
    for i, c in enumerate(["shampoing", "masque", "soin"]):
        cands = [x for x in cat if x["c"] == c and set(x["t"]) & set(tags)] or [x for x in cat if x["c"] == c]
        choix.append(cands[(jour.month + i) % len(cands)])
    rows = comparatif([{"marque": x["m"], "nom": x["nom"], "pourqui": x["w"][0].upper() + x["w"][1:], "prix": "€" * x["p"], "liens": [{"id": x["id"]}]} for x in choix])
    return (f'<section class="selmois" aria-labelledby="selmois"><h2 id="selmois">La sélection de {MOIS[jour.month - 1]}</h2>'
            f'<p>Trois produits mis en avant ce mois-ci, choisis pour la saison ({E(acc)}). Elle change chaque mois.</p>{rows}</section>')


def schema_crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": DOMAIN + u} for i, (n, u) in enumerate(items, 1)]}


AUTEUR = {"@type": "Organization", "name": SITE, "url": DOMAIN + "/"}
EDITEUR = {"@type": "Organization", "name": SITE, "url": DOMAIN + "/", "logo": {"@type": "ImageObject", "url": DOMAIN + "/favicon.svg"}}


def crumbs_for(d):
    items = [("Accueil", "/")]
    par = d.get("parent")
    if par and par in PAGES:
        items.append((PAGES[par]["court"], url(par)))
    items.append((d["court"], url(d["slug"])))
    return items


def crumbs_html(items):
    out = []
    for i, (n, u) in enumerate(items):
        out.append(f'<span aria-current="page">{E(n)}</span>' if i == len(items) - 1 else f'<a href="{u}">{E(n)}</a>')
    return '<nav class="crumbs" aria-label="Fil d\'Ariane">' + ' <span aria-hidden="true">›</span> '.join(out) + "</nav>"


def article(d):
    global PAGE_SLUG
    slug = d["slug"]
    PAGE_SLUG = slug
    path = url(slug)
    maj = d.get("maj") or LANCEMENT
    date_txt = dt.date.fromisoformat(maj).strftime("%d/%m/%Y")
    secs = d.get("sections", [])
    ids = []
    for s in secs:
        a = ancre(s["h2"]); n = 2
        while a in ids:
            a = f"{ancre(s['h2'])}-{n}"; n += 1
        ids.append(a)
    toc = "".join(f'<li><a href="#{a}">{E(strip(s["h2"]))}</a></li>' for s, a in zip(secs, ids))
    corps = "".join(f'<section aria-labelledby="{a}"><h2 id="{a}">{E(strip(s["h2"]))}</h2>' + "".join(bloc_html(b) for b in s.get("blocs", [])) + "</section>"
                    for s, a in zip(secs, ids))
    if "cta_quiz" not in json.dumps(secs) and slug != "quiz-type-de-cheveux":
        fins = [m.end() for m in re.finditer("</section>", corps)]
        if len(fins) >= 3:
            corps = corps[:fins[1]] + cta_quiz() + corps[fins[1]:]
    if '<div class="prods">' in corps:
        i = corps.find("</section>", corps.find('<div class="prods">'))
        if i > 0:
            corps = corps[:i] + SCAN_ENCART + corps[i:]
    if d.get("hub"):
        enfants = sorted([(s2, x) for s2, x in PAGES.items() if x.get("parent") == slug], key=lambda x: x[1].get("ordre", 50))
        cartes = "".join(f'<a class="lcard" href="{url(s2)}"><span class="k">{E(RUB.get(x.get("rubrique"), ("",))[0])}</span><h3>{E(x["court"])}</h3>'
                         f'<p>{E(x.get("accroche") or x.get("description", ""))}</p><span class="go">Lire le guide →</span></a>' for s2, x in enfants)
        corps = (f'<section aria-labelledby="pages-hub"><h2 id="pages-hub">{E(d.get("hub_titre") or "Tous les guides")}</h2><div class="hubgrid">{cartes}</div></section>' + corps)
        ids.insert(0, "pages-hub"); secs = [{"h2": d.get("hub_titre") or "Tous les guides"}] + secs
        toc = f'<li><a href="#pages-hub">{E(d.get("hub_titre") or "Tous les guides")}</a></li>' + toc
    if slug == "soins-cheveux":
        corps = selection_mois() + corps
        ids.insert(0, "selmois"); toc = f'<li><a href="#selmois">La sélection de {MOIS[dt.date.today().month - 1]}</a></li>' + toc
    bref = "".join(f"<li>{inline(x)}</li>" for x in d.get("en_bref", []))
    faq = d.get("faq", [])
    faq_html = ('<section aria-labelledby="faq"><h2 id="faq">Questions fréquentes</h2>' +
                "".join(f"<details><summary>{E(strip(f['q']))}</summary><p>{inline(f['r'])}</p></details>" for f in faq) + "</section>") if faq else ""
    # Maillage : liens déclarés, puis parent, enfants et même rubrique
    liens = []
    def add(s2):
        if s2 in PAGES and s2 != slug and s2 not in liens and PAGES[s2].get("rubrique") not in ("legal",):
            liens.append(s2)
    for s2 in d.get("liens_internes", []): add(s2)
    if d.get("parent"): add(d["parent"])
    for s2, x in PAGES.items():
        if x.get("parent") == slug: add(s2)
    for s2, x in PAGES.items():
        if len(liens) >= 6: break
        if x.get("rubrique") == d.get("rubrique"): add(s2)
    lire = "".join(f'<li><a href="{url(s2)}"><span class="k">{E(RUB.get(PAGES[s2].get("rubrique"), ("",))[0])}</span>{E(PAGES[s2]["court"])}</a></li>' for s2 in liens[:6])
    srcs = [x for x in d.get("sources", []) if str(x.get("url", "")).startswith("https://")]
    sources = "".join(f'<li><a href="{E(x["url"])}" rel="noopener" target="_blank">{E(x.get("titre") or x["url"])}</a></li>' for x in srcs)
    crumbs = crumbs_for(d)
    affil = AFFILIE_ENCART if d.get("affilie") else ""
    dermato = f'<aside class="attention" role="note"><p class="lab">Quand consulter</p><p>{inline(DERMATO)}</p></aside>' if d.get("dermato") else ""
    if slug in PHOTOS:
        hero_ph = f'<figure class="ph ph-img">{img(*PHOTOS[slug], lazy=True)}</figure>'
    elif os.path.exists(os.path.join(ROOT, "_assets", f"{slug}-photo-900.webp")) or slug in PHOTO_REUSE:
        nom = f"{slug}-photo" if os.path.exists(os.path.join(ROOT, "_assets", f"{slug}-photo-900.webp")) else PHOTO_REUSE[slug]
        hero_ph = f'<figure class="ph ph-img">{img(nom, d.get("photo_alt") or d["court"], lazy=True)}</figure>'
    else:
        hero_ph = ""
    body = f"""<div class="wrap art">
{crumbs_html(crumbs)}
<header class="ahead"><div>
<p class="kicker">{E(RUB.get(d.get("rubrique"), ("Carnet capillaire",))[0])}</p>
<h1>{E(strip(d['h1']))}</h1>
<p class="chapo">{inline(d.get('chapo'))}</p>
<p class="byline"><span class="av" aria-hidden="true">C</span>{SITE}, mis à jour le {date_txt} · {len(srcs)} sources citées</p>
</div>{hero_ph}</header>
{affil}
{sim_html(d["simulateur"]) if d.get("simulateur") else ""}
<div class="cols">
<aside class="side"><div class="bref"><p class="lab">L'essentiel</p><ul>{bref}</ul></div>
<nav class="toc" aria-label="Sommaire"><p class="lab">Sommaire</p><ol>{toc}{'<li><a href="#faq">Questions fréquentes</a></li>' if faq else ''}</ol></nav></aside>
<div class="txt">{corps}{faq_html}{dermato}
{cta_guide_type(GUIDE_SLUG.get(slug) or GUIDE_ROUTINES[slug]) if (slug in GUIDE_SLUG or slug in GUIDE_ROUTINES) else cta_ebook()}
<section class="lire" aria-labelledby="lire"><h2 id="lire">À lire ensuite</h2><ul>{lire}</ul></section>
{f'<section class="sources" aria-labelledby="sources"><h2 id="sources">Sources</h2><ul>{sources}</ul></section>' if sources else ''}
</div></div></div>"""
    schema = [
        {"@context": "https://schema.org", "@type": "Article", "headline": strip(d["h1"])[:110], "description": d.get("description", ""),
         "datePublished": LANCEMENT, "dateModified": maj, "inLanguage": "fr-FR", "author": AUTEUR, "publisher": EDITEUR,
         "image": DOMAIN + "/og.png", "mainEntityOfPage": DOMAIN + path, "about": d.get("kw", "")}
        | ({"citation": [x["url"] for x in srcs]} if srcs else {}),
        schema_crumbs(crumbs),
    ]
    if faq:
        schema.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": strip(f["q"]), "acceptedAnswer": {"@type": "Answer", "text": strip(f["r"])}} for f in faq]})
    actif = FAMILLE.get(d.get("rubrique"))
    if slug == "quiz-type-de-cheveux": actif = "quiz"
    js = f'\n<script src="/simulateurs.js?v={ASSET_V}" defer></script>' if d.get("simulateur") else ""
    if d.get("simulateur"):
        schema.append({"@context": "https://schema.org", "@type": "WebApplication", "name": SIMS[d["simulateur"]][0], "url": DOMAIN + path + "#simulateur",
                       "applicationCategory": "LifestyleApplication", "operatingSystem": "Tous navigateurs", "inLanguage": "fr-FR", "isAccessibleForFree": True,
                       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}})
    return path, page(d["title"], d["description"], path, body, schema, actif, (d.get("kw"), d.get("volume")), extra_js=js)


def main():
    global ASSET_V
    import hashlib
    for f in sorted(glob.glob(os.path.join(ROOT, "contenu", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        PAGES[d["slug"]] = d
    # Ordre et accroche courte des cartes de hub (fichier séparé pour ne pas toucher aux contenus)
    for s, (o, acc) in json.load(open(os.path.join(B, "accroches.json"), encoding="utf-8")).items():
        if s in PAGES: PAGES[s].setdefault("ordre", o); PAGES[s].setdefault("accroche", acc)
    js_site = open(os.path.join(B, "site.js"), encoding="utf-8").read()
    js_quiz = open(os.path.join(B, "quiz.js"), encoding="utf-8").read()
    js_sims = open(os.path.join(B, "simulateurs.js"), encoding="utf-8").read()
    js_scan = open(os.path.join(B, "scanner.js"), encoding="utf-8").read()
    ingr = json.dumps(json.load(open(os.path.join(B, "ingredients.json"), encoding="utf-8")), ensure_ascii=False, separators=(",", ":"))
    ASSET_V = hashlib.md5((CSS + js_site + js_quiz + js_sims + js_scan + ingr + json.dumps(OFFRES)).encode()).hexdigest()[:8]
    if os.path.isdir(OUT):
        for x in os.listdir(OUT):
            p = os.path.join(OUT, x)
            if os.path.isdir(p): shutil.rmtree(p)
            elif x != "og.png": os.remove(p)
    os.makedirs(OUT, exist_ok=True)
    out_urls = []

    liens_f = os.path.join(ROOT, "_affiliation", "liens.json")
    LIENS = {k: v for k, v in (json.load(open(liens_f, encoding="utf-8")) if os.path.exists(liens_f) else {}).items() if str(v).startswith("https://")}

    DIRECTS = urls_directes() if MODE_LANCEMENT else {}

    def lien_affilie(m):
        avant, i, apres, texte = m.group(1), m.group(2), m.group(3), m.group(4)
        if i in LIENS:  # lien suivi branché : rel sponsored conservé
            return f'<a {avant}href="{E(LIENS[i])}"{apres}>{texte}</a>'
        if not MODE_LANCEMENT:
            return m.group(0)
        if i in DIRECTS:  # lancement : fiche produit directe, pas de commission, donc pas « sponsored »
            attrs = re.sub(r'\s*(rel|target)="[^"]*"', "", avant + apres).strip()
            return f'<a {attrs + " " if attrs else ""}href="{E(DIRECTS[i])}" rel="nofollow noopener" target="_blank">{texte}</a>'
        return "" if "mlink" in avant + apres else texte  # bouton masqué, ou simple texte dans une phrase

    def brancher(h):
        # liens.json (id -> URL trackée) d'abord ; en mode lancement, URL directe ou rien ; sinon le lien reste #affilie-<id>
        h = re.sub(r'<a ([^>]*?)href="#affilie-([a-z0-9-]+)"([^>]*)>(.*?)</a>(?:<!-- TODO affiliation[^>]*-->)?', lien_affilie, h, flags=re.S)
        return h

    def write(path, h, prio="0.7", sitemap=True):
        h = brancher(h)
        dest = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w", encoding="utf-8").write(h)
        if sitemap: out_urls.append((path, prio))

    import pages_speciales as PS
    PS.init(globals())
    for slug, d in PAGES.items():
        if d.get("gabarit") == "article":
            p, h = article(d)
            write(p, h, "0.9" if d.get("argent") else "0.7")
    for p, h, prio in PS.pages():
        write(p, h, prio, sitemap=prio is not None)

    open(os.path.join(OUT, "style.css"), "w", encoding="utf-8").write(CSS)
    drapeau = "window.CC_LANCEMENT=true;\n" if MODE_LANCEMENT else ""
    open(os.path.join(OUT, "site.js"), "w", encoding="utf-8").write(drapeau + js_site)
    open(os.path.join(OUT, "quiz.js"), "w", encoding="utf-8").write(js_quiz)
    # Scanner de composition : règles (_build/ingredients.json) injectées devant le moteur
    open(os.path.join(OUT, "scanner.js"), "w", encoding="utf-8").write(f"window.CC_INGR={ingr};\n" + js_scan)
    offres_js = {"prix_type": PRIX_TYPE, "prix_pack": PRIX_PACK, "bump": BUMP, "selecteur": "/guide-produits-cheveux-pdf/",
                 "types": {t["id"]: {"nom": t["nom"], "url": url_guide(t["id"]), "accroche": t["accroche"]} for t in OFFRES["types"]}}
    open(os.path.join(OUT, "simulateurs.js"), "w", encoding="utf-8").write(
        f"{drapeau}window.CC_LIENS={json.dumps(LIENS)};\nwindow.CC_DIRECTS={json.dumps(DIRECTS)};\nwindow.CC_OFFRES={json.dumps(offres_js, ensure_ascii=False)};\n" + js_sims)
    # Lecteur de code-barres zxing-cpp (WebAssembly : zxing-wasm sous licence MIT, zxing-cpp sous licence Apache 2.0), auto-hébergé : chargé au clic par scanner.js
    os.makedirs(os.path.join(OUT, "lib"), exist_ok=True)
    for x in glob.glob(os.path.join(B, "vendor", "zxing", "*")):
        shutil.copy(x, os.path.join(OUT, "lib", os.path.basename(x)))
    # Images du site : _assets/*.webp -> site/images/
    os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "images", "logos"), exist_ok=True)
    for lg in glob.glob(os.path.join(ROOT, "_assets", "logos", "*")):
        shutil.copy(lg, os.path.join(OUT, "images", "logos", os.path.basename(lg)))
    for im in [x for x in glob.glob(os.path.join(ROOT, "_assets", "*")) if x.rsplit(".", 1)[-1] in ("webp", "jpg", "webm", "mp4")]:
        shutil.copy(im, os.path.join(OUT, "images", os.path.basename(im)))
    # Mini-guide gratuit (lien de l'e-mail J0 et de /bienvenue/) : copié seulement s'il a été généré en local
    mg = os.path.join(ROOT, "_guide", "mini-guide", "mini-guide-5-erreurs.pdf")
    if os.path.exists(mg):
        os.makedirs(os.path.join(OUT, "telechargements"), exist_ok=True)
        shutil.copy(mg, os.path.join(OUT, "telechargements", "mini-guide-5-erreurs.pdf"))
    # IndexNow : la clé (publique par nature) est servie à la racine, /<clé>.txt
    kf = os.path.join(B, "indexnow.txt")
    if os.path.exists(kf):
        k = open(kf).read().strip()
        open(os.path.join(OUT, f"{k}.txt"), "w").write(k)
    shutil.copy(os.path.join(B, "favicon.svg"), os.path.join(OUT, "favicon.svg")); shutil.copy(os.path.join(B, "og.png"), os.path.join(OUT, "og.png"))
    open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(
        page("Page introuvable | Carnet capillaire", "Cette page n'existe pas.", "/404.html",
             '<div class="wrap prose"><h1>Oups, cette page s\'est emmêlée</h1><p><a href="/">Revenir à l\'accueil</a> ou <a href="/quiz-type-de-cheveux/">faire le quiz</a>.</p></div>',
             [], noindex=True))
    BOTS_IA = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User",
               "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot", "Meta-ExternalAgent", "MistralAI-User", "DuckAssistBot"]
    robots = ("# Robots des moteurs de recherche et des assistants IA : bienvenus (citation des guides avec un lien).\n"
              + "".join(f"User-agent: {b}\nAllow: /\nDisallow: /404.html\n\n" for b in BOTS_IA)
              + "User-agent: *\nContent-Signal: search=yes, ai-input=yes, ai-train=yes\nAllow: /\nDisallow: /404.html\n\n"
              f"Sitemap: {DOMAIN}/sitemap.xml\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(robots)
    sm = "".join(f"<url><loc>{DOMAIN}{p}</loc><lastmod>{LANCEMENT}</lastmod><priority>{pr}</priority></url>" for p, pr in sorted(out_urls, key=lambda x: (x[0] != "/", x[0])))
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    print(f"{len(out_urls)} pages générées dans {OUT}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, B)
    main()

# Bandeau photo (IA, droits OK) sous l'en-tête des pages outils qui n'ont pas d'image
BANDEAUX = {"tests-cheveux": ("bandeau-test", "Femme qui regarde ses cheveux dans le miroir en faisant un test sur son téléphone"),
            "quiz-type-de-cheveux": ("bandeau-test", "Femme qui regarde ses cheveux dans le miroir en faisant un test sur son téléphone"),
            "composition-shampoing": ("bandeau-scanner", "Mains qui scannent le code-barres d'un flacon de shampoing avec un téléphone"),
            "classement-shampoings": ("bandeau-classement", "Flacons de shampoing sans marque alignés sur une étagère"),
            "methode-score": ("bandeau-classement", "Flacons de shampoing sans marque alignés sur une étagère"),
            "soins-cheveux": ("routine", "Flacons de soins sans marque, peigne et serviette posés sur du lin")}


def poser_bandeaux():
    for slug, (nom, alt) in BANDEAUX.items():
        f = os.path.join(OUT, slug, "index.html")
        if not os.path.exists(f):
            continue
        h = open(f, encoding="utf-8").read()
        if "class=\"bandeau\"" in h:
            continue
        fig = (f'<figure class="bandeau"><img src="/images/{nom}-480.webp" srcset="/images/{nom}-480.webp 480w, /images/{nom}-900.webp 900w" '
               f'sizes="(min-width:900px) 900px, 92vw" width="900" height="1200" loading="lazy" decoding="async" alt="{E(alt)}"></figure>')
        i = h.find("</header>", h.find("<h1"))
        if i < 0:
            continue
        h = h[:i + 9] + fig + h[i + 9:]
        open(f, "w", encoding="utf-8").write(h)



if __name__ == "__main__":
    poser_bandeaux()
