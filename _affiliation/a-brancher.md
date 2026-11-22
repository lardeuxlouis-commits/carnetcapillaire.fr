# Liens affiliés à brancher

Relevé du 22/11/2026, généré à partir du code du site (`contenu/*.json`, `_build/simulateurs.js`, pages de `site/`). **102 identifiants** de lien, tous FACTICES pour l'instant (`href="#affilie-<id>"`, `rel="sponsored nofollow"`). Rien n'est inscrit, aucun compte n'est créé.

Répartition : Notino 46, Amazon 26, Lookfantastic 13, Sephora 9, Greenweez 3, Atida 2, Nocibé 1, Les Secrets de Loly 1, Aroma-Zone 1.

Les guides PDF payants (6 guides par type + pack) ne contiennent aucun lien affilié : rien à brancher de ce côté. Les offres « Ton guide cheveux <type>, 9 € » des résultats de tests ne sont pas des liens affiliés.

## Mode d'emploi

1. Le préfixe de l'identifiant donne le marchand : `notino-klorane-galanga` = Notino, produit Klorane Galanga.
2. Une fois le programme validé, générer le lien suivi (Awin : « Link Builder » ; CJ : « Deep Link Generator » ; Amazon : barre SiteStripe) à partir de l'URL produit du tableau.
3. Coller le lien dans `_affiliation/liens.json`, sous la forme `{"notino-klorane-galanga": "https://www.awin1.com/cread.php?..."}`. **À faire côté build** : `build.py` lit ce fichier et remplace chaque `#affilie-<id>` par l'URL trouvée (dans les pages ET dans `simulateurs.js`), en gardant `rel="sponsored nofollow"` ; un id absent du fichier reste factice. Ainsi on branche les liens un par un, sans toucher aux contenus.
4. Rebuild, puis cliquer chaque lien branché (voir la checklist en bas).

**Règle de choix quand un produit a plusieurs marchands** : prendre celui qui l'a en stock, puis celui qui paie le mieux. Un lien vers une fiche en rupture ne rapporte rien.

## Alertes trouvées pendant le relevé

- ✅ Corrigé le 22/11 : Pink Paradise (après-shampoing) remplacé par Perfect Match (shampoing sans sulfate) dans les pages et le catalogue.
- Plusieurs fiches sont **en rupture ou retirées** chez le marchand prévu au 22/11/2026 (Fibralogy et Volumea chez Notino, Curbicia, Phytovolume, Olaplex N°3, Okara Color, Cantu Cleansing Cream chez Notino ; Bain Divalent et Moroccanoil chez Lookfantastic). Revérifier le jour du branchement.
- Doublons d'identifiants pour le même produit : `notino-klorane-avoine` / `notino-klorane-avoine-shampoing`, `notino-klorane-mangue-shampoing` / `notino-klorane-shampoing-mangue`, `notino-klorane-ortie-shampoing` / `notino-klorane-shampoing-ortie`. Un seul lien suivi suffit (même URL dans `liens.json` pour les deux), ou unifier les id dans le contenu.
- Les noms de produit changent : OGX « Ever Straightening » s'appelle aujourd'hui « Brazilian Keratin Smooth », Klorane « Centaurée » est remplacé par « Bleuet Organic » chez Notino. Vérifier l'INCI de la version actuelle.

## 1. Lookfantastic, via Awin (priorité 1)

- Inscription : créer un compte éditeur Awin (https://www.awin.com/fr/affilies), puis postuler au programme **LOOKFANTASTIC FR** (fiche annonceur : https://ui.awin.com/merchant-profile/7496).
- Conditions connues, à vérifier sur la fiche Awin : commission annoncée autour de 10 % (taux exact par catégorie dans l'onglet « Commission groups »), cookie de 30 jours, pas de commission sur la livraison ni les cartes cadeaux, seuls les codes promo fournis par le programme sont autorisés. Paiement par Awin (seuil de paiement à vérifier dans le compte, 20 € par défaut chez Awin).
- Points forts : Kérastase, Olaplex, Bouclème, Curlsmith, SheaMoisture, en stock et souvent en promo.

| id | Produit | Pages | URL produit | Remarques |
|---|---|---|---|---|
| `lookfantastic-boucleme-curl-cleanser` | Bouclème, Curl Cleanser | /meilleur-shampoing-cheveux-boucles/, /meilleur-shampoing-sans-sulfate/, /meilleur-shampoing/, /shampoing-cheveux-crepus-frises/, /soins-cheveux/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.lookfantastic.fr/p/boucleme-curl-cleanser-300ml/11352854/ | aussi relié à : Notino |
| `lookfantastic-curlsmith-conditioning-wash` | Curlsmith, Curl Quenching Conditioning Wash | /meilleur-shampoing-cheveux-boucles/, /shampoing-cheveux-crepus-frises/ | https://www.lookfantastic.fr/search?q=Curlsmith+Curl+Quenching+Conditioning+Wash (recherche, à confirmer) | aussi relié à : Notino |
| `lookfantastic-furterer-okara-color-shampooing` | René Furterer, Okara Color, shampooing protection couleur | /meilleur-shampoing/ | non vendu ici (introuvable sur Lookfantastic : garder Notino) | aussi relié à : Notino |
| `lookfantastic-kerastase-bain-divalent` | Kérastase, Spécifique, Bain Divalent | /meilleur-shampoing/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.lookfantastic.fr/p/kerastase-specifique-bain-divalent-shampoo-250ml/13193427/ | rupture de stock au 22/11; aussi relié à : Notino |
| `lookfantastic-kerastase-curl-manifesto-bain` | Kérastase, Curl Manifesto, Bain Hydratation Douceur | /meilleur-shampoing-cheveux-boucles/, /meilleur-shampoing-sans-sulfate/, /shampoing-cheveux-crepus-frises/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.lookfantastic.fr/p/kerastase-curl-manifesto-bain-hydratation-douceur-shampoo-250ml/12914400/ | aussi relié à : Notino, Sephora |
| `lookfantastic-kerastase-fluidealiste` | Kérastase, Discipline, Bain Fluidealiste | /shampoing-apres-lissage-bresilien/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.lookfantastic.fr/p/kerastase-discipline-bain-fluidealiste-250ml/10951818/ | version sans sulfates, rupture au 22/11 ; version classique : https://www.lookfantastic.fr/kerastase-discipline-bain-fluidealiste-250ml/10951817.html; aussi relié à : Notino |
| `lookfantastic-kerastase-nutritive-bain-satin` | Kérastase, Nutritive, Bain Satin | /cheveux-secs/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.lookfantastic.fr/p/kerastase-nutritive-bain-satin-hydrating-shampoo-for-dry-hair-250ml/14510090/ | formule actuelle ; Bain Satin 1 et 2 existent encore; aussi relié à : Sephora |
| `lookfantastic-loly-perfect-match` | Les Secrets de Loly, Perfect Match, shampoing | /meilleur-shampoing-cheveux-boucles/, /meilleur-shampoing-sans-sulfate/, /shampoing-cheveux-crepus-frises/ | non vendu ici (seul l'après-shampoing Pink Paradise est listé (en cadeau) : voir l'alerte en tête de fichier) |  |
| `lookfantastic-loreal-pro-absolut-repair-10-en-1` | L'Oréal Professionnel, Absolut Repair, soin sans rinçage 10-en-1 | /cheveux-abimes/ | https://www.lookfantastic.fr/p/l-oreal-professionnel-serie-expert-absolut-repair-10-in-1-leave-in-oil-for-dry-and-damaged-hair-90ml/13043378/ | c'est l'HUILE 10-en-1 ; le site parle d'un « soin sans rinçage », vérifier lequel est recommandé; aussi relié à : Notino |
| `lookfantastic-moroccanoil-smoothing` | Moroccanoil, Smoothing Shampoo | /shampoing-apres-lissage-bresilien/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.lookfantastic.fr/p/moroccanoil-smoothing-shampoo-conditioner-duo-2x500ml/11251691/ | seulement en duo 2 x 500 ml, rupture au 22/11; aussi relié à : Notino, Sephora |
| `lookfantastic-olaplex-n8` | Olaplex, N°8 Bond Intense Moisture Mask | /masque-cheveux/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.lookfantastic.fr/p/olaplex-no.-8-bond-intense-moisture-damage-repair-hair-mask-treatment-100ml/12882753/ | aussi relié à : Sephora |
| `lookfantastic-rene-furterer-curbicia` | René Furterer, Curbicia, shampooing purifiant légèreté | /cheveux-gras/ | non vendu ici (introuvable sur Lookfantastic : garder Notino) | aussi relié à : Notino |
| `lookfantastic-sheamoisture-coconut-hibiscus` | SheaMoisture, Coconut & Hibiscus Curl & Shine Shampoo | /meilleur-shampoing-sans-sulfate/, /shampoing-cheveux-crepus-frises/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.lookfantastic.fr/p/shea-moisture-coconut-hibiscus-curl-shine-shampoo-379ml/11309659/ | aussi relié à : Notino |

## 2. Notino, via CJ Affiliate (priorité 2)

- Inscription : page officielle https://www.notino.fr/programme-affiliation/ qui renvoie vers CJ Affiliate (https://www.cj.com/), compte éditeur puis candidature à l'annonceur Notino FR.
- Conditions connues, à vérifier : « jusqu'à 14 % » annoncé par Notino, environ 12 % selon le type de partenaire, bonus trimestriels possibles ; durée de cookie variable selon les sources (15 ou 30 jours). Seuil de paiement CJ à vérifier dans le compte (50 $ en virement selon les conditions CJ habituelles).
- Le plus gros catalogue du site (pharmacie, supermarché, Kérastase). Attention : Cattier et Curlsmith n'y ont pas été trouvés.

| id | Produit | Pages | URL produit | Remarques |
|---|---|---|---|---|
| `notino-boucleme-curl-cleanser` | Bouclème, Curl Cleanser | /meilleur-shampoing-cheveux-boucles/, /meilleur-shampoing-sans-sulfate/, /meilleur-shampoing/, /shampoing-cheveux-crepus-frises/ | https://www.notino.fr/boucleme/curl-cleanser-shampoing-nettoyant-et-nourrissant-pour-cheveux-boucles-et-frise/ | aussi relié à : Lookfantastic |
| `notino-cantu-cleansing-cream` | Cantu, Shea Butter Sulfate-Free Cleansing Cream Shampoo | /meilleur-shampoing-sans-sulfate/, /shampoing-cheveux-crepus-frises/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/cantu/shea-butter-cleansing-shampoo-shampoing-purifiant-pour-cheveux-boucles/ | rupture de stock au 22/11, format 709 g; aussi relié à : Amazon |
| `notino-cantu-deep-treatment-masque` | Cantu, Shea Butter Deep Treatment Masque | /masque-cheveux/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/search.asp?exps=Cantu+Shea+Butter+Deep+Treatment+Masque (recherche, à confirmer) | aussi relié à : Amazon |
| `notino-cattier-moelle-de-bambou` | Cattier, Shampooing Moelle de Bambou, cheveux secs | /cheveux-secs/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | non vendu ici (Cattier introuvable sur Notino : basculer sur Greenweez ou Amazon) | aussi relié à : Greenweez |
| `notino-cattier-shampooing-argile-verte` | Cattier, Shampooing Argile Verte, cuir chevelu gras | /cheveux-gras/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | non vendu ici (Cattier introuvable sur Notino : basculer sur Greenweez (https://www.greenweez.com/produit/shampoing-cuir-chevelu-gras-250ml, à confirmer que c'est bien l'argile verte) ou Amazon) | aussi relié à : Amazon |
| `notino-christophe-robin-aloe` | Christophe Robin, Shampoing hydratant à l'aloe vera | /meilleur-shampoing-sans-sulfate/, /shampoing-apres-lissage-bresilien/ | https://www.notino.fr/christophe-robin/hydrating-shampoo-with-aloe-vera-shampoing-hydratant-a-laloe-vera/ | aussi relié à : Sephora |
| `notino-curlsmith-conditioning-wash` | Curlsmith, Curl Quenching Conditioning Wash | /meilleur-shampoing-cheveux-boucles/, /shampoing-cheveux-crepus-frises/ | non vendu ici (Curlsmith introuvable sur Notino : garder Lookfantastic) | aussi relié à : Lookfantastic |
| `notino-ducray-sabal-shampooing` | Ducray, Sabal, shampooing séborégulateur | /cheveux-gras/, /meilleur-shampoing/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/ducray/sabal-shampoing-pour-cheveux-gras/ | aussi relié à : Amazon |
| `notino-ducray-sensinol-shampooing` | Ducray, Sensinol, shampooing physioprotecteur | /meilleur-shampoing/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/ducray/sensinol-shampoing-protecteur-et-apaisant-physiologique/ |  |
| `notino-ducray-squanorm` | Ducray, Squanorm, shampooing antipelliculaire | résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/ducray/squanorm-shampoing-anti-pellicules-grasses/ | version pellicules grasses ; chercher aussi la version pellicules sèches |
| `notino-elseve-argile-extraordinaire-shampoing` | L'Oréal Paris Elsève, Argile Extraordinaire, shampoing purifiant | /cheveux-gras/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/loreal-paris/elseve-extraordinary-clay-shampoing-purifiant-pour-cheveux-qui-deviennent-gras-tres-vite/ | aussi relié à : Amazon |
| `notino-elseve-color-vive-shampooing` | L'Oréal Paris, Elseve Color-Vive, shampooing | /meilleur-shampoing/ | https://www.notino.fr/loreal-paris/elseve-color-vive-shampoing-pour-cheveux-colores/ | aussi relié à : Amazon |
| `notino-elseve-color-vive-violet` | L'Oréal Paris Elseve, Color-Vive, shampooing violet déjaunisseur | /cheveux-blancs/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/loreal-paris/elseve-color-vive-purple-shampoing-neutralisant-les-reflets-jaunes/ | aussi relié à : Amazon |
| `notino-elseve-fibralogy-shampoing` | Elseve, Fibralogy, shampoing volume | /cheveux-fins/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/loreal-paris/elseve-fibralogy-shampoing-pour-des-cheveux-plus-epais/ | plus en vente sur Notino au 22/11 : vérifier si la gamme existe encore, sinon remplacer le produit; aussi relié à : Amazon |
| `notino-elseve-huile-extraordinaire-shampoing` | L'Oréal Paris Elsève, Huile Extraordinaire, shampoing nourrissant | /cheveux-secs/ | https://www.notino.fr/loreal-paris/elseve-extraordinary-oil-shampoing-nourrissant-pour-cheveux-secs-7065412/ | vérifier le format (une fiche est un lot avec recharge); aussi relié à : Amazon |
| `notino-elseve-total-repair-5-masque` | L'Oréal Paris, Elseve Total Repair 5, masque réparateur | /cheveux-abimes/, /masque-cheveux/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/loreal-paris/elseve-total-repair-5-masque-regenerant/ | aussi relié à : Amazon |
| `notino-furterer-okara-color-shampooing` | René Furterer, Okara Color, shampooing protection couleur | /meilleur-shampoing/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/rene-furterer/okara-color-shampoing-protecteur-de-cheveux/ | rupture de stock au 22/11; aussi relié à : Lookfantastic |
| `notino-garnier-hair-food-banane` | Garnier, Ultra Doux Hair Food Banane, masque 3 en 1 | /masque-cheveux/ | https://www.notino.fr/garnier/fructis-banana-hair-food-masque-nourrissant-pour-cheveux-secs/p-11632009/ | aussi relié à : Amazon |
| `notino-garnier-hair-food-papaye` | Garnier Fructis, Hair Food Papaye, masque 3-en-1 | /cheveux-abimes/ | https://www.notino.fr/garnier/fructis-papaya-hair-food-masque-renovateur-pour-cheveux-abimes/ | aussi relié à : Amazon |
| `notino-garnier-method-curls-shampoing` | Garnier, Fructis Method for Curls, shampoing | /meilleur-shampoing-cheveux-boucles/, /meilleur-shampoing-sans-sulfate/, /meilleur-shampoing/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/garnier/fructis-hydra-curls-shampoing-hydratant-pour-cheveux-boucles-et-frise/ | aussi relié à : Amazon |
| `notino-garnier-ultra-doux-avocat-karite` | Garnier Ultra Doux, Nutrition Profonde, avocat et karité | /cheveux-secs/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/search.asp?exps=Garnier+Ultra+Doux+Nutrition+Profonde%2C+avocat+et+karit%C3%A9 (recherche, à confirmer) | aussi relié à : Amazon |
| `notino-got2b-guardian-angel` | got2b (Schwarzkopf), Guardian Angel, spray protecteur thermique | /cheveux-abimes/, /soins-cheveux/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/got2b/guardian-angel-spray-de-definition-pour-cheveux-exposes-a-la-chaleur/ | aussi relié à : Amazon |
| `notino-kerastase-bain-divalent` | Kérastase, Spécifique, Bain Divalent | /meilleur-shampoing/ | https://www.notino.fr/kerastase/specifique-bain-divalent-shampoing-nettoyant-en-profondeur-pour-cuir-chevelu-gras/ | aussi relié à : Lookfantastic |
| `notino-kerastase-curl-manifesto-bain` | Kérastase, Curl Manifesto, Bain Hydratation Douceur | /meilleur-shampoing-cheveux-boucles/, /meilleur-shampoing-sans-sulfate/, /shampoing-cheveux-crepus-frises/ | https://www.notino.fr/kerastase/curl-manifesto-bain-hydratation-douceur-shampoing-nourrissant-pour-cheveux-boucles-et-frise/ | aussi relié à : Lookfantastic, Sephora |
| `notino-kerastase-fluidealiste` | Kérastase, Discipline, Bain Fluidealiste | /shampoing-apres-lissage-bresilien/ | https://www.notino.fr/kerastase/discipline-bain-lissant-pour-cheveux-indisciplines/ | aussi relié à : Lookfantastic |
| `notino-kerastase-masquintense` | Kérastase, Nutritive, Masquintense | /masque-cheveux/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/kerastase/nutritive-masquintense-masque-cheveux-regenerant/ | aussi relié à : Sephora |
| `notino-klorane-avoine` | Klorane, Shampoing au lait d'avoine | /shampoing-apres-lissage-bresilien/ | https://www.notino.fr/klorane/lait-davoine-shampooing-doux-pour-tous-types-de-cheveux/ | aussi relié à : Nocibé |
| `notino-klorane-avoine-shampoing` | Klorane, Shampoing extra-doux au lait d'avoine | /meilleur-shampoing/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/klorane/lait-davoine-shampooing-doux-pour-tous-types-de-cheveux/ | même produit que notino-klorane-avoine : un seul lien suffit; aussi relié à : Amazon |
| `notino-klorane-centauree` | Klorane, Shampoing déjaunissant à la centaurée bio | /cheveux-blancs/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/klorane/bleuet-organic-shampoing-anti-jaunissement/ | la fiche « Centaurée » est indisponible, celle-ci est la version bio actuelle (bleuet = centaurée); aussi relié à : Atida |
| `notino-klorane-galanga` | Klorane, Shampoing antipelliculaire au Galanga | résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/klorane/galanga-shampoing-hydratant-anti-pelliculaire/ |  |
| `notino-klorane-mangue-shampoing` | Klorane, Shampoing nutrition à la mangue | /meilleur-shampoing/ | https://www.notino.fr/klorane/mangue-shampoing-nourrissant-intense-pour-cheveux-secs/ |  |
| `notino-klorane-ortie-shampoing` | Klorane, Shampoing séboréducteur à l'ortie bio | /meilleur-shampoing/ | https://www.notino.fr/klorane/ortie-shampoing-purifiant-pour-cheveux-gras/ | aussi relié à : Amazon |
| `notino-klorane-shampoing-lin` | Klorane, Shampoing volume au lin | /cheveux-fins/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/klorane/lin-bio-shampoing-pour-cheveux-fins-et-plats/ | aussi relié à : Amazon |
| `notino-klorane-shampoing-mangue` | Klorane, Shampoing Nutrition à la Mangue | /cheveux-secs/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/klorane/mangue-shampoing-nourrissant-intense-pour-cheveux-secs/ | doublon de notino-klorane-mangue-shampoing; aussi relié à : Sephora |
| `notino-klorane-shampoing-ortie` | Klorane, Shampoing séboréducteur à l'Ortie BIO | /cheveux-gras/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/klorane/ortie-shampoing-purifiant-pour-cheveux-gras/ | doublon de notino-klorane-ortie-shampoing; aussi relié à : Sephora |
| `notino-klorane-shampoing-sec-lin` | Klorane, Shampoing sec volume au lin | /cheveux-fins/ | https://www.notino.fr/search.asp?exps=Klorane+Shampoing+sec+volume+au+lin (recherche, à confirmer) | aussi relié à : Amazon |
| `notino-laroche-kerium-doux-extreme` | La Roche-Posay, Kerium Doux Extrême, shampooing-gel physiologique | /meilleur-shampoing/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/la-roche-posay/kerium-shampoing-gel-physiologique-doux-pour-cheveux-normaux/ | nom « Doux Extrême » absent de la fiche : vérifier que c'est bien la même formule |
| `notino-loreal-pro-absolut-repair-10-en-1` | L'Oréal Professionnel, Absolut Repair, soin sans rinçage 10-en-1 | /cheveux-abimes/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/loreal-professionnel/serie-expert-absolut-repair-gold-quinoa-protein-spray-leger-et-multifonctionnel-pour-cheveux-abimes/ | spray 10 effets, rupture de stock au 22/11 ; il existe aussi une huile 10-en-1, choisir la bonne; aussi relié à : Lookfantastic |
| `notino-moroccanoil-smoothing` | Moroccanoil, Smoothing Shampoo | /shampoing-apres-lissage-bresilien/ | https://www.notino.fr/search.asp?exps=Moroccanoil+Smoothing+Shampoo (recherche, à confirmer) | aussi relié à : Lookfantastic, Sephora |
| `notino-ogx-brazilian-keratin` | OGX, Ever Straightening + Brazilian Keratin Therapy, shampoing | /shampoing-apres-lissage-bresilien/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/ogx/brazilian-keratin-smooth-shampooing-lissant-pour-des-cheveux-brillants-et-doux/ | nom actuel « Brazilian Keratin Smooth »; aussi relié à : Amazon |
| `notino-ogx-coconut-curls` | OGX, Coconut Curls, shampoing | /meilleur-shampoing-cheveux-boucles/ | https://www.notino.fr/ogx/coconut-curls-shampoing-pour-cheveux-boucles-et-frise/ | aussi relié à : Amazon |
| `notino-olaplex-n3` | Olaplex, N°3 Hair Perfector | /cheveux-abimes/ | https://www.notino.fr/olaplex/n3-hair-perfector-soin-traitant-pour-cheveux-abimes-et-fragiles/ | rupture de stock au 22/11; aussi relié à : Sephora |
| `notino-phyto-phytovolume-shampoing` | Phytovolume, shampoing volumateur | /cheveux-fins/ | https://www.notino.fr/phyto/phytovolume-shampoing-volume-pour-cheveux-fins-et-sans-volume/ | rupture de stock au 22/11; aussi relié à : Amazon |
| `notino-rene-furterer-curbicia` | René Furterer, Curbicia, shampooing purifiant légèreté | /cheveux-gras/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/rene-furterer/curbicia-shampoing-purifiant-pour-cheveux-gras/ | rupture de stock au 22/11; aussi relié à : Lookfantastic |
| `notino-rene-furterer-volumea-shampoing` | René Furterer, Volumea, shampoing expanseur | /cheveux-fins/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.notino.fr/rene-furterer/volumea-shampoing-pour-donner-du-volume/ | plus en vente sur Notino au 22/11; aussi relié à : Amazon |
| `notino-sheamoisture-coconut-hibiscus` | SheaMoisture, Coconut & Hibiscus Curl & Shine Shampoo | /meilleur-shampoing-sans-sulfate/, /shampoing-cheveux-crepus-frises/ | https://www.notino.fr/shea-moisture/coconut-hibiscus-shampoing-hydratant-pour-cheveux-boucles-et-frises/ | rupture de stock au 22/11 : Lookfantastic l'a en stock; aussi relié à : Lookfantastic |

## 3. Nocibé (priorité 3)

- Plateforme : Awin d'après les annuaires d'affiliation (fiche probable https://ui.awin.com/merchant-profile/122702, à vérifier dans le répertoire Awin en cherchant « Nocibé »).
- Conditions relevées (sources secondaires, à vérifier) : 8 % par vente, 4 % sur les ventes avec code promo affilié, cookie de 30 jours ; les produits « vendus et expédiés par un partenaire Nocibé » ne peuvent pas être promus.
- Un seul produit branché pour l'instant. Klorane, Ducray, La Roche-Posay et Kérastase y sont aussi vendus : Nocibé peut servir de marchand de secours.

| id | Produit | Pages | URL produit | Remarques |
|---|---|---|---|---|
| `nocibe-klorane-avoine` | Klorane, Shampoing au lait d'avoine | /shampoing-apres-lissage-bresilien/ | https://www.nocibe.fr/klorane-avoine-shampoing-extra-doux-au-lait-d-avoine-usage-frequent-shampoing-s284772 | aussi relié à : Notino |

## 4. Sephora (priorité 4, statut créatrice)

- Programme affilié Sephora France sur Awin (rechercher « Sephora FR » dans le répertoire Awin) ; la piste « créatrice » (programme influence) se demande à part, avec le compte Instagram ou TikTok de Carnet capillaire. Taux annoncé dans le brief : 7 % ; les sources trouvées donnent une fourchette de 2,5 à 10 % selon la catégorie, cookie de 30 jours. À vérifier à l'inscription.
- Utile pour Kérastase, Olaplex, Christophe Robin, Klorane, et pour Les Secrets de Loly (vendu chez Sephora).

| id | Produit | Pages | URL produit | Remarques |
|---|---|---|---|---|
| `sephora-christophe-robin-aloe` | Christophe Robin, Shampoing hydratant à l'aloe vera | /meilleur-shampoing-sans-sulfate/, /shampoing-apres-lissage-bresilien/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.sephora.fr/p/shampooing-hydratant-a-l-aloe-vera-P10017822.html | aussi relié à : Notino |
| `sephora-kerastase-curl-manifesto-bain` | Kérastase, Curl Manifesto, Bain Hydratation Douceur | /meilleur-shampoing-cheveux-boucles/, /meilleur-shampoing-sans-sulfate/, /shampoing-cheveux-crepus-frises/ | https://www.sephora.fr/KERAS-BrandUniverse-18.html | page de gamme : fiche du shampoing à prendre dans la gamme Curl Manifesto; aussi relié à : Lookfantastic, Notino |
| `sephora-kerastase-masquintense` | Kérastase, Nutritive, Masquintense | /masque-cheveux/ | https://www.sephora.fr/p/nutritive---masquintense-P10050797.html | aussi relié à : Notino |
| `sephora-kerastase-nutritive-bain-satin` | Kérastase, Nutritive, Bain Satin | /cheveux-secs/ | https://www.sephora.fr/p/nutritive----bain-satin-P10050792.html | aussi relié à : Lookfantastic |
| `sephora-klorane-shampoing-mangue` | Klorane, Shampoing Nutrition à la Mangue | /cheveux-secs/ | https://www.sephora.fr/p/shampoing-nutrition-a-la-mangue---cheveux-secs-P10026548.html | aussi relié à : Notino |
| `sephora-klorane-shampoing-ortie` | Klorane, Shampoing séboréducteur à l'Ortie BIO | /cheveux-gras/ | https://www.sephora.fr/p/shampoing-seboreducteur-a-l-ortie-bio---cheveux-gras-P10026553.html | aussi relié à : Notino |
| `sephora-moroccanoil-smoothing` | Moroccanoil, Smoothing Shampoo | /shampoing-apres-lissage-bresilien/ | non vendu ici (pas de Smoothing Shampoo trouvé chez Sephora (seulement Frizz Control Shampoo) : basculer sur Notino ou Lookfantastic) | aussi relié à : Lookfantastic, Notino |
| `sephora-olaplex-n3` | Olaplex, N°3 Hair Perfector | /cheveux-abimes/ | https://www.sephora.fr/p/olaplex-no.-3-hair-perfector-353189.html | aussi relié à : Notino |
| `sephora-olaplex-n8` | Olaplex, N°8 Bond Intense Moisture Mask | /masque-cheveux/ | https://www.sephora.fr/p/no.-8-masque-hydratant-bond-intense---masque-soin-cheveux-P10014907.html | aussi relié à : Lookfantastic |

## 5. Les Secrets de Loly (programme de la marque)

- La marque a un programme d'affiliation, apparemment sur Awin (à confirmer en cherchant « Les Secrets de Loly » dans le répertoire Awin), et un parrainage client (5 € offerts au filleul) qui n'est PAS de l'affiliation : ne pas mélanger les deux.
- Conditions : non publiées, à demander à la marque. Site : https://www.secretsdeloly.com/.
- Voir l'alerte « Pink Paradise » plus haut avant de brancher.

| id | Produit | Pages | URL produit | Remarques |
|---|---|---|---|---|
| `loly-perfect-match` | Les Secrets de Loly, Perfect Match | /meilleur-shampoing-cheveux-boucles/, /meilleur-shampoing-sans-sulfate/, /meilleur-shampoing/, /shampoing-cheveux-crepus-frises/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.secretsdeloly.com/products/pink-paradise-apres-shampooing | fiche de l'APRÈS-SHAMPOING (voir l'alerte en tête de fichier) ; URL vue en version /en/, vérifier la version française |

## 6. Autres marchands déjà cités dans le contenu (Greenweez, Atida, Aroma-Zone)

- Atida : les liens trouvés portent un paramètre `awc=24087_...`, signe d'un programme Awin (annonceur 24087 probable, à vérifier).
- Greenweez et Aroma-Zone : programme à chercher dans le répertoire Awin ou à demander au service partenariats. Aroma-Zone n'est pas vendu sur Amazon : garder le lien direct.

| id | Produit | Pages | URL produit | Remarques |
|---|---|---|---|---|
| `aromazone-henne-egypte` | Aroma-Zone, Henné d'Égypte, poudre | /cheveux-blancs/ | https://www.aroma-zone.com/product/egyptian-henna-natural-hair-dye | URL vue en version /en/ ; prendre la version française |
| `atida-couleurs-de-jeanne` | Les Couleurs de Jeanne, Coloration 100 % végétale | /cheveux-blancs/ | https://www.atida.fr/les-couleurs-de-jeanne-coloration-vegetale-chatain-100g-9800110.html | une fiche par teinte (ici châtain), choisir la teinte mise en avant; aussi relié à : Greenweez |
| `atida-klorane-centauree` | Klorane, Shampoing déjaunissant à la centaurée bio | /cheveux-blancs/ | https://www.atida.fr/klorane-centauree-bio-shampooing-dejaunissant-400ml.html | aussi relié à : Notino |
| `greenweez-cattier-moelle-de-bambou` | Cattier, Shampooing Moelle de Bambou, cheveux secs | /cheveux-secs/ | https://www.greenweez.com/produit/shampoing-bambou-cheveux-secs-250ml | aussi relié à : Notino |
| `greenweez-couleurs-de-jeanne` | Les Couleurs de Jeanne, Coloration 100 % végétale | /cheveux-blancs/ | https://www.greenweez.com/marque/les-couleurs-de-jeanne | page marque : une fiche par teinte; aussi relié à : Atida |
| `greenweez-khadi-coloration-vegetale` | Khadi, Coloration végétale et henné pur | /cheveux-blancs/ | https://www.greenweez.com/recherche?q=Khadi+Coloration+v%C3%A9g%C3%A9tale+et+henn%C3%A9+pur (recherche, à confirmer) | aussi relié à : Amazon |

## 7. Amazon Partenaires (en dernier)

- Inscription : https://partenaires.amazon.fr/ (il faut 3 ventes qualifiées dans les 180 jours pour que le compte soit validé).
- Conditions relevées : 6 % en Beauté et Beauté de luxe depuis juin 2025 (à vérifier dans le barème en vigueur), cookie de 24 heures seulement, seuil de paiement 25 € par virement (10 € en carte cadeau), paiement environ 60 jours après la fin du mois.
- À utiliser seulement quand le produit n'est pas chez un marchand mieux payé (Cantu, Head & Shoulders, Khadi, gros formats de supermarché). Beaucoup de fiches sont tenues par des vendeurs tiers à prix gonflé : choisir une fiche « Expédié et vendu par Amazon ». Les liens `amazon.fr/dp/<ASIN>` ci-dessous sont la forme courte des fiches trouvées.

| id | Produit | Pages | URL produit | Remarques |
|---|---|---|---|---|
| `amazon-aromazone-henne-egypte` | Aroma-Zone, Henné d'Égypte, poudre | /cheveux-blancs/ | non vendu ici (Aroma-Zone n'a pas été trouvé sur Amazon : garder le lien Aroma-Zone direct) |  |
| `amazon-cantu-cleansing-cream` | Cantu, Shea Butter Sulfate-Free Cleansing Cream Shampoo | /meilleur-shampoing-sans-sulfate/, /shampoing-cheveux-crepus-frises/ | https://www.amazon.fr/dp/B01LTIAU9W | aussi relié à : Notino |
| `amazon-cantu-deep-treatment-masque` | Cantu, Shea Butter Deep Treatment Masque | /masque-cheveux/ | https://www.amazon.fr/dp/B00MH90U2K | vendeur tiers, vérifier le vendeur et l'emballage; aussi relié à : Notino |
| `amazon-cattier-shampooing-argile-verte` | Cattier, Shampooing Argile Verte, cuir chevelu gras | /cheveux-gras/ | https://www.amazon.fr/s?k=Cattier+Shampooing+Argile+Verte%2C+cuir+chevelu+gras (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-ducray-sabal-shampooing` | Ducray, Sabal, shampooing séborégulateur | /cheveux-gras/ | https://www.amazon.fr/s?k=Ducray+Sabal%2C+shampooing+s%C3%A9bor%C3%A9gulateur (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-elseve-argile-extraordinaire-shampoing` | L'Oréal Paris Elsève, Argile Extraordinaire, shampoing purifiant | /cheveux-gras/ | https://www.amazon.fr/s?k=L%27Or%C3%A9al+Paris+Els%C3%A8ve+Argile+Extraordinaire%2C+shampoing+purifiant (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-elseve-color-vive-shampooing` | L'Oréal Paris, Elseve Color-Vive, shampooing | /meilleur-shampoing/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.amazon.fr/s?k=L%27Or%C3%A9al+Paris+Elseve+Color-Vive%2C+shampooing (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-elseve-color-vive-violet` | L'Oréal Paris Elseve, Color-Vive, shampooing violet déjaunisseur | /cheveux-blancs/ | https://www.amazon.fr/s?k=L%27Or%C3%A9al+Paris+Elseve+Color-Vive%2C+shampooing+violet+d%C3%A9jaunisseur (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-elseve-fibralogy-shampoing` | Elseve, Fibralogy, shampoing volume | /cheveux-fins/ | https://www.amazon.fr/s?k=Elseve+Fibralogy%2C+shampoing+volume (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-elseve-huile-extraordinaire-shampoing` | L'Oréal Paris Elsève, Huile Extraordinaire, shampoing nourrissant | /cheveux-secs/ | https://www.amazon.fr/s?k=L%27Or%C3%A9al+Paris+Els%C3%A8ve+Huile+Extraordinaire%2C+shampoing+nourrissant (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-elseve-total-repair-5-masque` | L'Oréal Paris, Elseve Total Repair 5, masque réparateur | /cheveux-abimes/, /masque-cheveux/ | https://www.amazon.fr/s?k=L%27Or%C3%A9al+Paris+Elseve+Total+Repair+5%2C+masque+r%C3%A9parateur (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-garnier-hair-food-banane` | Garnier, Ultra Doux Hair Food Banane, masque 3 en 1 | /masque-cheveux/, /soins-cheveux/, résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.amazon.fr/dp/B07KD4CGZM | aussi relié à : Notino |
| `amazon-garnier-hair-food-papaye` | Garnier Fructis, Hair Food Papaye, masque 3-en-1 | /cheveux-abimes/ | https://www.amazon.fr/s?k=Garnier+Fructis+Hair+Food+Papaye%2C+masque+3-en-1 (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-garnier-method-curls-shampoing` | Garnier, Fructis Method for Curls, shampoing | /meilleur-shampoing-cheveux-boucles/, /meilleur-shampoing-sans-sulfate/, /meilleur-shampoing/ | https://www.amazon.fr/dp/B0CPT6H8PQ | aussi relié à : Notino |
| `amazon-garnier-ultra-doux-avocat-karite` | Garnier Ultra Doux, Nutrition Profonde, avocat et karité | /cheveux-secs/ | https://www.amazon.fr/s?k=Garnier+Ultra+Doux+Nutrition+Profonde%2C+avocat+et+karit%C3%A9 (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-got2b-guardian-angel` | got2b (Schwarzkopf), Guardian Angel, spray protecteur thermique | /cheveux-abimes/ | https://www.amazon.fr/dp/B07P3DPQJ3 | aussi relié à : Notino |
| `amazon-head-shoulders-classic` | Head & Shoulders, Classique, shampooing antipelliculaire | résultats des simulateurs (shampoing, cuir chevelu, routine) et du quiz | https://www.amazon.fr/dp/B01J3UIVW6 |  |
| `amazon-khadi-coloration-vegetale` | Khadi, Coloration végétale et henné pur | /cheveux-blancs/ | https://www.amazon.fr/dp/B003TNIWPU | henné pur ; d'autres teintes Khadi existent; aussi relié à : Greenweez |
| `amazon-klorane-avoine-shampoing` | Klorane, Shampoing extra-doux au lait d'avoine | /meilleur-shampoing/ | https://www.amazon.fr/s?k=Klorane+Shampoing+extra-doux+au+lait+d%27avoine (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-klorane-ortie-shampoing` | Klorane, Shampoing séboréducteur à l'ortie bio | /meilleur-shampoing/ | https://www.amazon.fr/s?k=Klorane+Shampoing+s%C3%A9bor%C3%A9ducteur+%C3%A0+l%27ortie+bio (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-klorane-shampoing-lin` | Klorane, Shampoing volume au lin | /cheveux-fins/ | https://www.amazon.fr/s?k=Klorane+Shampoing+volume+au+lin (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-klorane-shampoing-sec-lin` | Klorane, Shampoing sec volume au lin | /cheveux-fins/ | https://www.amazon.fr/s?k=Klorane+Shampoing+sec+volume+au+lin (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-ogx-brazilian-keratin` | OGX, Ever Straightening + Brazilian Keratin Therapy, shampoing | /shampoing-apres-lissage-bresilien/ | https://www.amazon.fr/s?k=OGX+Ever+Straightening+%2B+Brazilian+Keratin+Therapy%2C+shampoing (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-ogx-coconut-curls` | OGX, Coconut Curls, shampoing | /meilleur-shampoing-cheveux-boucles/ | https://www.amazon.fr/dp/B0128QI49C | vendeur tiers à prix élevé, vérifier; aussi relié à : Notino |
| `amazon-phyto-phytovolume-shampoing` | Phytovolume, shampoing volumateur | /cheveux-fins/ | https://www.amazon.fr/s?k=Phyto+Phytovolume%2C+shampoing+volumateur (recherche, à confirmer) | aussi relié à : Notino |
| `amazon-rene-furterer-volumea-shampoing` | René Furterer, Volumea, shampoing expanseur | /cheveux-fins/ | https://www.amazon.fr/s?k=Ren%C3%A9+Furterer+Volumea%2C+shampoing+expanseur (recherche, à confirmer) | aussi relié à : Notino |

## Checklist de mise en route

- [ ] Corriger d'abord le contenu signalé dans les alertes (Pink Paradise, doublons d'id, noms de gammes changés).
- [ ] Créer le compte éditeur Awin au nom de Clara (micro-entreprise : SIRET, IBAN, adresse), avec l'URL du site en ligne et une page « affiliation » visible (déjà dans `/mentions-legales/#affiliation`).
- [ ] Postuler à Lookfantastic FR, puis Nocibé, Sephora FR, Les Secrets de Loly, Atida sur Awin.
- [ ] Créer le compte CJ et postuler à Notino FR.
- [ ] En dernier, créer le compte Amazon Partenaires (le compteur de 180 jours démarre à l'inscription).
- [ ] Attendre la validation de chaque annonceur avant de générer un lien (un lien d'un programme non validé ne rémunère pas).
- [ ] Générer chaque lien suivi à partir de l'URL du tableau, vérifier que la fiche est en stock, et le coller dans `_affiliation/liens.json`.
- [ ] Rebuild, puis cliquer chaque lien branché : il doit arriver sur la bonne fiche, le bon format, avec le paramètre de suivi du réseau ; vérifier dans le tableau de bord du réseau que le clic est compté.
- [ ] Revérifier les URL une fois par trimestre (ruptures, gammes renommées) ; un lien cassé ou en rupture se remplace par le marchand suivant du tableau.
- [ ] Sur Instagram et TikTok, toute publication avec lien affilié, code promo ou produit offert porte la mention « Publicité » ou « Collaboration commerciale », claire et visible, conformément à la loi n° 2023-451 du 9 juin 2023 ; un lien affilié en bio ou en story s'annonce aussi.
- [ ] Déclarer les commissions dans le chiffre d'affaires de la micro-entreprise.

## Produits cités seulement dans le guide PDF (pas encore de lien sur le site)

Le guide payant cite aussi ces produits. Ils n'ont pas d'identifiant `#affilie-` pour l'instant : un lien affilié dans un PDF vendu n'est utile que si le PDF est mis à jour quand le lien change. À décider par Clara ; sinon, les ajouter au site (tableaux comparatifs) avec un identifiant au même format.

| Produit | Programme conseillé | URL produit |
|---|---|---|
| Aroma-Zone, Gel d'aloe vera BIO | Aroma-Zone (programme à vérifier) | à confirmer, recherche sur aroma-zone.com |
| Aroma-Zone, Beurre de karité BIO | Aroma-Zone (programme à vérifier) | à confirmer, recherche sur aroma-zone.com |
| Bouclème, Curl Cream | Lookfantastic (Awin) | à confirmer, recherche sur lookfantastic.fr |
| Bouclème, Curl Defining Gel | Lookfantastic (Awin) | à confirmer, recherche sur lookfantastic.fr |
| Kérastase, Curl Manifesto Crème de Jour Fondamentale | Lookfantastic (Awin) | à confirmer, recherche sur lookfantastic.fr |
| Cantu, Coconut Curling Cream | Notino (CJ) | à confirmer, recherche sur notino.fr |
| Cantu, Shea Butter Leave-In Conditioning Repair Cream | Notino (CJ) | à confirmer, recherche sur notino.fr |
| SheaMoisture, Coconut & Hibiscus Curl Enhancing Smoothie | Lookfantastic (Awin) | à confirmer, recherche sur lookfantastic.fr |
| Moroccanoil, Treatment (huile) | Lookfantastic (Awin) ou Sephora | à confirmer, recherche sur lookfantastic.fr |

## Branchement technique (fait le 22/11/2026)

`build.py` lit `_affiliation/liens.json` s'il existe : `{"notino-cattier-shampooing-argile-verte": "https://...lien-tracké...", ...}`. Chaque `href="#affilie-<id>"` des pages est alors remplacé par l'URL, et les simulateurs reçoivent la même table (`window.CC_LIENS`). Seules les URL en `https://` sont prises. Les liens gardent `rel="sponsored nofollow"`. Rebuild puis `python3 _build/verif.py`.
