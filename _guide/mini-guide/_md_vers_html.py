import re, html, sys
src, dst = sys.argv[1], sys.argv[2]
md = open(src, encoding="utf-8").read()
md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
def inl(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"(https://[^\s<]+)", r'<a href="\1">\1</a>', s)
    return s
out, lst, n_err = [], None, 0
lines = md.split("\n")
title = ""
def close():
    global lst
    if lst: out.append(f"</{lst}>"); lst = None
for l in lines:
    if l.startswith("# "):
        title = l[2:].strip(); continue
    if l.startswith("## "):
        close(); h = l[3:].strip()
        m = re.match(r"Erreur n°(\d) : (.*)", h)
        if m:
            if m.group(1) != "1": out.append("</section>")
            out.append(f'<section class="err"><p class="num">Erreur {m.group(1)}</p><h2>{inl(m.group(2)[0].upper()+m.group(2)[1:])}</h2>')
            n_err = int(m.group(1))
        else:
            if n_err: out.append("</section>"); n_err = 0
            cls = ' class="src"' if h == "Sources" else (' class="check"' if h.startswith("Ta check") else "")
            out.append(f"<h2{cls}>{inl(h)}</h2>")
        continue
    if l.startswith("### "):
        close(); out.append(f"<h3>{inl(l[4:])}</h3>"); continue
    if l.startswith("> "):
        close(); t = l[2:]
        cls = "attention" if "Quand consulter" in t else "astuce"
        out.append(f'<aside class="{cls}"><p>{inl(t)}</p></aside>'); continue
    m = re.match(r"^(- |\d+\. )(.*)", l)
    if m:
        k = "ol" if m.group(1)[0].isdigit() else "ul"
        if lst != k: close(); out.append(f"<{k}>"); lst = k
        out.append(f"<li>{inl(m.group(2))}</li>"); continue
    if not l.strip(): close(); continue
    close(); out.append(f"<p>{inl(l)}</p>")
close()
body = "\n".join(out)
# premier paragraphe en italique = sous-titre de couverture
body = body.replace("<p><em>Le mini-guide gratuit", '<p class="sous"><em>Le mini-guide gratuit', 1)
css = """
@page{size:A4;margin:16mm 17mm 16mm}
*{box-sizing:border-box}
:root{--cream:#f7f1ea;--terra:#9a5236;--brun:#2e211b;--sauge:#4f5e47;--rose:#f6e4dc;--mut:#6b5a50;--line:#eadfd3}
html{background:var(--cream)}
body{margin:0 auto;max-width:760px;padding:24px 18px 60px;color:var(--brun);font:11.2pt/1.55 Figtree,Arial,Helvetica,sans-serif;background:var(--cream);-webkit-print-color-adjust:exact;print-color-adjust:exact}
h1,h2,h3{font-family:Fraunces,Georgia,serif;font-weight:600;line-height:1.15;color:var(--brun)}
.cover{background:linear-gradient(160deg,#c47a5a,var(--terra) 70%);color:var(--cream);border-radius:18px;padding:26px 28px;margin:0 0 18px}
.cover .k{font-size:9pt;letter-spacing:.14em;text-transform:uppercase;opacity:.9;margin:0}
.cover h1{color:#fff;font-size:28pt;margin:8px 0 6px}
.cover .sous{margin:0;opacity:.95}
h2{font-size:17pt;margin:18px 0 8px}
h3{font-size:12pt;font-family:Figtree,Arial,sans-serif;font-weight:700;color:var(--terra);text-transform:uppercase;letter-spacing:.06em;margin:12px 0 4px}
p{margin:0 0 8px}
ul,ol{margin:0 0 8px;padding-left:1.25em}
li{margin:0 0 4px}
a{color:var(--terra);word-break:break-all}
.err{margin-top:14px}.err h2,.err h3{break-after:avoid}
.err .num{display:inline-block;background:var(--rose);color:var(--terra);font-weight:700;font-size:9.5pt;letter-spacing:.1em;text-transform:uppercase;border-radius:999px;padding:3px 12px;margin:0}
.err h2{margin-top:8px}
.astuce{background:#eef1ea;border-left:4px solid var(--sauge);border-radius:10px;padding:10px 14px;margin:10px 0;break-inside:avoid}
.astuce p,.attention p{margin:0}
.attention{background:var(--rose);border-left:4px solid var(--terra);border-radius:10px;padding:10px 14px;margin:10px 0;break-inside:avoid}
h2.check{break-before:avoid}h2.check + ol{break-inside:avoid}
h2.check + ol{background:#fffdfa;border:1px solid var(--line);border-radius:12px;padding:12px 14px 8px 2.2em}
h2.src{font-size:13pt}
h2.src + ul{font-size:8.6pt;color:var(--mut)}
.print{position:fixed;right:16px;bottom:16px;background:var(--terra);color:#fff;border:0;border-radius:999px;padding:12px 20px;font:600 15px Figtree,Arial,sans-serif;cursor:pointer}
@media print{.print{display:none}body{padding:0;max-width:none;background:var(--cream)}html{background:var(--cream)}}
"""
doc = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} | Carnet capillaire</title><meta name="robots" content="noindex">
<style>{css}</style></head><body>
<header class="cover"><p class="k">Mini-guide gratuit · Carnet capillaire</p><h1>{html.escape(title)}</h1></header>
{body}
<button class="print" type="button" onclick="window.print()">Imprimer ou enregistrer en PDF</button>
</body></html>"""
open(dst, "w", encoding="utf-8").write(doc)
