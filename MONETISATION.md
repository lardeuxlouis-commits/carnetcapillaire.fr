# Carnet capillaire : le plan de monétisation en 1 page

État au 22/11/2026 (guides par type ajoutés le 22/11) : tout est prêt dans le site en local, **rien n'est branché ni publié, aucun compte n'est créé**. Les comptes se créent au nom de la micro-entreprise de Clara (identité, SIRET et adresse attendus dans 2 jours).

## Les sources de revenus, par ordre de priorité

| # | Source | Où c'est dans le projet | Ce qui manque |
|---|---|---|---|
| 1 | **Liste e-mail** (capitalise les vues TikTok et Instagram) | Formulaire en fin des 4 tests, bloc et encart sur l'accueil (`_build/site.js`, `ENDPOINT`), pages `/bienvenue/`, mini-guide `_guide/mini-guide/`, séquence `_emails/sequence-bienvenue.md` | Compte Brevo, fonction serveur d'inscription, double opt-in, adresse postale dans les e-mails |
| 2 | **Guides PDF : 6 guides par type à 9 €, pack complet tous types à 19 €** | Prix et produits dans `_build/offres.json` (seul endroit). Sources hors dépôt : `_guide/types/guide-cheveux-<type>.md` (19 à 20 pages chacun) et `_guide/guide-produits-cheveux.md` (le pack, 30 pages). Export `python3 _build/guide_pdf.py --tout --apercus`. Sélecteur indexé `/guide-produits-cheveux-pdf/`, 6 pages de vente `/guide/cheveux-<type>/` (noindex, canonical vers le sélecteur, hors sitemap), `/merci/?p=<produit>` | 7 Payment Links Stripe, CGV, médiateur, serveur de livraison (`VERIF_API`, `GUIDE_DL`), tests produits par Clara, validation des prix par Louis |
| 3 | **Affiliation** | Tableaux comparatifs sur les 11 pages sélections, la sélection du mois (`/soins-cheveux/`) et les résultats des tests ; liste des liens `_affiliation/a-brancher.md` (102 identifiants) | Inscriptions aux programmes, puis `_affiliation/liens.json` |
| 4 | **TikTok Shop affilié** | Rien dans le site | Vérifier si le compte de Clara y a accès (conditions d'éligibilité fixées par TikTok, à vérifier dans l'appli) |
| 5 | **Partenariats marques** | Règles déjà écrites sur `/contact/` et `/mentions-legales/` | Un kit média (audience, prix) quand l'audience existe ; toujours « Publicité » ou « Collaboration commerciale » |

Ordre d'affiliation : Lookfantastic (Awin, environ 10 %), Notino (CJ, environ 12 %), Nocibé (environ 8 %), Sephora (environ 7 %, statut créatrice), Amazon Partenaires en dernier. Taux annoncés à vérifier au moment de l'inscription, ils changent.

## Ce que Clara doit créer (dans cet ordre)

1. **Stripe** (stripe.com, compte au nom de la micro-entreprise) : 7 produits et 7 Payment Links, acceptation des CGV obligatoire, reçus automatiques.
   - 6 guides « Le guide des cheveux <type> » (raides, fins, ondulés, bouclés, frisés, crépus), 9,00 € TTC, redirection `https://carnetcapillaire.fr/merci/?p=<type>&s={CHECKOUT_SESSION_ID}` (ids : `raides`, `fins`, `ondules`, `boucles`, `frises`, `crepus`).
   - « Pack complet tous types », 19,00 € TTC, redirection `https://carnetcapillaire.fr/merci/?p=pack&s={CHECKOUT_SESSION_ID}`. Le pack livre le guide complet et les 6 guides par type (TODO validation Louis).
   - Order bump : sur chaque page type, la case « Ajoute le pack complet pour 10 € de plus » bascule le bouton vers le lien du pack (19 €, il contient le guide du type). Variante : configurer une vente croisée du pack dans le Payment Link de chaque guide.
   - Puis remplacer les ancres factices `#stripe-guide-<type>` et `#stripe-pack` (`STRIPE`, `STRIPE_PACK` dans `_build/pages_speciales.py`).
   - Frais Stripe France pour une carte européenne standard : 1,5 % + 0,25 € par paiement (grille publique stripe.com/fr/pricing, à revérifier), soit environ 0,39 € sur 9 € et 0,54 € sur 19 €. En franchise de TVA : mention « TVA non applicable, art. 293 B du CGI ».
2. **Brevo** (brevo.com, gratuit jusqu'à 300 e-mails par jour) : authentifier le domaine (SPF, DKIM, DMARC), créer la liste et les attributs, le modèle de confirmation double opt-in (retour vers `/bienvenue/`), puis le scénario des 5 e-mails. Alternative : Kit (ex ConvertKit). Réglages détaillés en tête de `_emails/sequence-bienvenue.md`.
3. **Awin** (Lookfantastic), **CJ** (Notino), puis Nocibé, Sephora (programme créatrices), **Amazon Partenaires**. Les programmes demandent un site en ligne et des contenus : s'inscrire juste après la mise en ligne.
4. **TikTok Shop affilié** : vérifier dans l'appli si l'option est proposée au compte.
5. **Médiateur de la consommation** : obligatoire avant la première vente (article L612-1 du code de la consommation).

## Checklist de mise en route

- [ ] Identité de l'éditrice dans `/mentions-legales/` (éditrice, SIRET, adresse, directrice de la publication, hébergeur), dans le guide PDF (bloc « Éditrice ») et dans le pied des e-mails
- [ ] Domaine carnetcapillaire.fr acheté, adresse de contact créée (`/contact/`)
- [ ] Polices auto-hébergées (Google Fonts transmet l'IP, voir la confidentialité)
- [ ] Louis valide les prix (9 € par type, 19 € le pack) dans `_build/offres.json`, et la règle « le pack livre aussi les 6 guides par type »
- [ ] Clara teste les produits des guides et des sélections, corrige les prix et les fiches, retire le badge « À vérifier par Clara » produit par produit (guide complet ET guides par type : une correction dans le guide complet se propage aux sections reprises par `@inclure`), puis `python3 _build/guide_pdf.py --tout --apercus`
- [ ] Guides fins et raides : Fibralogy, Volumea et Phytovolume étaient en rupture chez Notino au 22/11, à vérifier ou remplacer
- [ ] Photos IA « cheveux fins » et « cheveux frisés » à générer (3:4, 480 et 900 px dans `_assets/`, champ `photo` de `offres.json`) : en attendant, les cartes affichent l'illustration de la texture
- [ ] CGV publiées, médiateur désigné, `STRIPE` et `STRIPE_PACK` renseignés dans `_build/pages_speciales.py`
- [ ] Serveur de livraison : 7 produits (6 types + pack) dans le modèle `~/Documents/paiements-sites/server.py` (clé restreinte du compte Stripe de Clara, 7 PDF hors de tout dépôt public). Le serveur déduit le produit du Payment Link (jamais du paramètre `p`) et renvoie `{ok, t, produits}` ; puis `VERIF_API` et `GUIDE_DL`
- [ ] Brevo : attribut `GUIDE_ACHETE`, et `fins` écrit dans `TYPE_CHEVEUX` quand le formulaire envoie `guide=fins` (e-mails J4 et J9)
- [ ] Achat test de bout en bout en mode test Stripe, puis un vrai achat remboursé
- [ ] Fonction serveur d'inscription Brevo (la clé API ne va jamais dans `site.js`), `ENDPOINT` renseigné, inscription test avec une vraie adresse, prévisualisation de chaque e-mail
- [ ] Mini-guide généré (`_guide/mini-guide/`), servi en `/telechargements/mini-guide-5-erreurs.pdf`
- [ ] Liens affiliés générés dans `_affiliation/liens.json`, chacun cliqué une fois
- [ ] Contenus : « Pink Paradise » de Les Secrets de Loly est un après-shampoing, encore présenté comme shampoing dans certaines pages (`contenu/*.json`) ; retirer les fiches en rupture listées dans `_affiliation/a-brancher.md`
- [ ] Rebuild, `python3 _build/verif.py` sans erreur, puis mise en ligne

## Règles qui ne bougent pas

Pas de faux avis, pas de faux compte à rebours, pas de faux stock, pas de prix barré inventé. Aucune promesse de soin ou de pousse. Liens affiliés toujours signalés, et « Publicité » sur les réseaux (loi n° 2023-451 du 9 juin 2023). Case de consentement jamais pré-cochée, désinscription en un clic.
