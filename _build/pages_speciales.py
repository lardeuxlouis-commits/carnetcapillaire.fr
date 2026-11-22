"""Pages à gabarit spécial : accueil, tests, quiz, guide PDF (e-book), contact, mentions légales.
Chaque page indique en commentaire HTML son mot-clé cible et le volume Keyword Planner (FR, 22/11/2026)."""
G = {}

META = {
    "quiz-type-de-cheveux": {"court": "Quel est ton type de cheveux", "rubrique": "outil"},
    "tests-cheveux": {"court": "Les tests", "rubrique": "outil"},
    "guide-produits-cheveux-pdf": {"court": "Le guide PDF", "rubrique": "offre"},
    "contact": {"court": "Contact", "rubrique": "legal"},
    "mentions-legales": {"court": "Mentions légales", "rubrique": "legal"},
}


def init(g):
    G.update(g)
    for s, m in META.items():
        if s not in G["PAGES"]:
            G["PAGES"][s] = dict(m, slug=s)


def C(slug, field="court"):
    return G["PAGES"][slug].get(field, "")


CURLS = [  # illustrations des cartes de textures (SVG, quelques octets) : raides, ondulés, bouclés, frisés, crépus
    '<svg class="curl" viewBox="0 0 120 96" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M34 6v84"/><path d="M60 6v84"/><path d="M86 6v84"/></g></svg>',
    '<svg class="curl" viewBox="0 0 120 96" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M30 6c16 14-14 28 2 44s-14 26 0 40"/><path d="M60 6c16 14-14 28 2 44s-14 26 0 40"/><path d="M90 6c16 14-14 28 2 44s-14 26 0 40"/></g></svg>',
    '<svg class="curl" viewBox="0 0 120 96" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M40 6c-16 6 16 12 0 18s16 12 0 18s16 12 0 18s16 12 0 18"/><path d="M80 6c-16 6 16 12 0 18s16 12 0 18s16 12 0 18s16 12 0 18"/></g></svg>',
    '<svg class="curl" viewBox="0 0 120 96" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M38 6c-10 3 10 7 0 10s10 7 0 10s10 7 0 10s10 7 0 10s10 7 0 10s10 7 0 10s10 7 0 10"/><path d="M82 6c-10 3 10 7 0 10s10 7 0 10s10 7 0 10s10 7 0 10s10 7 0 10s10 7 0 10s10 7 0 10"/></g></svg>',
    '<svg class="curl" viewBox="0 0 120 96" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M34 6l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4"/><path d="M76 6l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4l-10 4l10 4"/></g></svg>',
]

# Photo du hero : image générée par IA, utilisable en ligne (confirmé par Louis le 22/11/2026).
HERO_IMG = ('<img src="/images/hero-clara-640.webp" srcset="/images/hero-clara-640.webp 640w, /images/hero-clara.webp 1200w" '
            'sizes="(min-width:900px) 440px, 92vw" width="1200" height="1600" fetchpriority="high" decoding="async" '
            'alt="Femme aux cheveux bouclés souriante">')


def lcard(slug, kick, texte):
    return (f'<a class="lcard rv" href="{G["url"](slug)}"><span class="k">{G["E"](kick)}</span><h3>{G["E"](C(slug))}</h3>'
            f'<p>{G["E"](texte)}</p><span class="go">Lire le guide →</span></a>')


EB = "guide-produits-cheveux-pdf"
TESTS = [  # (url, titre, sous-titre, durée)
    ("/quiz-type-de-cheveux/", "Quel est ton type de cheveux ?", "Texture, épaisseur, cuir chevelu, porosité : ton profil et ta routine.", "9 questions"),
    ("/meilleur-shampoing/#simulateur", "Quel shampoing est fait pour toi ?", "Trois produits adaptés à ton cuir chevelu, tes longueurs et ton budget.", "6 questions"),
    ("/cuir-chevelu-qui-gratte/#simulateur", "Diagnostic cuir chevelu", "Gras, sec, pellicules, démangeaisons : les bons gestes, et quand consulter.", "6 questions"),
    ("/soins-cheveux/#simulateur", "Ta routine et ton budget", "Ta routine type, poste par poste, et ce qu'elle coûte par mois.", "6 questions"),
]
TEST_ICO = ['<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3c3 3-3 6 0 9s-3 6 0 9M16 3c3 3-3 6 0 9s-3 6 0 9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
            '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 3h6v3l2 3v11a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V9l2-3z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M7 13h10" stroke="currentColor" stroke-width="2"/></svg>',
            '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="m16.5 16.5 4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
            '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 8h8M8 12h3M13 12h3M8 16h3M13 16h3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>']


def tests_html(cls="tests"):
    E = G["E"]
    return f'<div class="{cls}">' + "".join(
        f'<a class="tst" href="{u}"><span class="ico">{TEST_ICO[i]}</span><span class="tt">{E(t)}</span><span class="ts">{E(s)}</span><span class="td">{E(d)} · gratuit →</span></a>'
        for i, (u, t, s, d) in enumerate(TESTS)) + "</div>"


def ebook_band():
    return f"""<section class="sec" aria-labelledby="h-eb"><div class="wrap"><div class="eb-band rv">
<div class="eb-cover" aria-hidden="true"><span class="k">Guide PDF</span><strong>Les meilleurs produits pour ton type de cheveux</strong><span>Carnet capillaire</span></div>
<div><p class="kicker">Le guide PDF</p><h2 id="h-eb">Arrête d'acheter au hasard</h2>
<p>Un guide PDF par type de cheveux : ta routine semaine par semaine, 3 produits à chaque budget, les ingrédients à repérer. Une sélection indépendante : aucune marque ne paie pour y figurer.</p>
<a class="btn" href="/{EB}/">Choisir mon guide, {G["PRIX_TYPE"]}</a></div></div></div></section>"""


VIDEO = ('<video class="hero-vid" autoplay muted loop playsinline preload="metadata" poster="/images/hero-femme-poster.jpg" aria-hidden="true" tabindex="-1">'
         '<source src="/images/hero-femme.webm" type="video/webm"><source src="/images/hero-femme.mp4" type="video/mp4"></video>'
         '<div class="hero-voile" aria-hidden="true"></div>')  # vidéo générée par IA, droits OK (Louis, 22/11/2026)


PROB_ICO = {  # pictos simples des 6 problèmes (SVG, quelques octets)
    "gras": '<path d="M12 3c3 4 6 7.5 6 11a6 6 0 0 1-12 0c0-3.5 3-7 6-11z"/>',
    "sec": '<path d="M12 3v18M5 7l14 10M19 7 5 17"/>',
    "casse": '<path d="M5 19 11 11M13 9l6-6M9 7l2 2M15 13l2 2"/>',
    "gratte": '<circle cx="12" cy="12" r="8"/><path d="M9 10h.01M15 10h.01M9 15c2 1.5 4 1.5 6 0"/>',
    "blancs": '<path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/><circle cx="12" cy="12" r="3"/>',
    "chute": '<path d="M12 3c2 4-2 7 0 11M8 5c2 4-2 7 0 11M16 5c2 4-2 7 0 11M6 21h12"/>',
}
HOW_ICO = ['<path d="M9 9a3 3 0 1 1 4 2.8c-.7.3-1 .9-1 1.7V14M12 18h.01"/><circle cx="12" cy="12" r="9"/>',
           '<path d="M7 4c3 3-3 6 0 9s-3 6 0 7M15 4c3 3-3 6 0 9s-3 6 0 7"/>',
           '<path d="M9 3h6v3l2 3v11a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V9l2-3z"/><path d="M7 13h10"/>']


def svg(path):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{path}</svg>'


def accueil():
    """Accueil simplifié (consigne de Louis, 22/11/2026) : hero, comment ça marche, tests, types en photo, problèmes,
    guide PDF + mini-guide, confiance. Aucun texte de plus de 2 lignes. Saison et chiffres calculés au build."""
    E, url, img = G["E"], G["url"], G["img"]
    DOMAIN, SITE = G["DOMAIN"], G["SITE"]
    ch = G["chiffres"]()
    sai, acc, sliens, _ = G["saison"]()
    bande = " ".join(f'<a href="{url(sl)}">{E(t)}</a>' for sl, t in sliens)
    types = [("cheveux-raides", "type-raides", "Raides", "Femme aux cheveux raides et lisses"),
             ("cheveux-ondules", "type-ondules", "Ondulés", "Femme aux cheveux ondulés mi-longs"),
             ("cheveux-boucles", "type-boucles", "Bouclés", "Femme aux cheveux bouclés en spirales"),
             ("cheveux-crepus", "type-crepus", "Crépus", "Femme aux cheveux crépus portés au naturel")]
    ptypes = "".join(f'<a class="ptype rv" href="{url(sl)}">{img(nom, alt, sizes="(min-width:900px) 270px, 46vw")}<span>{E(mot)}<i>Voir →</i></span></a>'
                     for sl, nom, mot, alt in types)
    probs = [("cheveux-gras", "gras", "Racines grasses"), ("cheveux-secs", "sec", "Cheveux secs"), ("cheveux-abimes", "casse", "Casse"),
             ("cuir-chevelu-qui-gratte", "gratte", "Démangeaisons"), ("cheveux-blancs", "blancs", "Cheveux blancs"), ("chute-de-cheveux-femme", "chute", "Chute")]
    plinks = "".join(f'<li><a href="{url(sl)}">{svg(PROB_ICO[k])}{E(t)}</a></li>' for sl, k, t in probs)
    how = [("Tu réponds à quelques questions", "1"), ("Tu découvres ton type et ta routine", "2"), ("Tu reçois les produits faits pour toi", "3")]
    howh = "".join(f'<li><span class="n">{svg(HOW_ICO[i])}</span><span><small>Étape {n}</small>{E(t)}</span></li>' for i, (t, n) in enumerate(how))
    maj = ch["maj"].strftime("%d/%m/%Y")
    LCT = G["MODE_LANCEMENT"]
    acc_guide = (f'{G["BIENTOT"]}<p class="small"><a href="/{EB}/">Découvrir les guides</a></p>' if LCT else f'<a class="btn" href="/{EB}/">Choisir mon guide</a>')
    acc_cap = "" if LCT else ('<div class="rv" data-capture="accueil" data-titre="Le mini-guide gratuit" data-sous="« Les 5 erreurs qui abîment tes cheveux », 5 pages, dans ta boîte mail."></div>')
    acc_pop = "" if LCT else ('<div class="cap-pop" hidden role="dialog" aria-label="Mini-guide gratuit"><button type="button" class="pop-x" aria-label="Fermer">×</button>\n'
                              '<div data-capture="accueil-encart" data-titre="Avant de partir : le mini-guide gratuit" data-sous="Les 5 erreurs qui abîment tes cheveux, en 5 pages."></div></div>\n')
    body = f"""<section class="hero hero-v">{VIDEO}
<div class="wrap"><div>
<p class="kicker">Carnet capillaire</p>
<h1>Tes cheveux, <em>enfin</em> compris</h1>
<p class="lead">Raides, bouclés ou crépus, gras ou secs : découvre ton type, ta routine et les produits qui te vont vraiment.</p>
<div class="cta-main"><a class="btn btn-xl" href="/quiz-type-de-cheveux/">Fais le test gratuit (2 min)</a>
<a class="cta-sec" href="/meilleur-shampoing/#simulateur">ou trouve ton shampoing idéal</a></div>
<p class="micro">Résultat immédiat · gratuit · sans inscription</p>
</div>
</div></section>
<aside class="saison" aria-label="Conseils de saison"><div class="wrap"><span><strong>Spécial {E(sai)} :</strong> {E(acc)}.</span> {bande} <a href="/tests-cheveux/">Fais le test</a></div></aside>

<section class="sec tight" aria-labelledby="h-how"><div class="wrap">
<h2 id="h-how" class="rv" style="margin-top:0">Comment ça marche</h2>
<ol class="how rv">{howh}</ol>
</div></section>

<section class="sec tight alt" id="tests" aria-labelledby="h-tests"><div class="wrap">
<h2 id="h-tests" class="rv" style="margin-top:0">Les 4 tests gratuits</h2>
{tests_html("tests-home rv")}
</div></section>

<section class="sec tight" id="types" aria-labelledby="h-types"><div class="wrap">
<h2 id="h-types" class="rv" style="margin-top:0">Par type de cheveux</h2>
<div class="ptypes">{ptypes}</div>
<p class="mini-liens rv"><a href="/cheveux-frises/">Frisés</a><a href="/cheveux-fins/">Fins ou épais</a><a href="/porosite-cheveux/">Ta porosité</a><a href="/types-de-cheveux/">Les types de 1A à 4C</a></p>
</div></section>

<section class="sec tight alt" id="problemes" aria-labelledby="h-prob"><div class="wrap prob-g">
<div><h2 id="h-prob" class="rv" style="margin-top:0">Par problème</h2>
<ul class="probs rv">{plinks}</ul>
<p class="mini-liens rv"><a href="/problemes-cheveux/">Tous les problèmes</a><a href="/soins-cheveux/">Soins et sélections</a></p></div>
<figure class="rv">{img("probleme", "Femme qui observe les pointes de ses longueurs", sizes="300px")}</figure>
</div></section>

<section class="sec tight" aria-labelledby="h-eb"><div class="wrap offres">
<div class="eb-h rv">{img("routine", "Flacons de soins capillaires sans marque posés à plat", sizes="(min-width:560px) 170px, 70vw")}
<div><p class="kicker">Guides PDF · {G["PRIX_TYPE"]} par type</p><h2 id="h-eb">Arrête d'acheter au hasard</h2>
<p>Le guide de ton type de cheveux : ta routine semaine par semaine et 3 produits par budget, sources citées.</p>
{acc_guide}</div></div>
{acc_cap}
</div></section>

<aside class="trust" aria-label="Pourquoi nous faire confiance"><div class="wrap"><ul>
<li>Mis à jour le <strong>{maj}</strong></li>
<li><strong>{ch["guides"]} guides</strong> et <strong>{ch["produits"]} produits</strong> sélectionnés sur leur composition</li>
<li>Sélection indépendante : aucune marque ne paie pour figurer</li>
<li>Nos sources : PubMed, Ameli, ANSM, DGCCRF, règlement cosmétique européen ({ch["sources"]} références citées)</li>
</ul></div></aside>

{acc_pop}<div class="stick" aria-label="Raccourci vers le test"><a class="btn" href="/quiz-type-de-cheveux/">Fais le test (2 min)</a><button type="button" class="stick-x" aria-label="Fermer la barre">×</button></div>"""
    schema = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": DOMAIN + "/", "inLanguage": "fr-FR",
         "description": "Tests, guides et sélections de produits pour tous les types de cheveux, des raides aux crépus.", "publisher": {"@type": "Organization", "name": SITE, "url": DOMAIN + "/"}},
        {"@context": "https://schema.org", "@type": "Organization", "name": SITE, "url": DOMAIN + "/", "logo": DOMAIN + "/favicon.svg",
         "sameAs": []},  # TODO réseaux : ajouter les URL Instagram et TikTok de Carnet capillaire
    ]
    pre = '\n<link rel="preload" as="image" href="/images/hero-femme-poster.jpg" fetchpriority="high">'
    return G["page"]("Carnet capillaire : tes cheveux, enfin compris",
                     "Raides, fins, bouclés ou crépus, gras ou secs : fais le test gratuit, puis découvre ta routine et les produits faits pour tes cheveux.",
                     "/", body, schema, None, ("carnet capillaire (marque ; entrée vers les tests, types, problèmes et soins)", "n.r. (marque)"), extra_js=pre)


def tests():
    E, DOMAIN = G["E"], G["DOMAIN"]
    crumbs = [("Accueil", "/"), ("Les tests", "/tests-cheveux/")]
    body = f"""<div class="wrap">{G["crumbs_html"](crumbs)}
<header class="ahead" style="grid-template-columns:1fr"><div style="max-width:760px">
<p class="kicker">Tests gratuits · 2 minutes chacun</p>
<h1>Tests cheveux : diagnostic capillaire gratuit en ligne</h1>
<p class="chapo">Quatre tests rapides pour comprendre tes cheveux et arrêter d'acheter au hasard. Chacun te donne un résultat concret : ton profil, les gestes à adopter, et des produits adaptés. Tes réponses restent dans ton navigateur.</p></div></header>
{tests_html("tests tests-page")}
<div class="txt" style="margin-top:40px">
<section aria-labelledby="ordre"><h2 id="ordre">Par quel test commencer ?</h2>
<ul><li><strong>Tu ne sais pas vraiment quel est ton type de cheveux</strong> : commence par <a href="/quiz-type-de-cheveux/">quel est ton type de cheveux</a>. C'est la base de tout le reste.</li>
<li><strong>Tu cherches surtout un shampoing</strong> : le test <a href="/meilleur-shampoing/#simulateur">quel shampoing est fait pour toi</a> part de ton cuir chevelu, le vrai critère de choix.</li>
<li><strong>Ton cuir chevelu gratte, regraisse ou pèle</strong> : fais le <a href="/cuir-chevelu-qui-gratte/#simulateur">diagnostic cuir chevelu</a>. Il te dit aussi quand il vaut mieux consulter.</li>
<li><strong>Tu veux simplifier ta salle de bains</strong> : le <a href="/soins-cheveux/#simulateur">simulateur de routine et de budget</a> te montre ce que tu dépenses vraiment, poste par poste.</li></ul></section>
<section aria-labelledby="limites"><h2 id="limites">Ce que ces tests ne font pas</h2>
<p>Ce sont des outils d'orientation, pas des diagnostics médicaux. Ils s'appuient sur ce que tu observes, et sur les repères expliqués dans nos guides, sources à l'appui. Une démangeaison qui dure, des plaques, des croûtes ou une chute importante se montrent à un médecin ou à un dermatologue, pas à un questionnaire.</p>
<p>Les produits proposés à la fin sont choisis sur leur composition. Certains liens sont affiliés : si tu achètes, le site touche une petite commission, sans surcoût pour toi. <a href="/mentions-legales/#affiliation">Comment ça marche</a></p></section>
</div>
{G["cta_ebook"]()}
</div>"""
    schema = [G["schema_crumbs"](crumbs),
              {"@context": "https://schema.org", "@type": "ItemList", "name": "Tests cheveux gratuits", "itemListElement": [
                  {"@type": "ListItem", "position": i, "name": t, "url": DOMAIN + u} for i, (u, t, s, d) in enumerate(TESTS, 1)]}]
    return G["page"]("Tests cheveux : diagnostic capillaire gratuit",
                     "Quatre tests gratuits : ton type de cheveux, le shampoing fait pour toi, un diagnostic du cuir chevelu, et ta routine avec son budget mensuel.",
                     "/tests-cheveux/", body, schema, "tests", ("diagnostic capillaire en ligne / test cheveux", "n.r."))


QUIZ_FAQ = [
    ("Le quiz est-il fiable ?", "C'est une estimation à partir de ce que tu observes. Il donne une très bonne base pour choisir tes produits, mais tes cheveux restent la meilleure référence : si une routine ne te convient pas après quelques lavages, ajuste."),
    ("Pourquoi j'ai plusieurs types sur la tête ?", "C'est le cas de beaucoup de gens. Les cheveux sont souvent plus ondulés ou plus serrés à la nuque, et plus lâches sur le dessus. Choisis ta routine selon la zone majoritaire."),
    ("Mes réponses sont-elles enregistrées ?", "Non. Le calcul se fait dans ton navigateur, rien n'est envoyé ni stocké. Si tu recharges la page, tout s'efface. Seule exception : si tu demandes ton résultat par e-mail à la fin, ton adresse et ton résultat sont envoyés pour te l'écrire, avec ton accord."),
    ("Faut-il faire le quiz sur cheveux mouillés ?", "Non, sur cheveux secs, lavés la veille ou l'avant-veille, sans crème, sans gel et sans lissage. L'eau et les produits changent la forme et le toucher des cheveux."),
    ("Mes cheveux sont raides, le quiz me concerne-t-il ?", "Oui. Il a été pensé pour toutes les textures, des raides aux crépus. Pour des cheveux raides, ce sont surtout l'épaisseur et le cuir chevelu qui orientent la routine."),
    ("Et si j'ai des démangeaisons, des plaques ou une chute importante ?", "Le test te le signalera. Une démangeaison qui dure, des plaques ou une chute importante ne se règlent pas avec une routine : parle-en à ton médecin ou à un dermatologue."),
]


def quiz():
    E, DOMAIN = G["E"], G["DOMAIN"]
    faq = "".join(f"<details><summary>{E(q)}</summary><p>{E(r)}</p></details>" for q, r in QUIZ_FAQ)
    crumbs = [("Accueil", "/"), ("Les tests", "/tests-cheveux/"), ("Quel est ton type de cheveux", "/quiz-type-de-cheveux/")]
    body = f"""<div class="wrap">{G["crumbs_html"](crumbs)}
<div class="quiz-wrap">
<header style="text-align:center"><p class="kicker" style="justify-content:center">Quiz gratuit · 2 minutes</p>
<h1>Quel est ton type de cheveux ?</h1>
<p class="chapo" style="max-width:36em;margin:0 auto 22px">9 questions pour estimer ta texture (de raides à crépus), ton épaisseur, ton cuir chevelu et ta porosité, puis la routine qui va avec. Observe une mèche sèche, sans produit, et laisse-toi guider.</p></header>
<div id="quiz" class="quiz" style="scroll-margin-top:90px" data-insta="{G["INSTAGRAM"]}" data-tiktok="{G["TIKTOK"]}"><noscript><p>Le quiz a besoin de JavaScript. En attendant, tu peux lire le guide des <a href="/types-de-cheveux/">types de cheveux de 1A à 4C</a>.</p></noscript></div>
<p class="small" style="text-align:center;margin-top:12px">Tes réponses ne sont ni envoyées ni enregistrées, sauf si tu demandes ton résultat par e-mail. <a href="/mentions-legales/#confidentialite">Confidentialité</a></p>
<div class="txt" style="margin:40px auto 0">
<section aria-labelledby="comment"><h2 id="comment">Comment fonctionne ce quiz</h2>
<p>Les deux premières questions estiment ta <strong>texture</strong>, d'après la forme de tes cheveux secs et leur rétraction : raides (type 1), ondulés (type 2), bouclés (type 3), frisés ou crépus (type 4). On s'appuie sur la classification de 1A à 4C, la plus utilisée par les coiffeurs et les créatrices, même si elle simplifie une réalité plus nuancée. Les chercheurs eux-mêmes décrivent toute une gamme de courbures, regroupées en 8 types dans une étude mondiale (<a href="https://pubmed.ncbi.nlm.nih.gov/18078200/" rel="noopener" target="_blank">De La Mettrie et al., 2007</a>).</p>
<p>Viennent ensuite ton <strong>épaisseur</strong> (fins, moyens ou épais) et ton <strong>cuir chevelu</strong> (équilibré, gras, sec, pellicules) : ce sont eux qui décident du shampoing. Les trois questions suivantes estiment ta <strong>porosité</strong>, c'est-à-dire la façon dont ton cheveu absorbe et garde l'eau. Pour aller plus loin, lis le <a href="/porosite-cheveux/">guide de la porosité</a>.</p>
<p>Enfin, ton souci principal personnalise le conseil final. Le résultat te renvoie vers le guide de ta texture, celui de ton problème principal et une sélection de soins adaptés.</p></section>
<section aria-labelledby="faq"><h2 id="faq">Questions fréquentes</h2>{faq}</section>
</div></div></div>"""
    schema = [G["schema_crumbs"](crumbs),
              {"@context": "https://schema.org", "@type": "WebApplication", "name": "Quiz type de cheveux, cuir chevelu et porosité", "url": DOMAIN + "/quiz-type-de-cheveux/",
               "applicationCategory": "LifestyleApplication", "operatingSystem": "Tous navigateurs", "inLanguage": "fr-FR", "isAccessibleForFree": True,
               "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in QUIZ_FAQ]}]
    js = f'\n<script src="/simulateurs.js?v={G["ASSET_V"]}" defer></script>\n<script src="/quiz.js?v={G["ASSET_V"]}" defer></script>'
    return G["page"]("Quiz : quel est ton type de cheveux ?",
                     "Quiz gratuit en 9 questions : découvre ta texture (raides à crépus), ton épaisseur, ton cuir chevelu, ta porosité et ta routine en 4 étapes.",
                     "/quiz-type-de-cheveux/", body, schema, "tests", ("quel est mon type de cheveux (outil)", "n.r."), extra_js=js)



# --- Guides PDF payants : sélecteur (/guide-produits-cheveux-pdf/), pages de vente par type (/guide/<type>/), /merci/ ---
# Prix et produits : _build/offres.json (SEUL endroit, TODO validation Louis), exposés par build.py (PRIX_TYPE, PRIX_PACK, BUMP, OFFRES).
# TODO Stripe : un Payment Link par produit, au nom de la micro-entreprise de Clara (dans 2 jours) :
#   - 6 liens « Le guide des cheveux <type> », 9,00 € TTC, redirection https://carnetcapillaire.fr/merci/?p=<type>&s={CHECKOUT_SESSION_ID}
#   - 1 lien « Pack complet tous types », 19,00 € TTC, redirection https://carnetcapillaire.fr/merci/?p=pack&s={CHECKOUT_SESSION_ID}
#   Acceptation des CGV obligatoire, reçus automatiques. Remplacer les ancres factices ci-dessous par les URL buy.stripe.com.
# Order bump : sur une page type, la case « Ajoute le pack complet pour 10 € de plus » bascule le bouton vers le lien du pack
# (le pack contient le guide du type). Variante possible côté Stripe : « ventes croisées » du Payment Link de chaque guide.
STRIPE = {}  # id du type -> Payment Link du guide (rempli par init_offres() depuis offres.json)
STRIPE_PACK = "#stripe-pack"  # TODO Stripe : Payment Link du pack (19 €)
# TODO livraison : vérification serveur comme pour le kit de mes-droits-handicap (~/Documents/paiements-sites/server.py) :
# 7 produits (6 types + pack), clé restreinte du compte Stripe de Clara, PDF hors de tout dépôt public. Le serveur vérifie que la
# session est payée, déduit le produit du Payment Link (jamais du paramètre p, qui ne sert qu'à l'affichage) et renvoie
# {ok, t, produits: ["boucles"] ou ["pack"]}. Puis renseigner VERIF_API = "https://.../pay/verifier" et GUIDE_DL = "https://.../pay/guide".
VERIF_API = None
GUIDE_DL = None
RENONCE = ("Je demande l'accès immédiat au guide après le paiement et je reconnais perdre mon droit de rétractation dès que le téléchargement est disponible "
           "(article L221-28 13° du code de la consommation).")


def init_offres():
    global STRIPE
    STRIPE = {t["id"]: f"#stripe-guide-{t['id']}" for t in G["OFFRES"]["types"]}  # TODO Stripe : Payment Link de chaque guide (9 €)


EBOOK_FAQ = [
    ("Quel guide choisir ?", "Celui de ta texture : raides, ondulés, bouclés, frisés ou crépus. Si tes cheveux sont surtout très fins, quelle que soit leur forme, prends le guide des cheveux fins. Tu hésites ? Le quiz gratuit te donne ton type en 2 minutes."),
    ("Que contient un guide par type ?", "Une vingtaine de pages rien que pour ton type : ton profil, la lecture des étiquettes, les gestes de base, une routine semaine par semaine, 3 produits par budget, les erreurs fréquentes, les problèmes associés et un calendrier."),
    ("Et le pack complet ?", "Le pack contient le guide complet (7 profils et tous les problèmes fréquents, une trentaine de pages) et les 6 guides par type. Utile si plusieurs types cohabitent à la maison, ou si tes cheveux mélangent deux textures."),
    ("Les produits sont-ils chers ?", "Pas forcément. Pour chaque type, il y a des produits petit budget (supermarché ou pharmacie), moyens et premium."),
    ("Les produits ont-ils été testés ?", "Ils sont choisis sur leur composition, leurs besoins et leur disponibilité en France. Les tests en conditions réelles sont en cours et seront signalés et datés dans les mises à jour."),
    ("Les marques paient-elles pour figurer dans les guides ?", "Non. Certains liens du site sont affiliés, et c'est toujours signalé, mais aucune marque n'achète sa place. Les PDF ne contiennent aucun lien affilié."),
    ("Comment je reçois mon guide ?", "Juste après le paiement, tu arrives sur une page de téléchargement. Tu reçois aussi un reçu par e-mail."),
    ("Un guide remplace-t-il un avis médical ?", "Non. Il parle de cosmétiques et de routine. Pour une chute importante, des plaques ou des démangeaisons qui durent, consulte un médecin ou un dermatologue."),
    ("Puis-je me rétracter ?", "Pour un contenu numérique disponible tout de suite, le droit de rétractation ne s'applique plus une fois le téléchargement possible, si tu l'as expressément accepté au moment de l'achat. Les conditions complètes figureront dans les conditions générales de vente."),
]
EB_SOMMAIRE = [("Mode d'emploi", "Comment trouver ton profil et utiliser le guide en 10 minutes."),
               ("Lire une étiquette INCI", "Tensioactifs doux ou forts, silicones, alcools, conservateurs, parfum : ce qu'il faut repérer."),
               ("Les 7 profils de cheveux", "Raides, ondulés, bouclés, frisés, crépus, fins, secs ou abîmés : le portrait de chacun."),
               ("Une routine par profil", "Laver, nourrir, hydrater, coiffer : les gestes et la fréquence."),
               ("3 produits par profil et par budget", "Petit, moyen, premium : des produits vendus en France, avec où les acheter."),
               ("Les problèmes fréquents", "Gras, pellicules, démangeaisons, casse, frisottis, cheveux blancs, après lissage, et quand consulter."),
               ("Le calendrier de routine", "Ta semaine type et les ajustements selon la saison."),
               ("Les sources", "Les études et textes officiels sur lesquels le guide s'appuie.")]


def nb_pages(pdf):
    import os
    if not os.path.exists(pdf):
        return None
    try:
        import fitz
        return len(fitz.open(pdf))
    except Exception:
        return None


def guide_infos():
    """Nombre de pages du guide complet (si le PDF existe en local) et aperçus disponibles dans _assets/."""
    import os
    root = G["ROOT"]
    pages = nb_pages(os.path.join(root, "_guide", "guide-produits-cheveux.pdf"))
    ap = [i for i in (1, 2, 3) if os.path.exists(os.path.join(root, "_assets", f"guide-apercu-{i}.webp"))]
    return pages, ap


def visuel_type(t, sizes="(min-width:900px) 200px, 44vw"):
    """Photo IA du type si elle existe dans _assets, sinon l'illustration SVG de la texture (TODO photo IA à générer)."""
    if t.get("photo"):
        return G["img"](t["photo"], t["alt"], sizes=sizes)
    return (f'<span class="gvis-svg" role="img" aria-label="{G["E"](t["alt"])}">{CURLS[t["curl"]]}</span>'
            f'<!-- TODO photo : photo IA « cheveux {G["E"](t["nom"])} » au format 3:4 (480 et 900 px) à ajouter dans _assets/ -->')


JS_ACHAT = """<script>
(function () {
  var c = document.getElementById("renonce"), b = document.getElementById("acheter"), u = document.getElementById("bump");
  if (!c || !b) return;
  var base = { href: b.getAttribute("href"), txt: b.textContent };
  function maj() {
    b.setAttribute("aria-disabled", c.checked ? "false" : "true");
    if (u) { b.setAttribute("href", u.checked ? u.getAttribute("data-href") : base.href); b.textContent = u.checked ? u.getAttribute("data-txt") : base.txt; }
  }
  c.addEventListener("change", maj); if (u) u.addEventListener("change", maj);
  b.addEventListener("click", function (e) { if (!c.checked) { e.preventDefault(); c.focus(); c.parentNode.style.outline = "2px solid #9a5236"; } });
})();
</script>"""


def ebook():
    """Page guide principale = sélecteur « Choisis ton guide » (6 guides par type) + le pack complet. Seule page indexée de l'offre."""
    E, DOMAIN, url = G["E"], G["DOMAIN"], G["url"]
    PT, PP = G["PRIX_TYPE"], G["PRIX_PACK"]
    crumbs = [("Accueil", "/"), ("Le guide PDF", f"/{EB}/")]
    faq = "".join(f"<details><summary>{E(q)}</summary><p>{E(r)}</p></details>" for q, r in EBOOK_FAQ)
    npages, ap = guide_infos()
    taille = f"{npages} pages" if npages else "une trentaine de pages"
    som = "".join(f"<li><strong>{E(t)}</strong><span>{E(x)}</span></li>" for t, x in EB_SOMMAIRE)
    legendes = ["La couverture", "Le sommaire", "Une page profil"]
    apercu = ('<div class="eb-apercu">' + "".join(
        f'<figure><img src="/images/guide-apercu-{i}.webp" width="620" height="877" loading="lazy" decoding="async" alt="Aperçu du guide PDF complet : {E(legendes[i - 1].lower())}"><figcaption>{E(legendes[i - 1])}</figcaption></figure>'
        for i in ap) + "</div>") if ap else ""
    cartes = "".join(
        f'<a class="gcard rv" href="{G["url_guide"](t["id"])}"><span class="gvis">{visuel_type(t)}</span>'
        f'<span class="gtxt"><span class="k">Guide PDF</span><strong>Cheveux {E(t["nom"])}</strong><span class="gacc">{E(t["accroche"])}</span>'
        f'<span class="gpx">{E(PT)}<i>Voir le guide →</i></span></span></a>' for t in G["OFFRES"]["types"])
    achat_pack = (f'<p>{G["BIENTOT"]}</p><p class="small">Les ventes ouvrent très bientôt.</p>' if G["MODE_LANCEMENT"] else
                  f'<label class="renonce"><input type="checkbox" id="renonce"> <span>{E(RENONCE)}</span></label>\n'
                  f'<p><a class="btn btn-xl" id="acheter" href="{STRIPE_PACK}" aria-disabled="true">Acheter le pack complet, {E(PP)}</a></p><!-- TODO Stripe : Payment Link du pack (STRIPE_PACK), CGV, mentions de l\'éditrice avant toute vente -->\n'
                  '<p class="small">Paiement sécurisé par Stripe. Téléchargement juste après le paiement.</p>')
    demo = "" if G["MODE_LANCEMENT"] else '<aside class="attention" role="note"><p class="lab">Démo</p><p>Les ventes ne sont pas encore ouvertes : les boutons d\'achat ne mènent nulle part pour l\'instant.</p></aside>'
    pack = f"""<section class="pack" id="pack" aria-labelledby="h-pack"><div class="pack-in">
<div class="eb-cover" aria-hidden="true"><span class="k">Pack complet</span><strong>Les meilleurs produits pour ton type de cheveux</strong><span>+ les 6 guides par type</span></div>
<div><p class="kicker">Le pack complet tous types · {E(PP)}</p><h2 id="h-pack">Tous les types, tous les problèmes</h2>
<p>Le guide complet ({E(taille)} : 7 profils, tous les problèmes fréquents, la lecture des étiquettes) <strong>et</strong> les 6 guides par type. Pour une maison où plusieurs types cohabitent, ou des cheveux qui mélangent deux textures.</p>
<div class="eb-prix"><p class="prix">{E(PP)}<small> TTC</small></p></div>
{achat_pack}</div></div></section>"""
    body = f"""<div class="wrap">{G["crumbs_html"](crumbs)}
<header class="sel-head"><p class="kicker">Guides PDF · Carnet capillaire</p>
<h1>Le guide des meilleurs produits pour ton type de cheveux</h1>
<p class="chapo">Choisis le guide de tes cheveux : ta routine semaine par semaine, 3 produits par budget, les erreurs à éviter et les problèmes de ton type. {E(PT)} le guide, une vingtaine de pages rien que pour toi.</p>
<p class="small">Tu ne connais pas ton type ? <a href="/quiz-type-de-cheveux/">Fais le quiz gratuit</a>, il te le dit en 2 minutes.</p></header>
<section aria-labelledby="h-choix"><h2 id="h-choix" class="sr">Choisis ton guide</h2><div class="gsel">{cartes}</div></section>
{pack}
<!-- TODO Clara : garantie « satisfait ou remboursé » à décider avant de l'afficher. Jamais de faux prix barré, de compte à rebours ni de stock. -->
{demo}
<div class="txt" style="margin-top:36px">
<section aria-labelledby="dedans"><h2 id="dedans">Ce que contient un guide par type</h2>
<ol class="eb-som"><li><strong>Ton profil</strong><span>Reconnaître ton type, et ce dont tes cheveux ont besoin.</span></li>
<li><strong>Lire une étiquette INCI</strong><span>La méthode en 30 secondes, et ce qu'il faut chercher pour ton type.</span></li>
<li><strong>Les gestes de base et ta routine semaine par semaine</strong><span>Un premier mois pas à pas, du jour de lavage aux jours sans lavage.</span></li>
<li><strong>3 produits par budget</strong><span>Petit, moyen, premium : des produits vendus en France, et comment les combiner.</span></li>
<li><strong>Les erreurs fréquentes et les problèmes de ton type</strong><span>Par exemple, pour les cheveux frisés : sécheresse, frisottis, nœuds, rétraction. Et quand consulter.</span></li>
<li><strong>Ton calendrier</strong><span>Ta semaine type, les saisons et une fiche de suivi.</span></li></ol></section>
{f'<section aria-labelledby="apercu"><h2 id="apercu">Un aperçu du guide complet (pack)</h2>{apercu}</section>' if apercu else ''}
<section aria-labelledby="sommaire"><h2 id="sommaire">Ce que contient le guide complet du pack</h2><ol class="eb-som">{som}</ol></section>
<section aria-labelledby="pourqui"><h2 id="pourqui">Pour qui, et pas pour qui</h2>
<div class="pourqui2"><div><h3>C'est pour toi si</h3><ul>
<li>Tu ne sais plus quoi acheter et tu veux une liste claire, classée selon <strong>ton</strong> type.</li>
<li>Tu veux une option petit budget à chaque étape, sans sacrifier la composition.</li>
<li>Tu as fait un de nos <a href="/tests-cheveux/">tests</a> et tu veux aller plus loin que trois produits.</li>
<li>Tu veux apprendre à lire une étiquette pour choisir seule ensuite.</li></ul></div>
<div><h3>Ce n'est pas pour toi si</h3><ul>
<li>Tu cherches une solution contre une chute importante, des plaques ou des démangeaisons qui durent : c'est le rôle d'un médecin.</li>
<li>Tu attends une promesse de pousse ou un produit miracle : tu ne la trouveras pas ici.</li>
<li>Tu as déjà une routine qui te convient : garde-la.</li></ul></div></div>
<p>Les guides gratuits du site restent complets : le PDF te fait surtout gagner du temps, tout est au même endroit.</p></section>
<section aria-labelledby="confiance"><h2 id="confiance">Comment la sélection est faite</h2>
<p>Chaque produit est retenu sur sa liste d'ingrédients (INCI), sur les besoins du type concerné et sur sa disponibilité en France. Les affirmations s'appuient sur des sources citées, comme la revue de <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4387693/" rel="noopener" target="_blank">Gavazzoni Dias sur les cosmétiques capillaires</a>. Un cosmétique ne soigne pas, ne fait pas pousser les cheveux et n'arrête pas une chute.</p></section>
<section aria-labelledby="faq"><h2 id="faq">Questions fréquentes</h2>{faq}</section>
<p style="text-align:center;margin-top:30px"><a class="btn" href="#h-choix">Revenir aux guides</a></p>
</div></div>
{JS_ACHAT}"""
    schema = [G["schema_crumbs"](crumbs),
              {"@context": "https://schema.org", "@type": "Product", "name": "Guides PDF des meilleurs produits pour ton type de cheveux", "brand": {"@type": "Brand", "name": G["SITE"]},
               "description": "Un guide PDF par type de cheveux (raides, fins, ondulés, bouclés, frisés, crépus) et un pack complet : routine, 3 produits par budget, lecture des étiquettes INCI, sources citées.",
               "image": DOMAIN + "/og.png",
               "offers": {"@type": "AggregateOffer", "lowPrice": f'{G["OFFRES"]["prix_type"]:.2f}', "highPrice": f'{G["OFFRES"]["prix_pack"]:.2f}', "priceCurrency": "EUR",
                          "offerCount": len(G["OFFRES"]["types"]) + 1, "availability": "https://schema.org/PreOrder", "url": DOMAIN + f"/{EB}/"}},
              {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in EBOOK_FAQ]}]
    return G["page"]("Guide PDF : les produits faits pour tes cheveux",
                     f"Un guide PDF par type de cheveux à {PT} : raides, fins, ondulés, bouclés, frisés ou crépus. Routine et 3 produits par budget. Pack tous types {PP}.",
                     f"/{EB}/", body, schema, "ebook", ("guide produits cheveux pdf (transactionnel)", "n.r."))


def guide_type(t):
    """Page de vente d'un guide par type : /guide/<slug>/. noindex seul, sans canonical (pas de page mince
    qui cannibalise les guides SEO gratuits), hors sitemap. Générée depuis ce gabarit pour les 6 types."""
    import os
    E, url = G["E"], G["url"]
    PT, PP, BUMP = G["PRIX_TYPE"], G["PRIX_PACK"], G["BUMP"]
    nom, tid = t["nom"], t["id"]
    path = G["url_guide"](tid)
    crumbs = [("Accueil", "/"), ("Le guide PDF", f"/{EB}/"), (f"Cheveux {nom}", path)]
    npages = nb_pages(os.path.join(G["ROOT"], "_guide", "types", f"guide-cheveux-{tid}.pdf"))
    taille = f"{npages} pages" if npages else "une vingtaine de pages"
    ap = [i for i in (1, 2) if os.path.exists(os.path.join(G["ROOT"], "_assets", f"guide-{tid}-apercu-{i}.webp"))]
    leg = ["La couverture", "La routine semaine par semaine"]
    apercu = ('<div class="eb-apercu ap2">' + "".join(
        f'<figure><img src="/images/guide-{tid}-apercu-{i}.webp" width="620" height="877" loading="lazy" decoding="async" alt="Aperçu du guide des cheveux {E(nom)} : {E(leg[i - 1].lower())}"><figcaption>{E(leg[i - 1])}</figcaption></figure>'
        for i in ap) + "</div>") if ap else ""
    probs = ", ".join(t["problemes"])
    if G["MODE_LANCEMENT"]:
        achat = f'<p>{G["BIENTOT"]}</p>\n<p class="small">Les ventes ouvrent très bientôt.</p>\n'
    else:
        achat = f"""<label class="renonce bump"><input type="checkbox" id="bump" data-href="{STRIPE_PACK}" data-txt="Acheter le guide et le pack complet, {E(PP)}"> <span><strong>Ajoute le pack complet pour {E(BUMP)} de plus</strong> : le guide complet (7 profils, tous les problèmes) et les 5 autres guides par type. Pratique si tes cheveux mélangent deux textures.</span></label><!-- TODO Stripe : order bump. Case cochée = lien du pack (STRIPE_PACK, 19 €, il contient ce guide) ; variante : vente croisée dans le Payment Link du guide -->
<label class="renonce"><input type="checkbox" id="renonce"> <span>{E(RENONCE)}</span></label>
<p><a class="btn btn-xl" id="acheter" href="{STRIPE[tid]}" aria-disabled="true">Acheter mon guide, {E(PT)}</a></p><!-- TODO Stripe : Payment Link du guide {E(nom)} (STRIPE["{tid}"]), redirection /merci/?p={tid}&s={{CHECKOUT_SESSION_ID}} -->
<p class="small">Paiement sécurisé par Stripe. Téléchargement juste après le paiement.</p>
"""
    demo = "" if G["MODE_LANCEMENT"] else '<aside class="attention" role="note"><p class="lab">Démo</p><p>Les ventes ne sont pas encore ouvertes : le bouton ne mène nulle part pour l\'instant.</p></aside>'
    retour = f'<a class="btn" href="/{EB}/">Voir tous les guides</a>' if G["MODE_LANCEMENT"] else '<a class="btn" href="#acheter">Revenir à l\'achat</a>'
    autres = " ".join(f'<a href="{G["url_guide"](x["id"])}">{E(x["Nom"])}</a>' for x in G["OFFRES"]["types"] if x["id"] != tid)
    body = f"""<div class="wrap">{G["crumbs_html"](crumbs)}
<div class="eb-head">
<div><p class="kicker">Guide PDF · Cheveux {E(nom)}</p>
<h1>Le guide des cheveux {E(nom)}</h1>
<p class="chapo">{E(t["accroche"])} Ta routine semaine par semaine, 3 produits par budget, les erreurs à éviter et les problèmes des cheveux {E(nom)}, au même endroit.</p>
<div class="eb-prix"><p class="prix">{E(PT)}<small> TTC</small></p></div>
{achat}
<ul class="eb-conf"><li>PDF de {E(taille)}, lisible sur téléphone</li><li>Une routine semaine par semaine pour ton premier mois</li><li>3 produits par budget, vendus en France</li><li>Sélection indépendante, sources citées, édition novembre 2026</li></ul>
</div>
<figure class="gt-vis">{visuel_type(t, sizes="(min-width:900px) 300px, 70vw")}</figure>
</div>
{demo}
<div class="txt" style="margin-top:36px">
{f'<section aria-labelledby="apercu"><h2 id="apercu">Un aperçu</h2>{apercu}</section>' if apercu else ''}
<section aria-labelledby="dedans"><h2 id="dedans">Ce que contient ton guide</h2><ol class="eb-som">
<li><strong>Ton profil : cheveux {E(nom)}</strong><span>Reconnaître ton type, et ce dont tes cheveux ont besoin.</span></li>
<li><strong>Lire une étiquette INCI</strong><span>La méthode en 30 secondes, et ce qu'il faut chercher pour des cheveux {E(nom)}.</span></li>
<li><strong>Les gestes de base</strong><span>Laver, nourrir, hydrater, coiffer, et les bons outils.</span></li>
<li><strong>Ta routine semaine par semaine</strong><span>Ton jour de lavage pas à pas, puis un premier mois en 4 semaines.</span></li>
<li><strong>Tes produits, 3 par budget</strong><span>Petit, moyen, premium, et comment les combiner selon ton budget.</span></li>
<li><strong>Les erreurs fréquentes</strong><span>Celles qui reviennent le plus souvent sur des cheveux {E(nom)}.</span></li>
<li><strong>Les problèmes des cheveux {E(nom)}</strong><span>{E(probs[0].upper() + probs[1:])}, et quand consulter.</span></li>
<li><strong>Ton calendrier</strong><span>Ta semaine type, les saisons et une fiche de suivi.</span></li></ol></section>
<section aria-labelledby="gratuit"><h2 id="gratuit">Le guide gratuit reste complet</h2>
<p>Tout l'essentiel sur tes cheveux est en accès libre dans <a href="{url(t["slug"])}">le guide des cheveux {E(nom)}</a>. Le PDF te fait gagner du temps : ta routine du premier mois, tes produits et tes problèmes, au même endroit, à garder sur ton téléphone.</p>
<p>Un cosmétique ne soigne pas, ne fait pas pousser les cheveux et n'arrête pas une chute. Pour des démangeaisons qui durent, des plaques ou une chute importante, consulte un médecin ou un dermatologue.</p></section>
<section aria-labelledby="autre"><h2 id="autre">Pas le bon type ?</h2>
<p class="mini-liens">{autres}</p><p><a href="/{EB}/">Voir tous les guides et le pack</a> ou <a href="/quiz-type-de-cheveux/">faire le quiz</a>.</p></section>
<p style="text-align:center;margin-top:30px">{retour}</p>
</div></div>
{JS_ACHAT}"""
    titre = f"Guide PDF cheveux {nom} : routine et produits"
    desc = (f"Le guide PDF des cheveux {nom} à {PT} : ta routine semaine par semaine, 3 produits par budget, les erreurs à éviter et les problèmes de ton type.")
    return G["page"](titre, desc, path, body, [G["schema_crumbs"](crumbs)], "ebook", None, noindex=True, canon=False)


def merci():
    """Après paiement Stripe : /merci/?p=<produit>&s={CHECKOUT_SESSION_ID}. noindex, hors sitemap, jamais liée depuis le site.
    Livre le bon PDF selon le produit : un guide par type, ou le pack (guide complet + 6 guides par type)."""
    E, json = G["E"], G["json"]
    prods = {t["id"]: {"nom": f"Le guide des cheveux {t['nom']}", "fichier": f"guide-cheveux-{t['id']}.pdf"} for t in G["OFFRES"]["types"]}
    prods["pack"] = {"nom": "Le guide complet (pack)", "fichier": G["OFFRES"]["pack"]["pdf"]}
    pack = ["pack"] + [t["id"] for t in G["OFFRES"]["types"]]  # TODO validation Louis : le pack livre le guide complet ET les 6 guides par type
    body = f"""<div class="wrap prose txt">
<h1>Merci pour ton achat</h1>
<div id="ok" hidden><p class="kicker">Paiement reçu</p><h2 id="ok-t">Ton guide est prêt</h2>
<ul class="dl-list" id="dl-list"></ul><!-- TODO livraison : GUIDE_DL (serveur de livraison qui vérifie la session Stripe et le produit acheté) -->
<p>Enregistre les fichiers sur ton téléphone ou ton ordinateur. Un reçu t'a été envoyé par e-mail. Un souci ? Écris à <a href="/contact/">l'adresse de contact</a> avec l'e-mail utilisé pour le paiement.</p>
<p class="small">Tu as demandé l'accès immédiat au guide et reconnu perdre ton droit de rétractation (article L221-28 13° du code de la consommation).</p>
<button class="btn btn-o" type="button" onclick="window.print()">Enregistrer cette confirmation</button></div>
<div id="ko"><h2>Cette page s'affiche après un achat</h2><p>Tu cherches un guide ? <a href="/{EB}/">Voir les guides PDF</a>.</p></div>
</div>
<script>
(function () {{
  // TODO livraison : VERIF_API vérifie que la session Stripe est payée, déduit le(s) produit(s) du Payment Link et renvoie
  // {{ok, t, produits}}. Le paramètre p de l'URL ne sert qu'à l'affichage en démo : seule la réponse du serveur fait foi.
  var API = {json.dumps(VERIF_API)}, DL = {json.dumps(GUIDE_DL)}, K = "cc-guide";
  var PRODUITS = {json.dumps(prods, ensure_ascii=False)}, PACK = {json.dumps(pack)};
  var q = new URLSearchParams(location.search), s = q.get("s") || "", p = q.get("p") || "pack";
  if (!/^cs_(live|test)_/.test(s)) return;
  function liste(achats) {{
    var f = [];
    achats.forEach(function (a) {{ (a === "pack" ? PACK : [a]).forEach(function (x) {{ if (PRODUITS[x] && f.indexOf(x) < 0) f.push(x); }}); }});
    return f;
  }}
  function ok(t, achats) {{
    try {{ localStorage.setItem(K, JSON.stringify({{ s: s, t: t, p: achats }})); }} catch (e) {{}}
    history.replaceState(null, "", "/merci/"); document.getElementById("ko").hidden = true; document.getElementById("ok").hidden = false;
    var f = liste(achats);
    if (f.length > 1) document.getElementById("ok-t").textContent = "Tes guides sont prêts";
    document.getElementById("dl-list").innerHTML = f.map(function (x) {{
      var href = DL && t ? DL + "?p=" + encodeURIComponent(x) + "&s=" + encodeURIComponent(s) + "&t=" + t : "#todo-telechargement-" + x;
      return '<li><a class="btn' + (x === f[0] ? " btn-xl" : " btn-o") + '" href="' + href + '" download="' + PRODUITS[x].fichier + '">Télécharger ' + PRODUITS[x].nom.replace(/^Le /, "le ") + "</a></li>";
    }}).join("");
  }}
  if (!API) {{ ok("", [PRODUITS[p] ? p : "pack"]); return; }} // démo : pas de serveur de vérification branché
  fetch(API + "?s=" + encodeURIComponent(s)).then(function (r) {{ return r.json(); }}).catch(function () {{ return {{ ok: false }}; }})
    .then(function (r) {{ if (r.ok) ok(r.t, r.produits || []); else document.getElementById("ko").innerHTML = "<h2>Paiement non retrouvé</h2><p>Si tu viens de payer, recharge la page dans une minute.</p>"; }});
}})();
</script>"""
    return G["page"]("Merci pour ton achat | Carnet capillaire",
                     "Page de téléchargement des guides PDF Carnet capillaire, affichée juste après le paiement. Elle n'est pas destinée aux moteurs de recherche.",
                     "/merci/", body, [], None, None, noindex=True)


def bienvenue():
    """Après le clic dans l'e-mail de confirmation (double opt-in Brevo : redirectionUrl). noindex, hors sitemap."""
    body = f"""<div class="wrap prose txt">
<p class="kicker">Inscription confirmée</p><h1>Bienvenue, ton mini-guide arrive</h1>
<p class="chapo">Merci d'avoir confirmé ton adresse. Le premier e-mail, avec ta routine et le mini-guide « Les 5 erreurs qui abîment tes cheveux », part dans quelques minutes.</p>
<p><a class="btn" href="/telechargements/mini-guide-5-erreurs.pdf">Lire le mini-guide tout de suite (PDF, 5 pages)</a></p><!-- Mini-guide gratuit : copié par build.py depuis _guide/mini-guide/ (le générer avant la mise en ligne) -->
<p>En attendant : <a href="/tests-cheveux/">refaire un test</a>, ou découvrir <a href="/{EB}/">le guide PDF de ton type de cheveux</a>.</p>
<p class="small">Tu peux te désinscrire à tout moment avec le lien en bas de chaque e-mail. <a href="/mentions-legales/#confidentialite">Ce que deviennent tes données</a></p>
</div>"""
    return G["page"]("Inscription confirmée | Carnet capillaire",
                     "Ton adresse est confirmée : le mini-guide gratuit des 5 erreurs qui abîment les cheveux arrive dans ta boîte mail dans quelques minutes.",
                     "/bienvenue/", body, [], None, None, noindex=True)


def simple(slug, title, desc, h1, html_body, kw, extra_schema=None, actif=None):
    crumbs = [("Accueil", "/"), (C(slug), G["url"](slug))]
    body = f'<div class="wrap">{G["crumbs_html"](crumbs)}<div class="prose txt"><h1>{G["E"](h1)}</h1>{html_body}</div></div>'
    return G["page"](title, desc, G["url"](slug), body, [G["schema_crumbs"](crumbs)] + (extra_schema or []), actif, kw)


CONTACT_EMAIL = None  # ex. "bonjour@carnetcapillaire.fr" quand la boîte existe


def contact():
    h = """<p class="chapo">Une question sur un guide, une erreur à signaler, une proposition de partenariat ? Écris-nous.</p>
<div class="contact-cards">
<!--EMAIL-->
<a class="lcard" href="/tests-cheveux/"><span class="k">Conseil</span><h3>Les tests gratuits</h3><p>Pour un avis sur tes cheveux, commence par un test : il répond en 2 minutes.</p></a></div>
<h2>Avant d'écrire</h2>
<ul><li>Aucun diagnostic n'est fait par message. Pour une question de cuir chevelu, de chute ou de démangeaisons, vois ton médecin ou un dermatologue.</li>
<li>Pour les marques : toute collaboration rémunérée ou tout produit offert est signalé « Publicité » ou « Collaboration commerciale », comme le prévoit la loi du 9 juin 2023. Aucune place dans les sélections ne s'achète.</li></ul>"""
    # TODO contact : renseigner CONTACT_EMAIL une fois la boîte créée sur le domaine (aucun lien mort en attendant)
    if CONTACT_EMAIL:
        carte = f'<a class="lcard" href="mailto:{CONTACT_EMAIL}"><span class="k">E-mail</span><h3>{CONTACT_EMAIL}</h3><p>Réponse en général sous quelques jours.</p></a>'
    else:
        carte = '<div class="lcard"><span class="k">E-mail</span><h3>Adresse en cours de création</h3><p>L\'adresse e-mail de contact sera ajoutée ici sous quelques jours.</p></div>'
    h = h.replace("<!--EMAIL-->", carte)
    return simple("contact", "Contact | Carnet capillaire",
                  "Pour écrire à Carnet capillaire : questions sur les guides, erreur à signaler ou partenariat. Aucun diagnostic par message, voici pourquoi.",
                  "Nous écrire", h, ("contact (navigation)", "n.r."))


def mentions():
    LCT = G["MODE_LANCEMENT"]
    etats = {
        "AFFIL_ETAT": " Aucun programme n'est actif pour l'instant : les liens vers les boutiques sont de simples liens, sans commission." if LCT else "",
        "VENTE_ETAT": "Les ventes ne sont pas encore ouvertes : les conditions générales de vente seront publiées avant la première vente." if LCT else
                      "Paiement par Stripe. Conditions générales de vente : <mark>TODO : CGV, identité de la vendeuse et médiateur de la consommation (article L612-1 du code de la consommation).</mark>",
        "PRESTA_ETAT": "Prestataire d'envoi : il sera indiqué ici à l'ouverture des inscriptions." if LCT else
                       "Prestataire d'envoi : <mark>TODO : Brevo (société française, données hébergées dans l'Union européenne), à confirmer avec le contrat de sous-traitance.</mark>",
        "MAIL_ETAT": " aucun formulaire d'inscription n'est ouvert pour l'instant. À l'ouverture," if LCT else "",
    }
    h = """<p class="chapo">Les informations légales du site, la façon dont il gagne de l'argent, et ce que deviennent tes données.</p>
<h2 id="editeur">Éditeur du site</h2>
<p>Site : Carnet capillaire, carnetcapillaire.fr.</p>
<p>Éditrice : en cours de création (micro-entreprise). Les informations légales (nom, statut, numéro SIRET, adresse de contact, directrice de la publication) seront ajoutées ici sous quelques jours.</p><!-- TODO : identité complète de l'éditrice dès l'immatriculation (loi pour la confiance dans l'économie numérique) -->
<h2 id="hebergeur">Hébergement</h2>
<p>GitHub Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis (service GitHub Pages).</p>
<h2 id="affiliation">Liens affiliés : comment le site gagne de l'argent</h2>
<p>Le site est gratuit. Pour le faire vivre, certaines pages et les résultats des tests contiennent des <strong>liens affiliés</strong> : si tu achètes un produit après avoir cliqué, la boutique verse une petite commission au site. Le prix reste le même pour toi.</p>
<ul><li>Programmes prévus : Lookfantastic, Notino, Les Secrets de Loly, Nocibé, Sephora, Amazon.{AFFIL_ETAT}</li>
<li>Chaque page qui contient ces liens l'annonce en haut, et les liens sont marqués pour les moteurs de recherche (attribut « sponsored »).</li>
<li>Une commission ne change pas les sélections, et une marque ne peut pas acheter une place.</li>
<li>Sur les réseaux, toute publication avec lien affilié, code promo ou produit offert porte la mention « Publicité » ou « Collaboration commerciale », conformément à la <a href="https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000047663185" rel="noopener" target="_blank">loi n° 2023-451 du 9 juin 2023</a>.</li></ul>
<p>Le site vend aussi des guides PDF : <a href="/guide-produits-cheveux-pdf/">un guide par type de cheveux et un pack complet</a>. {VENTE_ETAT}</p>
<h2 id="sante">Santé</h2>
<p>Les contenus de ce site sont des conseils de beauté, pas des conseils médicaux. Un cosmétique ne soigne pas (<a href="https://www.economie.gouv.fr/dgccrf/allegations-sur-les-produits-cosmetiques-tout-nest-pas-permis" rel="noopener" target="_blank">DGCCRF</a>). En cas de démangeaisons persistantes, de plaques, de rougeurs ou de chute importante, consulte ton médecin ou un dermatologue.</p>
<h2 id="avis">Avis et tests</h2>
<p>Aucun avis client n'est publié pour l'instant, aucun avis n'est acheté et aucune note n'est inventée. Les produits sont sélectionnés sur leur composition ; les tests en conditions réelles seront signalés et datés.</p>
<h2 id="confidentialite">Confidentialité</h2>
<ul><li><strong>Les tests</strong> fonctionnent entièrement dans ton navigateur : tes réponses ne sont ni envoyées ni enregistrées.</li>
<li><strong>Les e-mails (mini-guide, résultat d'un test)</strong> :{MAIL_ETAT} seulement si tu remplis le formulaire et coches la case. On collecte ton e-mail, ton prénom si tu le donnes, la page et le test d'où tu viens, et le résultat du test que tu as demandé. But : t'envoyer ce que tu as demandé, puis 5 e-mails de conseils sur 10 jours et une lettre de temps en temps, avec parfois des liens affiliés signalés. Base légale : ton consentement. Tu confirmes ton adresse par un e-mail (double opt-in) et tu peux te désinscrire en un clic dans chaque e-mail. Durée : jusqu'à ta désinscription, et au plus 3 ans après ton dernier clic ou ta dernière ouverture. Ces données ne sont jamais vendues ni louées. {PRESTA_ETAT} Tu peux demander l'accès, la rectification ou la suppression de tes données via la page <a href="/contact/">contact</a>, et saisir la <a href="https://www.cnil.fr/fr/plaintes" rel="noopener" target="_blank">CNIL</a>. Responsable du traitement : l'éditrice du site (voir plus haut).</li>
<li><strong>Stockage local</strong> : ton navigateur retient seulement que tu as fermé l'encart du mini-guide ou la barre du test, pour ne pas te les remontrer. Rien n'est envoyé.</li>
<li><strong>Aucun cookie</strong> publicitaire ni de mesure d'audience n'est déposé pour l'instant.</li><!-- TODO : si une mesure d'audience est ajoutée, choisir un outil sans cookie ou mettre en place un bandeau de consentement -->
<li><strong>Polices d'écriture</strong> : elles sont chargées depuis Google Fonts, ce qui transmet ton adresse IP à Google.</li><!-- TODO : héberger les polices sur le site -->
<li>Quand tu cliques sur un lien affilié, la boutique concernée peut déposer ses propres cookies, selon sa politique.</li>
<li>Pour toute question sur tes données : <a href="/contact/">contact</a>.</li></ul>
<h2 id="propriete">Propriété intellectuelle</h2>
<p>Les textes de ce site appartiennent à son éditeur. Les images d'illustration sont générées par intelligence artificielle. Merci de ne pas reproduire les contenus sans accord.</p>"""
    for k, v in etats.items():
        h = h.replace("{" + k + "}", v)
    return simple("mentions-legales", "Mentions légales, affiliation et confidentialité",
                  "Mentions légales de Carnet capillaire, fonctionnement des liens affiliés, avis, santé et confidentialité : les tests n'enregistrent aucune donnée.",
                  "Mentions légales, affiliation et confidentialité", h, ("mentions légales (obligatoire)", "n.r."))


def pages():
    init_offres()
    return [("/", accueil(), "1.0"), ("/tests-cheveux/", tests(), "0.9"), ("/quiz-type-de-cheveux/", quiz(), "0.9"), (f"/{EB}/", ebook(), "0.8"),
            ("/merci/", merci(), None), ("/bienvenue/", bienvenue(), None)] + [
            (G["url_guide"](t["id"]), guide_type(t), None) for t in G["OFFRES"]["types"]] + [
            ("/contact/", contact(), "0.3"), ("/mentions-legales/", mentions(), "0.2")]
