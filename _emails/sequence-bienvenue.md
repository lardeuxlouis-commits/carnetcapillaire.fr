# Séquence de bienvenue Carnet capillaire (5 e-mails, J0 à J9)

Prix des guides : 9 € par type, 19 € le pack complet tous types. Ils viennent de `_build/offres.json` (seul endroit côté site) : si Louis les change, mettre à jour les e-mails J4 et J9 à la main (TODO validation Louis).

Prête à coller dans Brevo. Rien n'est créé : ni compte Brevo, ni liste, ni domaine d'envoi.

TODO Clara : confirmer la signature « Clara, Carnet capillaire » (prénom affiché ou signature de marque seule).
TODO Clara : adresse postale de l'éditrice (micro-entreprise) dans le pied de page. Elle est obligatoire dans tout e-mail commercial : ne rien inventer, la compléter dans 2 jours avec les mentions légales.
TODO Clara : relire chaque phrase écrite à la première personne et l'adapter à ton expérience réelle (« j'ai testé », « chez moi ») : ne garder que ce qui est vrai.

## 0. Réglages Brevo

### Compte et domaine
- Compte Brevo gratuit (300 e-mails par jour sur l'offre gratuite ; plafond de contacts et conditions à revérifier sur brevo.com/fr/pricing avant de s'inscrire).
- Expéditeur : `clara@carnetcapillaire.fr` ou `bonjour@carnetcapillaire.fr` (TODO : domaine non acheté, adresse à créer). Ne jamais envoyer depuis une adresse Gmail : Gmail et Yahoo exigent un domaine authentifié.
- Authentifier le domaine dans Brevo : enregistrements DKIM, SPF (`include:spf.brevo.com`) et DMARC (au minimum `v=DMARC1; p=none; rua=mailto:...`).

### Liste et attributs à créer
Liste : « Carnet capillaire, inscrites site » (une seule liste ; segmenter par attribut).

| Attribut | Type | Rempli par | Exemple |
|---|---|---|---|
| `PRENOM` | Texte | champ facultatif du formulaire | Léa |
| `TEST` | Catégorie | champ caché du formulaire | `quiz`, `shampoing`, `cuir`, `routine`, `accueil` |
| `TYPE_CHEVEUX` | Texte | champ caché, résultat du quiz | `bouclés (3B)`, `raides`, `crépus (4C)` |
| `PROFIL_CUIR` | Catégorie | champ caché | `gras`, `sec`, `sensible`, `pellicules`, `equilibre` |
| `RESULTAT` | Texte | champ caché, phrase de résultat | `un shampoing doux, sans sulfate` |
| `CONSENTEMENT_DATE` | Date | automatique à la confirmation | 2026-11-24 |
| `SOURCE_PAGE` | Texte | champ caché, URL de la page | `/meilleur-shampoing/` |
| `ACHAT_GUIDE` | Booléen | à mettre à jour après un achat Stripe (manuel ou via Zapier/Make) | oui / non |
| `GUIDE_ACHETE` | Texte | idem, produit acheté | `boucles`, `pack` |

`TYPE_CHEVEUX` commence par le nom de la texture (`raides`, `ondulés`, `bouclés`, `frisés`, `crépus`). Le formulaire envoie aussi le champ `guide` (id du guide proposé dans le résultat : `raides`, `fins`, `ondules`, `boucles`, `frises`, `crepus`, vide si inconnu). TODO serveur : quand `guide` vaut `fins`, écrire `fins` dans `TYPE_CHEVEUX` (ex. `raides fins (1A)`). Dans les conditions des e-mails J4 et J9, le test « fins » est donc placé avant « raides ».

Si l'attribut est vide, chaque e-mail prévoit un texte par défaut (syntaxe `| default:`). Conditions écrites dans la syntaxe des modèles Brevo (`{% if %}`, `{% elif %}`, opérateur `in`) : vérifier l'aperçu de chaque branche avec un contact de test avant d'activer le scénario.

### Double opt-in (obligatoire dans ce projet)
- Formulaire Brevo, ou appel API `POST /v3/contacts/doubleOptinConfirmation` depuis le petit serveur qui remplacera l'endpoint factice du site (TODO).
- Paramètres de l'appel : `email`, `attributes`, `includeListIds: [ID de la liste]`, `templateId: [ID du modèle de confirmation ci-dessous]`, `redirectionUrl: https://carnetcapillaire.fr/inscription-confirmee/` (TODO : page à créer).
- Le contact n'entre dans la liste, et ne reçoit la séquence, qu'après le clic de confirmation.
- Conserver la preuve du consentement : date, page, texte de la case cochée (Brevo garde la date et l'IP de confirmation).
- Le texte de la case du formulaire du site, non pré-cochée : « J'accepte de recevoir ma routine, le mini-guide gratuit et les e-mails de Carnet capillaire (conseils, sélections avec liens affiliés, offres du guide PDF). Désinscription en un clic dans chaque e-mail. » + lien vers la politique de confidentialité.

### Automatisation
Scénario Brevo « Bienvenue » : déclencheur « Contact ajouté à la liste » (donc après confirmation).

| E-mail | Délai | Condition |
|---|---|---|
| E-mail 1, J0 | immédiat | aucune |
| E-mail 2, J2 | attendre 2 jours | aucune |
| E-mail 3, J4 | attendre 2 jours | aucune |
| E-mail 4, J6 | attendre 2 jours | aucune |
| E-mail 5, J9 | attendre 3 jours | `ACHAT_GUIDE` différent de oui (sinon sortie du scénario) |

- Heure d'envoi conseillée pour J2 à J9 : entre 18 h et 20 h (lecture sur téléphone après le travail). À ajuster selon les statistiques d'ouverture.
- Test A/B : Brevo ne propose le test A/B d'objet que sur les campagnes, pas dans un scénario sur l'offre gratuite. Pour tester les variantes, alterner l'objet A et l'objet B un mois sur deux et comparer les taux d'ouverture.
- Après J9 : le contact passe dans la liste de la newsletter mensuelle (TODO : rythme à décider par Clara, une fois par mois suffit pour démarrer).

### Règles à respecter dans tous les e-mails
- Chaque lien affilié est signalé juste à côté : « lien affilié : je touche une petite commission, sans surcoût pour toi ».
- Les liens `#affilie-...` sont factices : à remplacer par les vrais liens une fois les programmes validés (liste dans `_affiliation/a-brancher.md`). Les identifiants sont ceux de `_build/simulateurs.js`.
- Aucune promesse de soin, de pousse ou de résultat. Aucun faux avis, aucune fausse photo avant/après, aucun faux compte à rebours, aucune fausse rareté.
- Lien de désinscription `{{ unsubscribe }}` dans chaque pied de page, et adresse postale de l'éditrice.

### Pied de page commun (à mettre dans le modèle Brevo)

> Tu reçois cet e-mail car tu t'es inscrite sur carnetcapillaire.fr et tu as confirmé ton adresse.
> Carnet capillaire, TODO nom de l'éditrice, TODO adresse postale.
> Certains liens sont affiliés : si tu achètes via ces liens, je touche une petite commission, sans surcoût pour toi. Aucune marque ne paie pour figurer dans mes sélections.
> Ces conseils ne remplacent pas l'avis d'un médecin ou d'un dermatologue.
> [Me désinscrire]({{ unsubscribe }}) · [Politique de confidentialité](https://carnetcapillaire.fr/mentions-legales/#confidentialite)

## E-mail de confirmation (double opt-in)

**Objet** : Confirme ton adresse pour recevoir ta routine
**Pré-en-tête** : Un clic, et ta routine arrive avec le mini-guide.

Bonjour {{ contact.PRENOM | default: "" }},

Tu viens de demander ta routine et le mini-guide « Les 5 erreurs qui abîment tes cheveux » sur Carnet capillaire.

Pour les recevoir, confirme simplement ton adresse :

**[Oui, je confirme mon adresse]({{ doubleoptin }})**

Si ce n'est pas toi, ignore ce message : tu ne recevras rien d'autre.

À tout de suite,
Clara, Carnet capillaire

*Tu reçois ce message unique parce que cette adresse a été saisie sur carnetcapillaire.fr. Sans confirmation, elle n'est pas ajoutée à la liste.*
*Carnet capillaire, TODO nom de l'éditrice, TODO adresse postale.*

## E-mail 1, J0 : ta routine et ton mini-guide

**Objet A** : Ta routine est là (et ton mini-guide aussi)
**Objet B** : {{ contact.PRENOM | default: "Coucou" }}, voici ce que tes cheveux m'ont dit
**Pré-en-tête** : Les 4 étapes de ta routine, et les 5 gestes qui changent tout.

Coucou {{ contact.PRENOM | default: "toi" }},

Merci d'avoir confirmé ton adresse. Comme promis, voici ta routine et ton mini-guide.

**Ton résultat**

{% if contact.TEST == "quiz" %}
D'après le quiz, tu as probablement les cheveux **{{ contact.TYPE_CHEVEUX | default: "de ton type" }}**. Voici ta routine en 4 étapes :
- **Laver** : un shampoing adapté à ton cuir chevelu, posé sur les racines seulement.
- **Nourrir** : un après-shampoing sur les longueurs à chaque lavage, un masque une fois par semaine si elles sont sèches.
- **Hydrater** : un soin sans rinçage léger, selon ton épaisseur.
- **Coiffer** : en douceur, sans chaleur forte, avec un protecteur thermique si tu en utilises.
{% elif contact.TEST == "shampoing" %}
D'après le test, il te faut **{{ contact.RESULTAT | default: "un shampoing doux, adapté à ton cuir chevelu" }}**. Le bon réflexe : le shampoing sur les racines, l'après-shampoing sur les longueurs.
{% elif contact.TEST == "cuir" %}
D'après le diagnostic, tu as plutôt **{{ contact.RESULTAT | default: "un cuir chevelu à chouchouter" }}**. Garde des gestes doux, un seul nouveau produit à la fois, et si ça dure plus de quelques semaines ou s'il y a des plaques, des rougeurs ou une douleur, parles-en à ton médecin ou à un dermatologue.
{% elif contact.TEST == "routine" %}
D'après le simulateur, ta routine type, c'est **{{ contact.RESULTAT | default: "shampoing, après-shampoing et un masque par semaine" }}**. Le poste qui compte le plus n'est pas le plus cher : c'est l'après-shampoing à chaque lavage.
{% else %}
Tu n'as pas encore fait de test ? Commence par le quiz « Quel est ton type de cheveux ? » : 2 minutes, et tu repars avec ta routine en 4 étapes.
**[Faire le quiz](https://carnetcapillaire.fr/quiz-type-de-cheveux/)**
{% endif %}

Ta liste de produits complète, avec les liens, t'attend ici :
**[Revoir mon résultat et mes produits](https://carnetcapillaire.fr/tests-cheveux/)**
<!-- TODO : si le formulaire transmet l'URL du résultat (SOURCE_PAGE + paramètres), pointer directement vers elle. -->

**Ton mini-guide gratuit**

« Les 5 erreurs qui abîment tes cheveux », en 5 pages : la serviette, la chaleur, le shampoing sur les longueurs, les coiffures qui tirent et les recettes maison. Pour chacune, pourquoi ça abîme et le bon geste à la place.

**[Télécharger le mini-guide (PDF)](https://carnetcapillaire.fr/telechargements/mini-guide-5-erreurs.pdf)**
<!-- TODO : héberger le PDF du mini-guide (il est gratuit : il peut aller dans le site, contrairement au guide payant). -->

Dans les prochains jours, je t'envoie quelques e-mails courts : une erreur que je vois partout, ce que ton type de cheveux aime vraiment, et ce qu'on peut attendre (honnêtement) d'une nouvelle routine. Pas plus d'un tous les deux ou trois jours, promis.

Une question sur tes cheveux ? Réponds simplement à cet e-mail, je lis tout. (Je ne fais pas de diagnostic médical par e-mail, mais je peux t'orienter.)

À très vite,
Clara, Carnet capillaire

*Pied de page commun.*

## E-mail 2, J2 : l'erreur que je vois partout

**Objet A** : L'erreur que (presque) tout le monde fait sous la douche
**Objet B** : Ton shampoing n'est peut-être pas le problème
**Pré-en-tête** : Un geste de 10 secondes qui change tes longueurs.

Coucou {{ contact.PRENOM | default: "toi" }},

Si je ne devais garder qu'un conseil, ce serait celui-là : **le shampoing, c'est pour le cuir chevelu. Les longueurs, elles, ont besoin d'après-shampoing.**

On a presque toutes appris à frotter le shampoing sur toute la tête. Résultat : les pointes perdent le peu de protection qu'elles ont, et deviennent rêches, ternes, cassantes. L'Académie américaine de dermatologie classe d'ailleurs « frotter le shampoing sur les longueurs » et « sauter l'après-shampoing » parmi les habitudes qui abîment le plus les cheveux ([la source](https://www.aad.org/public/everyday-care/hair-scalp-care/hair/habits-that-damage-hair), en anglais).

**Le geste, dès ce soir :**
1. Une noisette de shampoing sur les racines, massée avec la pulpe des doigts.
2. La mousse qui coule en rinçant suffit pour les longueurs.
3. L'après-shampoing sur les longueurs et les pointes, jamais sur le cuir chevelu, à chaque lavage. Tu démêles avec les doigts pendant qu'il est posé.

Et non, laver souvent n'abîme pas tes cheveux si ton shampoing est doux : une étude menée en 2021 auprès de 1 500 personnes n'a pas observé de dégât lié à des lavages fréquents ([la source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8138261/)).

**Si tu cherches un après-shampoing qui fait aussi masque, à petit prix**

{% if contact.PROFIL_CUIR == "gras" %}
Avec des racines grasses, garde-le bien loin du cuir chevelu, et préfère une petite quantité.
{% endif %}

Le **Garnier Ultra Doux Hair Food Banane** s'utilise en après-shampoing, en masque ou en soin sans rinçage. C'est une option simple pour les longueurs sèches, les boucles et les cheveux crépus, que l'on trouve en supermarché.
<!-- TODO Clara : tester ce produit avant l'envoi, vérifier la liste INCI et le prix ; le remplacer si tu en préfères un autre (même identifiant que sur le site). -->

**[Voir le prix du masque Hair Food Banane](#affilie-amazon-garnier-hair-food-banane)**
*Lien affilié : je touche une petite commission, sans surcoût pour toi. Je le cite parce qu'il correspond à beaucoup de profils, aucune marque ne m'a payée pour ça.*

Pour les cheveux fins ou raides, il risque d'alourdir : un après-shampoing léger, posé seulement sur les pointes, ira mieux. Tu trouveras des options dans le [guide des cheveux fins](https://carnetcapillaire.fr/cheveux-fins/).

Dans deux jours, on parle de ton type de cheveux et de ce qu'il aime vraiment.

Clara, Carnet capillaire

*Pied de page commun.*

## E-mail 3, J4 : ce que ton type de cheveux aime vraiment

**Objet A** : Ce que tes cheveux {{ contact.TYPE_CHEVEUX | default: "" }} aiment vraiment
**Objet B** : 3 choses à savoir sur ton type de cheveux
**Pré-en-tête** : Et les produits à regarder, à tous les budgets.

Coucou {{ contact.PRENOM | default: "toi" }},

Chaque type de cheveux a ses besoins. Voici l'essentiel pour le tien.
<!-- Brevo : le bloc ci-dessous s'adapte au résultat du quiz. Valeurs possibles de TYPE_CHEVEUX commençant par : raides, ondulés, bouclés, frisés, crépus. Si l'attribut est vide, le bloc par défaut s'affiche. -->

{% if "raides" in contact.TYPE_CHEVEUX %}
**Tes cheveux raides**
- Ils regraissent vite parce que le sébum glisse facilement le long d'une fibre lisse. Un shampoing doux, aussi souvent que nécessaire, ne pose pas de problème.
- Ils s'aplatissent sous les produits riches : après-shampoing léger, seulement sur les pointes.
- La chaleur est ton principal ennemi : protecteur thermique et température moyenne.
**[Lire le guide des cheveux raides](https://carnetcapillaire.fr/cheveux-raides/)**
{% elif "ondulés" in contact.TYPE_CHEVEUX %}
**Tes cheveux ondulés**
- Leurs vagues s'aplatissent vite si on les alourdit : des soins légers, en petite quantité.
- Pas de brosse sur cheveux secs, qui casse l'ondulation et crée des frisottis.
- Une mousse ou un gel léger sur cheveux trempés aide à garder la forme.
**[Lire le guide des cheveux ondulés](https://carnetcapillaire.fr/cheveux-ondules/)**
{% elif "bouclés" in contact.TYPE_CHEVEUX %}
**Tes cheveux bouclés**
- Le sébum descend mal le long des spirales : les longueurs ont souvent soif.
- Ils adorent l'eau : on pose les soins sur cheveux trempés, et on essore dans un tee-shirt en coton.
- Un nettoyant doux, un après-shampoing généreux et un gel ou une crème de définition.
**[Lire le guide des cheveux bouclés](https://carnetcapillaire.fr/cheveux-boucles/)**
{% elif "frisés" in contact.TYPE_CHEVEUX %}
**Tes cheveux frisés**
- Des boucles serrées et pleines de volume, souvent très sèches : on nourrit à chaque lavage.
- On démêle uniquement sur cheveux mouillés et imprégnés de soin, des pointes vers les racines.
- La nuit, un bonnet ou une taie en satin limite les frottements.
**[Lire le guide des cheveux frisés](https://carnetcapillaire.fr/cheveux-frises/)**
{% elif "crépus" in contact.TYPE_CHEVEUX %}
**Tes cheveux crépus**
- C'est la texture la plus dense, et la plus fragile : chaque courbe est un point de casse.
- Crème lavante ou shampoing sans sulfate, masque riche, et la méthode LOC pour garder l'hydratation.
- Des coiffures protectrices, mais jamais serrées sur les bords.
**[Lire le guide des cheveux crépus](https://carnetcapillaire.fr/cheveux-crepus/)**
{% else %}
**Tu ne connais pas encore ton type ?**
Le quiz te le dit en 2 minutes : texture, épaisseur, cuir chevelu et porosité.
**[Faire le quiz](https://carnetcapillaire.fr/quiz-type-de-cheveux/)**
{% endif %}

**Et si tu veux tout au même endroit**

Je reçois souvent la même question : « D'accord, mais concrètement, j'achète quoi ? ». C'est pour ça que j'ai écrit **un guide PDF par type de cheveux** : une vingtaine de pages rien que pour ton type, avec ta routine semaine par semaine, 3 produits par budget (petit, moyen, premium) vendus en France, les erreurs à éviter et les problèmes de ton type.
<!-- Brevo : le guide du type connu en premier, sinon le sélecteur et le pack. Ordre des tests : fins avant raides. -->

{% if "fins" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux fins, 9 €](https://carnetcapillaire.fr/guide/cheveux-fins/)** : ta routine du premier mois et tes produits, au même endroit.
{% elif "raides" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux raides, 9 €](https://carnetcapillaire.fr/guide/cheveux-raides/)** : ta routine du premier mois et tes produits, au même endroit.
{% elif "ondulés" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux ondulés, 9 €](https://carnetcapillaire.fr/guide/cheveux-ondules/)** : ta routine du premier mois et tes produits, au même endroit.
{% elif "bouclés" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux bouclés, 9 €](https://carnetcapillaire.fr/guide/cheveux-boucles/)** : ta routine du premier mois et tes produits, au même endroit.
{% elif "frisés" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux frisés, 9 €](https://carnetcapillaire.fr/guide/cheveux-frises/)** : ta routine du premier mois et tes produits, au même endroit.
{% elif "crépus" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux crépus, 9 €](https://carnetcapillaire.fr/guide/cheveux-crepus/)** : ta routine du premier mois et tes produits, au même endroit.
{% else %}
**[Choisir mon guide, 9 €](https://carnetcapillaire.fr/guide-produits-cheveux-pdf/)** : un guide par type de cheveux. Ou **[le pack complet tous types, 19 €](https://carnetcapillaire.fr/guide-produits-cheveux-pdf/#pack)**.
{% endif %}

Les guides du site restent gratuits et complets : le PDF te fait surtout gagner du temps.

Clara, Carnet capillaire

*Pied de page commun.*

## E-mail 4, J6 : un avant/après honnête

**Objet A** : Ce qu'une nouvelle routine change vraiment (et en combien de temps)
**Objet B** : Les avant/après que tu vois sur TikTok, parlons-en
**Pré-en-tête** : Pas de miracle, mais des changements bien réels.

Coucou {{ contact.PRENOM | default: "toi" }},

Tu as sûrement vu passer des avant/après spectaculaires : des cheveux ternes devenus brillants en une semaine, une « pousse record » grâce à une huile. Je préfère te dire les choses franchement.

<!-- TODO Clara : si tu veux illustrer cet e-mail, utilise UNIQUEMENT une vraie photo de tes propres cheveux, prise dans la même lumière, sans filtre, avec les deux dates écrites dessous (ex. « 3 octobre / 14 novembre »), et la routine exacte suivie entre les deux. Pas de photo d'une autre personne, pas de photo de marque, pas d'image générée. Si tu n'en as pas encore, envoie l'e-mail sans photo : le texte suffit. -->

**Ce qui peut changer vite (en 2 à 4 lavages)**
- Le toucher : des longueurs plus douces et plus faciles à démêler, grâce à l'après-shampoing et aux bons gestes.
- Les frisottis et la définition des boucles, quand tu arrêtes la serviette éponge et la brosse sur cheveux secs.
- La sensation de cuir chevelu propre ou moins tiraillé, avec un shampoing adapté.

**Ce qui prend des mois**
- Les pointes abîmées ne se réparent pas : un cheveu est une fibre morte. Les soins les gainent, mais seule la coupe les enlève. Ce qui change avec le temps, c'est que les nouvelles longueurs, mieux protégées, cassent moins.
- La longueur : les cheveux poussent d'environ 1 cm par mois en moyenne (TODO Clara : garder ce chiffre seulement avec une source, par ex. la fiche Vidal sur la chute de cheveux), et aucun cosmétique ne les fait pousser plus vite. Moins de casse, en revanche, ça se voit sur la longueur au bout de quelques mois.

**Ce qu'aucun produit ne fait**
- Arrêter une chute importante ou soigner un cuir chevelu irrité. Un cosmétique ne soigne pas ([DGCCRF](https://www.economie.gouv.fr/dgccrf/allegations-sur-les-produits-cosmetiques-tout-nest-pas-permis)). Si tu perds beaucoup de cheveux, par plaques, ou si ton cuir chevelu gratte depuis des semaines, c'est un rendez-vous chez ton médecin ou un dermatologue.

**Mon conseil pour juger une routine**
Prends une photo de tes cheveux aujourd'hui, à la lumière du jour, et une autre dans 6 semaines, dans la même lumière. Change un seul produit à la fois. C'est le seul avant/après qui compte : le tien.

Dans trois jours, je te présente une dernière fois le guide PDF, puis je te laisse tranquille avec ça.

Clara, Carnet capillaire

*Pied de page commun.*

## E-mail 5, J9 : le guide PDF

**Objet A** : Arrête d'acheter au hasard
**Objet B** : {{ contact.PRENOM | default: "Ta" }}, ta liste de produits, classée pour tes cheveux
**Pré-en-tête** : Le guide PDF de ton type de cheveux, 9 €.

Coucou {{ contact.PRENOM | default: "toi" }},

Ça fait une semaine que tu reçois mes e-mails, merci de les lire. Aujourd'hui, je te parle une dernière fois de mon guide, puis on passe à autre chose.

**Le guide PDF de ton type de cheveux**

Tu as déjà acheté un shampoing « miracle » qui a fini au fond du placard ? Moi aussi. Ces guides sont là pour que ça n'arrive plus.

Dans chaque guide (raides, fins, ondulés, bouclés, frisés ou crépus) :
- **Comment lire une étiquette INCI**, avec ce qu'il faut chercher pour ton type.
- **Ta routine semaine par semaine** : ton jour de lavage pas à pas, puis un premier mois en 4 semaines.
- **3 produits par budget** : petit prix, moyen, premium, tous vendus en France.
- **Les erreurs fréquentes et les problèmes de ton type** (par exemple, pour les cheveux frisés : sécheresse, frisottis, nœuds, rétraction), et quand consulter.
- **Un calendrier** et une fiche de suivi à garder sous la main.

**Ce qu'il n'est pas** : un traitement, ni une promesse de pousse. Les sources sont citées à la fin, et aucune marque n'a payé pour y figurer.

Prix : **9 €** le guide de ton type, en PDF à télécharger tout de suite, lisible sur téléphone. Et si plusieurs types cohabitent chez toi, **le pack complet tous types est à 19 €**.
<!-- TODO Louis : pas de prix barré ni de « offre limitée » tant qu'il n'y a pas de vraie promotion datée. Si un code de bienvenue est créé dans Stripe, l'indiquer ici avec sa vraie date de fin. -->

{% if "fins" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux fins, 9 €](https://carnetcapillaire.fr/guide/cheveux-fins/)** : ta routine, tes produits et tes problèmes, en une vingtaine de pages.
{% elif "raides" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux raides, 9 €](https://carnetcapillaire.fr/guide/cheveux-raides/)** : ta routine, tes produits et tes problèmes, en une vingtaine de pages.
{% elif "ondulés" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux ondulés, 9 €](https://carnetcapillaire.fr/guide/cheveux-ondules/)** : ta routine, tes produits et tes problèmes, en une vingtaine de pages.
{% elif "bouclés" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux bouclés, 9 €](https://carnetcapillaire.fr/guide/cheveux-boucles/)** : ta routine, tes produits et tes problèmes, en une vingtaine de pages.
{% elif "frisés" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux frisés, 9 €](https://carnetcapillaire.fr/guide/cheveux-frises/)** : ta routine, tes produits et tes problèmes, en une vingtaine de pages.
{% elif "crépus" in contact.TYPE_CHEVEUX %}
**[Ton guide cheveux crépus, 9 €](https://carnetcapillaire.fr/guide/cheveux-crepus/)** : ta routine, tes produits et tes problèmes, en une vingtaine de pages.
{% else %}
**[Choisir mon guide, 9 €](https://carnetcapillaire.fr/guide-produits-cheveux-pdf/)** : un guide par type de cheveux. Ou **[le pack complet tous types, 19 €](https://carnetcapillaire.fr/guide-produits-cheveux-pdf/#pack)**.
{% endif %}

Et si ce n'est pas pour toi, aucun souci : les guides et les tests du site restent gratuits, et tu continueras à recevoir mes conseils une fois par mois. Tu peux aussi te désinscrire en un clic, en bas de cet e-mail.

Merci de me lire,
Clara, Carnet capillaire

*Pied de page commun.*

## Après la séquence

- Si `ACHAT_GUIDE` passe à oui : e-mail de remerciement avec le lien de téléchargement du bon produit (`GUIDE_ACHETE` : un type ou le pack) (TODO : livraison décrite sur la page /merci/ et le serveur de vérification), puis sortie du scénario de vente.
- Statistiques à suivre dans Brevo, après 100 inscrites : taux d'ouverture (repère : au-dessus de 40 % pour une séquence de bienvenue), taux de clic, désinscriptions par e-mail (au-dessus de 1 % sur un e-mail, revoir son contenu ou sa fréquence), ventes du guide après J4 et J9.
