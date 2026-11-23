# MorphoSite
Les Mathématiques des transformations

Complément du livre *Les Mathématiques des Transformations* : 32 projets concrets (un par chapitre), chacun présenté comme un parcours de questions, avec des réponses simples puis les mathématiques derrière.

- `index.html` : page d'accueil (recherche et filtres par partie ; la recherche liste aussi les questions des parcours où le mot apparaît, avec un lien direct vers la question)
- `projets/` : une page par projet. Chaque question est d'abord cachée (« Devine d'abord », désactivable dans la marge) : l'élève réfléchit, découvre la réponse et dit s'il avait trouvé. Les étapes atteintes, ces réponses et la fin du parcours sont gardées sur l'appareil (`localStorage`, clé `famzak:morpho:<page>`). L'accueil en tire « Mes projets terminés » (grille des 32 projets, badges 1, 8, 16, 32)
- `assets/style.css` : feuille de style commune
- `livre/` : le livre en PDF (lien « Le livre (PDF) » du menu)
- `_source/` : générateur (`python3 build.py`, lancé depuis `_source/`) et contenu des projets (`projets/p1.py` à `p7.py`). Le générateur lit le PDF de `livre/` pour retrouver les numéros de page.

Progression liée au code élève : `famzak-progres.js` (même fichier sur les sites FamZakSites) envoie les progrès des jeux au serveur de suivi de RoutineSite (routes `/progres/…`, Worker 1.6) sous le code de l'élève, saisi une fois (bouton 👤 en bas à droite). Sans code, tout reste sur l'appareil.
