#!/bin/sh
# Publication de carnetcapillaire.fr : build + contrôles + push du dossier site/ sur la branche gh-pages (GitHub Pages).
# Usage : ./publier.sh            (ajoute --ping pour prévenir Bing/Yandex via IndexNow après la mise en ligne)
# Les sources se poussent à part, sur main : git push origin main
set -e
cd "$(dirname "$0")"
REMOTE="https://github.com/lardeuxlouis-commits/carnetcapillaire.fr.git"
DOMAINE="carnetcapillaire.fr"

# Données du classement (compositions + plus scannés) : réseau, sans bloquer la publication si le VPS ou OBF ne répondent pas
python3 _build/classement_data.py || echo "classement_data.py en échec : on garde _build/classement.json actuel"
python3 _build/build.py
if ! python3 _build/verif.py > /tmp/verif-carnet.txt; then
  grep -v " OK$" /tmp/verif-carnet.txt; echo "verif.py a trouvé des problèmes : publication annulée."; exit 1
fi
tail -3 /tmp/verif-carnet.txt

TMP=$(mktemp -d)
cp -R site/. "$TMP"/
echo "$DOMAINE" > "$TMP/CNAME"
touch "$TMP/.nojekyll"
cd "$TMP"
git init -q -b gh-pages
git add -A
git -c user.name="Carnet capillaire" -c user.email="publication@$DOMAINE" commit -qm "Publication du $(date '+%d/%m/%Y %H:%M')"
git push -q -f "$REMOTE" gh-pages
cd - > /dev/null
rm -rf "$TMP"
echo "Publié sur https://$DOMAINE/ (GitHub Pages met à jour en 1 à 2 minutes)."

if [ "$1" = "--ping" ]; then
  KEY=$(cat _build/indexnow.txt)
  curl -s -o /dev/null -w "IndexNow : HTTP %{http_code}\n" -X POST "https://api.indexnow.org/indexnow" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "{\"host\":\"$DOMAINE\",\"key\":\"$KEY\",\"keyLocation\":\"https://$DOMAINE/$KEY.txt\",\"urlList\":[\"https://$DOMAINE/\",\"https://$DOMAINE/sitemap.xml\"]}"
fi
