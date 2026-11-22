#!/usr/bin/env python3
"""Export des guides PDF payants de Carnet capillaire (prix : _build/offres.json, seul endroit).

1. Le pack complet tous types :
   _guide/guide-produits-cheveux.md  ->  _guide/guide-produits-cheveux.html  ->  _guide/guide-produits-cheveux.pdf
2. Les 6 guides par type de cheveux (raides, fins, ondulés, bouclés, frisés, crépus) :
   _guide/types/guide-cheveux-<type>.md  ->  _guide/types/guide-cheveux-<type>.pdf
   Les sources par type reprennent les chapitres communs du guide complet avec la directive
   « @inclure Chapitre » (chapitre entier) ou « @inclure Chapitre > Section » (une section ## avec son titre ;
   « @inclure- … » pour la reprendre sans sa ligne de titre),
   pour qu'une correction faite dans le guide complet se retrouve partout.
Lancer : python3 _build/guide_pdf.py                 (pack : HTML + PDF)
         python3 _build/guide_pdf.py --apercus       (+ 3 vignettes webp du pack dans _assets/guide-apercu-{1,2,3}.webp)
         python3 _build/guide_pdf.py --types         (les 6 guides par type ; --type boucles pour un seul)
         python3 _build/guide_pdf.py --types --apercus  (+ 2 vignettes par type : _assets/guide-<type>-apercu-{1,2}.webp)
         python3 _build/guide_pdf.py --tout --apercus   (tout)

Sans dépendance de conversion : petit convertisseur Markdown maison (titres, listes, tableaux, gras, italique,
liens, encadrés > [!clara] / [!info] / [!medecin], badge [[verif]]), puis Chrome headless --print-to-pdf.
Deux passes : la 1re mesure la page de chaque chapitre (PyMuPDF), la 2e écrit le sommaire avec les numéros.
Numéros de page tamponnés par PyMuPDF (Chrome ne gère pas les marges @page sans en-têtes natifs).
Le PDF payant ne doit jamais être publié dans un dépôt public : _guide/.gitignore ignore *.pdf et *.html.
"""
import html, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(ROOT, "_guide")
SRC = os.path.join(G, "guide-produits-cheveux.md")
OUT_HTML = os.path.join(G, "guide-produits-cheveux.html")
OUT_PDF = os.path.join(G, "guide-produits-cheveux.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TITRE = "Les meilleurs produits pour ton type de cheveux"
OFFRES = json.load(open(os.path.join(ROOT, "_build", "offres.json"), encoding="utf-8"))
TYPES = {t["id"]: t for t in OFFRES["types"]}
EDITION = "Édition novembre 2026"
VERIF = '<span class="verif">À vérifier par Clara</span>'
ENCADRES = {"clara": ("clara", ""), "info": ("info", ""), "medecin": ("medecin", "")}


def slug(t):
    t = t.lower().translate(str.maketrans("àâäéèêëîïôöùûüç’'", "aaaeeeeiioouuuc  "))
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:50]


def inline(s):
    s = html.escape(s, quote=False)
    s = s.replace("« ", "«\u00a0").replace(" »", "\u00a0»").replace(" :", "\u00a0:").replace(" ;", "\u00a0;").replace(" ?", "\u00a0?").replace(" !", "\u00a0!")
    s = s.replace("[[verif]]", VERIF)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((https://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"(?<![\"'>])(https://[^\s<]+)", lambda m: f'<a class="url" href="{m.group(1)}">{m.group(1)}</a>', s)
    return s


def sections_source(md):
    """Découpe le guide complet : {"Chapitre": texte} et {"Chapitre > Section": texte} (titres compris)."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    res, chap, sec, buf_c, buf_s = {}, None, None, [], []
    def fin_sec():
        if chap and sec: res[f"{chap} > {sec}"] = "\n".join(buf_s).strip()
    for l in md.split("\n") + ["# FIN"]:
        if l.startswith("# "):
            fin_sec()
            if chap: res[chap] = "\n".join(buf_c).strip()
            chap, sec, buf_c, buf_s = l[2:].strip(), None, [l], []
            continue
        if l.startswith("## "):
            fin_sec(); sec, buf_s = l[3:].strip(), [l]
        elif sec:
            buf_s.append(l)
        buf_c.append(l)
    return res


def inclure(md, source):
    """Remplace chaque ligne « @inclure Chapitre [> Section] » par le texte du guide complet."""
    parts = sections_source(source)
    def rep(m):
        cle = m.group(2).strip()
        if cle not in parts:
            raise SystemExit(f"@inclure introuvable dans le guide complet : {cle}")
        txt = parts[cle]
        return txt.split("\n", 1)[1].strip() if m.group(1) else txt  # « @inclure- » : sans la ligne de titre
    return re.sub(r"^@inclure(-?) (.+)$", rep, md, flags=re.M)


def convertir(md):
    """Renvoie (html du corps, liste des chapitres [(id, titre)])."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    lignes = md.split("\n")
    out, chap, i, n_chap = [], [], 0, 0
    para = []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lignes):
        l = lignes[i].rstrip()
        if not l.strip():
            flush(); i += 1; continue
        m = re.match(r"^(#{1,3}) (.+)$", l)
        if m:
            flush()
            niv, t = len(m.group(1)), m.group(2).strip()
            if niv == 1:
                n_chap += 1
                suite = t.endswith(" {suite}")  # « # Titre {suite} » : chapitre sans saut de page (chapitres courts)
                t = t.replace(" {suite}", "")
                cid = slug(t)
                chap.append((cid, t))
                if len(chap) > 1:
                    out.append("</section>")
                num = f'<span class="num">{n_chap:02d}</span>' if t not in ("Sources", "Mentions") else ""
                out.append(f'<section class="chap{" suite" if suite else ""}" id="{cid}"><h1 data-chap="{html.escape(t)}">{num}{inline(t)}</h1>')
            else:
                out.append(f"<h{niv}>{inline(t)}</h{niv}>")
            i += 1; continue
        if l.startswith("|"):
            flush()
            rows = []
            while i < len(lignes) and lignes[i].startswith("|"):
                rows.append([c.strip() for c in lignes[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r":?-+:?", c) for c in r)]
            t = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table>"
            out.append(t); continue
        if l.startswith(">"):
            flush()
            bloc = []
            while i < len(lignes) and lignes[i].startswith(">"):
                bloc.append(lignes[i][1:].strip()); i += 1
            kind = "info"
            m2 = re.match(r"^\[!(\w+)\]$", bloc[0]) if bloc else None
            if m2:
                kind = m2.group(1); bloc = bloc[1:]
            out.append(f'<aside class="box {ENCADRES.get(kind, ("info",))[0]}"><p>' + inline(" ".join(bloc)) + "</p></aside>")
            continue
        if re.match(r"^(- |\d+\. )", l):
            flush()
            ordonnee = bool(re.match(r"^\d+\. ", l))
            items = []
            while i < len(lignes) and re.match(r"^(- |\d+\. )", lignes[i]):
                txt = re.sub(r"^(- |\d+\. )", "", lignes[i].rstrip()); i += 1
                while i < len(lignes) and lignes[i].startswith("  ") and lignes[i].strip():
                    txt += " " + lignes[i].strip(); i += 1
                items.append(txt)
            tag = "ol" if ordonnee else "ul"
            cls = ' class="prods"' if any("[[verif]]" in x for x in items) and not ordonnee else ""
            out.append(f"<{tag}{cls}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        para.append(l.strip()); i += 1
    flush()
    if chap:
        out.append("</section>")
    return "\n".join(out), chap


CSS = """
@page{size:A4;margin:17mm 17mm 20mm}
@page:first{margin:0}
:root{--cream:#f7f1ea;--card:#fffdfa;--rose:#e8c4b8;--rose-l:#f6e4dc;--terra:#c47a5a;--terra-d:#9a5236;--brun:#2e211b;--mut:#6b5a50;--sauge-d:#4f5e47;--sauge-l:#eef1ea;--line:#eadfd3;
--serif:Fraunces,Georgia,serif;--sans:Figtree,Arial,Helvetica,sans-serif}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font:10.3pt/1.52 var(--sans);color:var(--brun);background:#fff}
a{color:var(--terra-d);text-decoration:none}
a.url{word-break:break-all;font-size:9pt}
h1,h2,h3{font-family:var(--serif);font-weight:500;color:var(--brun);line-height:1.15;break-after:avoid}
h1{font-size:28pt;margin:0 0 14pt;padding-bottom:10pt;border-bottom:2px solid var(--rose)}
h1 .num{display:block;font:600 11pt var(--sans);letter-spacing:.14em;color:var(--terra-d);margin-bottom:6pt}
h2{font-size:16.5pt;margin:20pt 0 6pt;color:var(--terra-d)}
h3{font-size:12.5pt;margin:14pt 0 5pt;font-family:var(--sans);font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--sauge-d)}
p{margin:0 0 7pt}
ul,ol{margin:0 0 9pt;padding-left:16pt}
li{margin:0 0 4pt}
.chap{break-before:page}
#mentions,.chap.suite{break-before:auto;margin-top:22pt}
td:empty{height:20pt}
#sources li,#mentions p{font-size:9pt;line-height:1.42;margin-bottom:2.5pt}
#sources h2,#mentions h2{font-size:13pt;margin-top:12pt}
table{width:100%;border-collapse:collapse;margin:6pt 0 12pt;font-size:9.4pt;break-inside:avoid;background:var(--card)}
th{background:var(--rose-l);color:var(--brun);text-align:left;font-weight:700;padding:5pt 7pt;border-bottom:1.5px solid var(--rose)}
td{padding:5pt 7pt;border-bottom:1px solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:#fcf8f3}
ul.prods{list-style:none;padding:0}
ul.prods li{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--terra);border-radius:8pt;padding:7pt 10pt;margin:0 0 6pt;break-inside:avoid}
.verif{display:inline-block;font:700 7.6pt/1 var(--sans);letter-spacing:.04em;text-transform:uppercase;color:#7a3f27;background:var(--rose-l);border:1px solid var(--rose);border-radius:20pt;padding:2.5pt 6pt;margin-left:4pt;white-space:nowrap;vertical-align:1pt}
.box{border-radius:10pt;padding:9pt 12pt;margin:8pt 0 12pt;break-inside:avoid;font-size:10pt}
.box p{margin:0}
.box.info{background:var(--sauge-l);border:1px solid #d6ddcf}
.box.clara{background:#fff6e8;border:1.5px dashed var(--terra)}
.box.medecin{background:#fbecea;border-left:4px solid #a8412f}
/* Couverture */
.cover{height:297mm;width:210mm;background:linear-gradient(160deg,var(--terra) 0%,var(--terra-d) 72%);color:var(--cream);padding:30mm 24mm 26mm;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden;break-after:page}
.cover:before{content:"";position:absolute;right:-40mm;top:-30mm;width:150mm;height:190mm;border:2px solid rgba(247,241,234,.25);border-radius:999px 999px 30mm 30mm}
.cover:after{content:"";position:absolute;right:-10mm;top:10mm;width:110mm;height:150mm;border:2px solid rgba(247,241,234,.16);border-radius:999px 999px 24mm 24mm}
.cover .k{font:600 11pt var(--sans);letter-spacing:.2em;text-transform:uppercase;opacity:.9}
.cover h1{font:500 44pt/1.05 var(--serif);color:var(--cream);border:0;margin:14mm 0 8mm;max-width:150mm}
.cover .sous{font-size:14pt;max-width:130mm;opacity:.95}
.cover .logo{font:500 22pt var(--serif)}.cover .logo b{font-style:italic;font-weight:600}
.cover .ed{font-size:10.5pt;opacity:.85;margin-top:3mm}
/* Sommaire */
.toc{break-after:page}
.toc ol{list-style:none;padding:0;margin:10pt 0 0}
.toc li{display:flex;align-items:baseline;gap:8pt;padding:7pt 0;border-bottom:1px solid var(--line);font-size:12pt}
.toc li .n{font:600 10pt var(--sans);color:var(--terra-d);width:22pt}
.toc li .t{font-family:var(--serif);font-size:13.5pt}
.toc li .d{flex:1;border-bottom:1px dotted var(--rose);transform:translateY(-3pt)}
.toc li .p{font-weight:700;color:var(--terra-d)}
.toc .note{margin-top:16pt;color:var(--mut);font-size:9.6pt}
"""


def document(corps, chap, pages=None, titre=TITRE, kicker="Guide PDF · Carnet capillaire",
             sous="Lire une étiquette, connaître ton profil, choisir trois produits à chaque budget, et une routine qui tient dans la vraie vie."):
    pages = pages or {}
    lis = "".join(
        f'<li><span class="n">{(f"{k:02d}" if t not in ("Sources", "Mentions") else "")}</span><span class="t">{html.escape(t)}</span><span class="d"></span><span class="p">{pages.get(cid, "")}</span></li>'
        for k, (cid, t) in enumerate(chap, 1))
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{html.escape(titre)} | Carnet capillaire</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Figtree:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="cover"><div><p class="k">{html.escape(kicker)}</p><h1>{html.escape(titre)}</h1>
<p class="sous">{html.escape(sous)}</p></div>
<div><p class="logo">carnet<b>capillaire</b></p><p class="ed">{EDITION} · Sélection indépendante, sources citées</p></div></div>
<div class="toc"><h1>Sommaire</h1><ol>{lis}</ol>
<p class="note">Chaque produit porte un badge {VERIF} tant qu'il n'a pas été testé, et que sa liste d'ingrédients et son prix n'ont pas été contrôlés en boutique.</p></div>
{corps}
</body></html>"""


def imprimer(html_path, pdf_path):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=8000", f"--print-to-pdf={pdf_path}", "file://" + html_path],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def pages_chapitres(pdf_path, chap):
    import fitz
    doc = fitz.open(pdf_path)
    res = {}
    for cid, t in chap:
        for pno in range(2, len(doc)):  # titre de chapitre = texte en très gros corps (h1, 28 pt)
            gros = "".join(s["text"] for b in doc[pno].get_text("dict")["blocks"] for l in b.get("lines", [])
                            for s in l["spans"] if s["size"] > 22)
            if t.lower()[:30] in re.sub(r"\s+", " ", gros).lower():
                res[cid] = pno + 1; break
    return res, len(doc)


def numeroter(pdf_path, titre=TITRE):
    import fitz
    doc = fitz.open(pdf_path)
    for pno in range(1, len(doc)):  # pas de numéro sur la couverture
        p = doc[pno]
        r = p.rect
        p.insert_text((r.width / 2 - 8, r.height - 28), f"{pno + 1}", fontsize=8.5, fontname="helv", color=(0.42, 0.35, 0.31))
        p.insert_text((50, r.height - 28), "Carnet capillaire · " + titre, fontsize=7.5, fontname="helv", color=(0.6, 0.52, 0.47))
    tmp = pdf_path + ".tmp"
    doc.save(tmp, garbage=3, deflate=True); doc.close()
    os.replace(tmp, pdf_path)


def exporter(md, out_html, out_pdf, **doc):
    """Deux passes (pagination du sommaire), puis numéros de page. Renvoie (pages des chapitres, nb de pages)."""
    corps, chap = convertir(md)
    with tempfile.TemporaryDirectory() as tmp:
        h1 = os.path.join(tmp, "passe1.html"); p1 = os.path.join(tmp, "passe1.pdf")
        open(h1, "w", encoding="utf-8").write(document(corps, chap, **doc))
        imprimer(h1, p1)
        pages, n = pages_chapitres(p1, chap)
    open(out_html, "w", encoding="utf-8").write(document(corps, chap, pages, **doc))
    imprimer(out_html, out_pdf)
    pages2, n2 = pages_chapitres(out_pdf, chap)
    if pages2 != pages:
        print("attention : pagination différente entre les deux passes", pages, pages2)
    numeroter(out_pdf, doc.get("titre", TITRE))
    print(f"{out_pdf} : {n2} pages, {len(chap)} chapitres")
    for cid, t in chap:
        print(f"  p.{pages2.get(cid, '?'):>3}  {t}")
    return pages2, n2


def vignettes(pdf_path, pnos, prefixe):
    import fitz
    from PIL import Image
    doc = fitz.open(pdf_path)
    for k, pno in enumerate(pnos, 1):
        pix = doc[pno].get_pixmap(dpi=130)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        im = im.resize((620, round(620 * pix.height / pix.width)), Image.LANCZOS)
        dest = os.path.join(ROOT, "_assets", f"{prefixe}-{k}.webp")
        im.save(dest, "WEBP", quality=80, method=6)
        print("vignette", dest, im.size)


def guide_type(tid, source, avec_apercus=False):
    t = TYPES[tid]
    d = os.path.join(G, "types")
    src = os.path.join(d, f"guide-cheveux-{tid}.md")
    if not os.path.exists(src):
        print("source absente (hors dépôt, à régénérer) :", src); return None
    md = inclure(open(src, encoding="utf-8").read(), source)
    base = os.path.join(d, f"guide-cheveux-{tid}")
    titre = f"Le guide des cheveux {t['nom']}"
    pages, n = exporter(md, base + ".html", base + ".pdf", titre=titre, kicker=f"Guide PDF · Cheveux {t['nom']}",
                        sous=f"Ta routine semaine par semaine, 3 produits à chaque budget, les erreurs à éviter et les problèmes des cheveux {t['nom']}.")
    if not 15 <= n <= 20:
        print(f"ATTENTION : {n} pages pour le guide {tid}, la cible est de 15 à 20 pages")
    if avec_apercus:
        cible = next((p for cid, p in pages.items() if cid.startswith("ta-routine-semaine")), 3) - 1
        vignettes(base + ".pdf", [0, cible], f"guide-{tid}-apercu")
    return n


def main():
    source = open(SRC, encoding="utf-8").read()
    ap = "--apercus" in sys.argv
    if "--types" not in sys.argv and "--type" not in sys.argv or "--tout" in sys.argv:
        pages, n = exporter(source, OUT_HTML, OUT_PDF)
        if ap:
            vignettes(OUT_PDF, [0, 1, pages.get("cheveux-boucles", 8) - 1], "guide-apercu")
    if "--types" in sys.argv or "--tout" in sys.argv:
        bilan = {tid: guide_type(tid, source, ap) for tid in TYPES}
        print("Guides par type :", ", ".join(f"{k} {v} p." for k, v in bilan.items()))
    elif "--type" in sys.argv:
        guide_type(sys.argv[sys.argv.index("--type") + 1], source, ap)


if __name__ == "__main__":
    main()
