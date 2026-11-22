# MorphoSite
Les Mathématiques des transformations

Complément du livre *Les Mathématiques des Transformations* : 32 projets concrets (un par chapitre), chacun présenté comme un parcours de questions, avec des réponses simples puis les mathématiques derrière.

- `index.html` : page d'accueil (recherche et filtres par partie ; la recherche liste aussi les questions des parcours où le mot apparaît, avec un lien direct vers la question)
- `projets/` : une page par projet
- `assets/style.css` : feuille de style commune
- `livre/` : le livre en PDF (lien « Le livre (PDF) » du menu)
- `_source/` : générateur (`python3 build.py`, lancé depuis `_source/`) et contenu des projets (`projets/p1.py` à `p7.py`). Le générateur lit le PDF de `livre/` pour retrouver les numéros de page.
