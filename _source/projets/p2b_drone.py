# Partie II — chapitre 6 : le drone (repris du POC validé par Armen)

PROJETS = [
{'ch': 6,
 'slug': 'drone',
 'emoji': '🚁',
 'title': 'Construire un drone',
 'em': 'drone',
 'card': 'Construire un drone',
 'desc': "Tenir en l'air, savoir où l'on penche, se redresser 400 fois par seconde : quaternions, Fourier, Laplace et relativité.",
 'tags': ['vecteurs', 'nombres complexes', 'quaternions', 'régulation'],
 'lead': "Dix questions à se poser dans l'ordre, comme un ingénieur qui part de zéro. Pour chacune : une réponse simple, puis les mathématiques qui se cachent "
         'derrière, et où les retrouver dans le livre.',
 'hero': {'type': 'svg',
          'svg': '<svg viewBox="0 0 360 230" role="img" aria-label="Drone à quatre hélices vu de face">\n'
                 '          <defs><radialGradient id="g1" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#5fd4f0" stop-opacity=".35"/><stop offset="1" '
                 'stop-color="#5fd4f0" stop-opacity="0"/></radialGradient></defs>\n'
                 '          <circle cx="180" cy="118" r="110" fill="url(#g1)"/>\n'
                 '          <g stroke="#c4b5fd" stroke-width="3" fill="none" stroke-linecap="round">\n'
                 '            <line x1="70" y1="104" x2="290" y2="104"/>\n'
                 '            <line x1="82" y1="104" x2="82" y2="92"/><line x1="278" y1="104" x2="278" y2="92"/>\n'
                 '            <line x1="136" y1="104" x2="136" y2="94"/><line x1="224" y1="104" x2="224" y2="94"/>\n'
                 '          </g>\n'
                 '          <g fill="#5fd4f0" opacity=".9">\n'
                 '            <ellipse cx="82" cy="88" rx="34" ry="4"/><ellipse cx="278" cy="88" rx="34" ry="4"/>\n'
                 '            <ellipse cx="136" cy="90" rx="24" ry="3" opacity=".6"/><ellipse cx="224" cy="90" rx="24" ry="3" opacity=".6"/>\n'
                 '          </g>\n'
                 '          <rect x="150" y="96" width="60" height="30" rx="10" fill="#1a2150" stroke="#c4b5fd" stroke-width="2"/>\n'
                 '          <circle cx="180" cy="133" r="7" fill="#0b1233" stroke="#5fd4f0" stroke-width="2"/>\n'
                 '          <g stroke="#5fd1b3" stroke-width="2.5" fill="#5fd1b3">\n'
                 '            <line x1="82" y1="76" x2="82" y2="40"/><path d="M76 46 L82 34 L88 46Z" stroke="none"/>\n'
                 '            <line x1="278" y1="76" x2="278" y2="40"/><path d="M272 46 L278 34 L284 46Z" stroke="none"/>\n'
                 '          </g>\n'
                 '          <g stroke="#f5a65b" stroke-width="2.5" fill="#f5a65b">\n'
                 '            <line x1="180" y1="146" x2="180" y2="196"/><path d="M174 190 L180 202 L186 190Z" stroke="none"/>\n'
                 '          </g>\n'
                 '          <text x="96" y="44" fill="#5fd1b3" font-family="Jost" font-size="13">poussée</text>\n'
                 '          <text x="192" y="196" fill="#f5a65b" font-family="Jost" font-size="13">poids</text>\n'
                 '          <text x="20" y="222" fill="#7c85ab" font-family="Jost" font-size="12">roulis · tangage · lacet : trois façons de tourner</text>\n'
                 '        </svg>'},
 'steps': [{'q': "Qu'est-ce qui fait tenir un drone en l'air ?",
            'a': "Ses quatre hélices <b>poussent l'air vers le bas</b>, et l'air pousse le drone vers le haut. Pour rester immobile en l'air, il suffit que "
                 'cette poussée soit <b>exactement égale à son poids</b>. Un peu plus, il monte ; un peu moins, il descend.',
            'mt': 'les vecteurs',
            'f': '<span class="v">P</span>₁ + <span class="v">P</span>₂ + <span class="v">P</span>₃ + <span class="v">P</span>₄ + <span class="v">Poids</span> '
                 '= <span class="v">0',
            'mp': "Une force a une direction et une intensité : c'est un vecteur. En vol stationnaire, la somme de toutes les forces est le vecteur nul.",
            'book': {'ch': 5, 'label': 'Déplacer sans déformer (vecteurs)', 'p': 54},
            'more': ('Aller plus loin',
                     '<p>Un drone de 1 kg pèse environ 10 newtons : chaque hélice doit donc fournir environ 2,5 N. Pour monter, le contrôleur augmente un peu '
                     'la vitesse des quatre moteurs en même temps.</p>'),
            'art': {'type': 'svg',
                    'svg': '<svg viewBox="0 0 220 180" aria-label="Forces sur le drone"><rect x="70" y="80" width="80" height="22" rx="8" fill="#1a2150" '
                           'stroke="#c4b5fd" stroke-width="2"/><line x1="30" y1="80" x2="190" y2="80" stroke="#c4b5fd" stroke-width="3"/>\n'
                           '        <g stroke="#5fd1b3" stroke-width="3"><line x1="40" y1="74" x2="40" y2="30"/><line x1="180" y1="74" x2="180" '
                           'y2="30"/></g><g fill="#5fd1b3"><path d="M34 36 L40 24 L46 36Z"/><path d="M174 36 L180 24 L186 36Z"/></g>\n'
                           '        <g stroke="#f5a65b" stroke-width="3"><line x1="110" y1="106" x2="110" y2="158"/></g><path d="M104 152 L110 166 L116 152Z" '
                           'fill="#f5a65b"/>\n'
                           '        <text x="50" y="40" fill="#5fd1b3" font-size="12" font-family="Jost">poussée</text><text x="118" y="158" fill="#f5a65b" '
                           'font-size="12" font-family="Jost">poids</text></svg>'},
            'cap': 'Poussée = poids : il plane',
            'short': "Qu'est-ce qui le fait tenir en l'air ?"},
           {'q': 'Sans gouvernail ni ailes, comment avance-t-il et tourne-t-il ?',
            'a': "Pour avancer, il fait tourner <b>un peu plus vite les hélices de l'arrière</b> : il penche vers l'avant, et une partie de la poussée le tire "
                 "dans cette direction. Pour pivoter sur lui-même, il joue sur un détail : <b>deux hélices tournent dans un sens, deux dans l'autre</b>. Si "
                 "une paire accélère, le drone tourne dans le sens opposé, comme un patineur qui pivote en lançant les bras de l'autre côté.",
            'mt': 'ce qui se conserve',
            'f': 'symétrie ⟶ quantité conservée',
            'mp': "Quand un système n'a rien pour « s'accrocher », sa quantité de rotation totale (le moment cinétique) ne change pas : si les hélices "
                  "tournent plus d'un côté, le corps du drone compense de l'autre. C'est le théorème de Noether.",
            'morph': 'une symétrie donne un invariant',
            'book': {'ch': 21, 'label': 'Mouvement et conservation', 'p': 190},
            'art': {'type': 'svg',
                    'svg': '<svg viewBox="0 0 200 200" aria-label="Drone vu de dessus, sens de rotation des hélices"><line x1="50" y1="50" x2="150" y2="150" '
                           'stroke="#c4b5fd" stroke-width="3"/><line x1="150" y1="50" x2="50" y2="150" stroke="#c4b5fd" stroke-width="3"/><rect x="85" y="85" '
                           'width="30" height="30" rx="7" fill="#1a2150" stroke="#c4b5fd" stroke-width="2"/>\n'
                           '        <g fill="none" stroke-width="3"><circle cx="50" cy="50" r="26" stroke="#5fd4f0"/><circle cx="150" cy="150" r="26" '
                           'stroke="#5fd4f0"/><circle cx="150" cy="50" r="26" stroke="#f0719a"/><circle cx="50" cy="150" r="26" stroke="#f0719a"/></g>\n'
                           '        <g font-family="Jost" font-size="20" text-anchor="middle"><text x="50" y="57" fill="#5fd4f0">↻</text><text x="150" y="157" '
                           'fill="#5fd4f0">↻</text><text x="150" y="57" fill="#f0719a">↺</text><text x="50" y="157" fill="#f0719a">↺</text></g></svg>'},
            'cap': 'Vu de dessus : deux paires en sens opposés',
            'short': 'Comment avance-t-il et tourne-t-il ?'},
           {'q': 'Comment décrire où il est et comment il se déplace ?',
            'a': 'On choisit un point de départ et trois directions : est, nord, haut. La position du drone devient <b>trois nombres (x, y, z)</b>. Un '
                 "déplacement, c'est une flèche qu'on ajoute à ces nombres. Et comme le drone est rigide, <b>tous ses points bougent ensemble</b> : un seul "
                 'calcul déplace toute la machine, sans la déformer.',
            'mt': 'vecteurs et matrices',
            'f': '(x, y, z) ⟼ (x + a, y + b, z + c)',
            'mp': "Une translation ou une rotation conserve les distances (une isométrie). En informatique, on l'écrit comme une seule matrice appliquée à "
                  'tous les points, exactement comme un moteur de jeu vidéo.',
            'morph': 'conserver les distances',
            'book': {'ch': 5, 'label': 'Déplacer sans déformer', 'p': 54},
            'art': {'type': 'svg',
                    'svg': '<svg viewBox="0 0 220 170" aria-label="Translation d\'un objet rigide"><g stroke="#7c85ab" stroke-width="1.5"><line x1="20" '
                           'y1="150" x2="210" y2="150"/><line x1="20" y1="150" x2="20" y2="10"/></g>\n'
                           '        <g fill="none" stroke-width="2.5"><rect x="35" y="105" width="50" height="24" rx="6" stroke="#7c85ab" stroke-dasharray="4 '
                           '4"/><rect x="140" y="40" width="50" height="24" rx="6" stroke="#5fd4f0"/></g>\n'
                           '        <line x1="62" y1="115" x2="158" y2="55" stroke="#a78bfa" stroke-width="2.5"/><path d="M152 52 L164 51 L158 62Z" '
                           'fill="#a78bfa"/><text x="96" y="76" fill="#c4b5fd" font-size="13" font-family="Jost">vecteur</text></svg>'},
            'cap': 'Même forme, autre place',
            'short': 'Comment décrire où il est ?'},
           {'q': 'Comment décrire de quel côté il penche ?',
            'a': 'Les pilotes utilisent trois angles : le <b>roulis</b> (pencher à gauche ou à droite), le <b>tangage</b> (piquer du nez ou le relever) et le '
                 "<b>lacet</b> (pivoter comme une girouette). Dans un plan, un seul angle suffirait : tourner d'un angle, c'est simplement <b>multiplier par "
                 'un nombre complexe</b> de longueur 1.',
            'mt': 'les nombres complexes',
            'f': 'e<sup>iα</sup> × e<sup>iβ</sup> = e<sup>i(α+β)</sup>',
            'mp': "Tourner de α puis de β, c'est tourner de α + β. L'exponentielle transforme une addition d'angles en multiplication de rotations.",
            'morph': 'θ ↦ e<sup>iθ</sup>, des angles vers les rotations',
            'book': {'ch': 6, 'label': 'Tourner, symétriser', 'p': 62},
            'art': {'type': 'svg',
                    'svg': '<svg viewBox="0 0 200 190" aria-label="Rotation sur le cercle unité"><circle cx="100" cy="100" r="70" fill="none" stroke="#7c85ab" '
                           'stroke-width="1.5"/><line x1="20" y1="100" x2="180" y2="100" stroke="#7c85ab"/><line x1="100" y1="20" x2="100" y2="180" '
                           'stroke="#7c85ab"/>\n'
                           '        <line x1="100" y1="100" x2="170" y2="100" stroke="#5fd4f0" stroke-width="3"/><line x1="100" y1="100" x2="149" y2="50" '
                           'stroke="#a78bfa" stroke-width="3"/>\n'
                           '        <path d="M130 100 A30 30 0 0 0 121 79" fill="none" stroke="#f3cf7a" stroke-width="2"/><text x="134" y="88" fill="#f3cf7a" '
                           'font-size="15" font-family="Jost">θ</text><text x="150" y="44" fill="#c4b5fd" font-size="14" font-family="Jost">× '
                           'e^iθ</text></svg>'},
            'cap': 'Multiplier = tourner',
            'short': 'Comment décrire de quel côté il penche ?'},
           {'q': 'Pourquoi trois angles ne suffisent-ils pas en 3D ?',
            'a': 'Parce que, dans certaines positions, <b>deux des trois axes se superposent</b> : le drone « oublie » une direction de rotation et le calcul '
                 "décroche. C'est le <b>blocage de cardan</b>. La parade : décrire l'orientation par <b>quatre nombres</b> au lieu de trois, un quaternion. "
                 'Tous les contrôleurs de vol, des drones de loisir aux fusées, font ainsi.',
            'mt': 'les quaternions',
            'f': 'q = cos(θ/2) + sin(θ/2)(x i + y j + z k)',
            'mp': "Un quaternion prolonge les nombres complexes en dimension 4, avec i² = j² = k² = ijk = −1. Combiner deux rotations, c'est multiplier deux "
                  'quaternions : quelques microsecondes de calcul.',
            'morph': 'chaque rotation correspond à deux quaternions, q et −q',
            'book': {'ch': 6, 'label': 'cas concret « stabiliser un drone »', 'p': 69},
            'more': ('Aller plus loin : le calcul pour 10°',
                     '<p>Le drone penche de 10° en roulis (axe x). Avec θ/2 = 5° : q ≈ 0,9962 + 0,0872 i. Pour le remettre à plat, le contrôleur calcule la '
                     'rotation inverse (même axe, −10°), q<sub>corr</sub> ≈ 0,9962 − 0,0872 i, et multiplie : q<sub>corr</sub> × q = 1, la position « à plat '
                     '».</p>'),
            'art': {'type': 'svg',
                    'svg': '<svg viewBox="0 0 200 190" aria-label="Trois anneaux de cardan"><g fill="none" stroke-width="3"><ellipse cx="100" cy="95" rx="78" '
                           'ry="78" stroke="#5fd4f0"/><ellipse cx="100" cy="95" rx="78" ry="26" stroke="#f0719a"/><ellipse cx="100" cy="95" rx="26" ry="78" '
                           'stroke="#f3cf7a"/></g><circle cx="100" cy="95" r="6" fill="#c4b5fd"/><text x="100" y="186" fill="#7c85ab" font-size="12" '
                           'font-family="Jost" text-anchor="middle">si deux anneaux s\'alignent…</text></svg>'},
            'cap': 'Le blocage de cardan',
            'short': 'Pourquoi trois angles ne suffisent pas ?'},
           {'q': "Comment le drone sent-il qu'il penche ?",
            'a': 'Il a une petite centrale de capteurs : un <b>gyroscope</b> qui mesure la vitesse à laquelle il tourne, et un <b>accéléromètre</b> qui sent '
                 "où est le bas. Chaque capteur transforme un mouvement en tension électrique, puis en nombre. C'est une <b>chaîne de transformations</b>, et "
                 "chaque arrondi au passage fait perdre un tout petit peu d'information.",
            'mt': 'fonctions et composition',
            'f': 'mouvement ⟼ tension ⟼ nombre ⟼ angle',
            'mp': "On enchaîne des fonctions. Celles qui arrondissent ne sont pas injectives : deux mouvements très proches donnent le même nombre. C'est là "
                  'que se joue la précision.',
            'book': {'ch': 1, 'label': 'cas concret « le thermomètre connecté »', 'p': 20},
            'art': {'type': 'svg',
                    'svg': '<svg viewBox="0 0 220 120" aria-label="Chaîne de mesure"><g font-family="Jost" font-size="12" text-anchor="middle">\n'
                           '        <rect x="4" y="40" width="58" height="34" rx="8" fill="#121839" stroke="#5fd4f0"/><text x="33" y="61" '
                           'fill="#eef1fb">pente</text>\n'
                           '        <rect x="82" y="40" width="58" height="34" rx="8" fill="#121839" stroke="#5fd4f0"/><text x="111" y="61" '
                           'fill="#eef1fb">tension</text>\n'
                           '        <rect x="160" y="40" width="56" height="34" rx="8" fill="#121839" stroke="#5fd4f0"/><text x="188" y="61" '
                           'fill="#eef1fb">nombre</text>\n'
                           '        <text x="72" y="62" fill="#5fd1b3" font-size="16">→</text><text x="150" y="62" fill="#f5a65b" font-size="16">→</text>\n'
                           '        <text x="150" y="100" fill="#f5a65b">arrondi</text></g></svg>'},
            'cap': "Mesurer, c'est déjà transformer",
            'short': "Comment sent-il qu'il penche ?"},
           {'q': 'Les moteurs font trembler les capteurs : comment nettoyer la mesure ?',
            'a': 'Les moteurs vibrent <b>très vite</b> (des centaines de fois par seconde), alors que le drone, lui, penche <b>lentement</b>. On décompose '
                 "donc la mesure en « notes » rapides et lentes, puis on <b>ne garde que les lentes</b>. C'est la même idée que le MP3, qui jette ce que "
                 "l'oreille n'entend pas.",
            'mt': 'la transformée de Fourier',
            'f': 'signal = somme de sinusoïdes',
            'mp': 'Tout signal se décompose en fréquences pures. On passe du temps aux fréquences, on supprime le bruit, puis on revient au temps : un filtre '
                  'passe-bas.',
            'morph': 'passer du temps aux fréquences, et revenir',
            'book': {'ch': 20, 'label': 'Décomposer un signal', 'p': 182},
            'art': {'type': 'svg',
                    'svg': '<svg viewBox="0 0 220 130" aria-label="Signal bruité et signal filtré"><path d="M5 70 L12 58 L19 80 L26 52 L33 76 L40 50 L47 72 '
                           'L54 46 L61 68 L68 42 L75 64 L82 40 L89 62 L96 40 L103 60 L110 42 L117 62 L124 44 L131 66 L138 48 L145 70 L152 54 L159 76 L166 58 '
                           'L173 80 L180 64 L187 84 L194 68 L201 88 L208 74 L215 92" fill="none" stroke="#f5a65b" stroke-width="1.6" opacity=".8"/>\n'
                           '        <path d="M5 66 C50 40,90 40,120 52 S180 80,215 84" fill="none" stroke="#5fd4f0" stroke-width="3.5"/>\n'
                           '        <text x="8" y="118" fill="#f5a65b" font-size="12" font-family="Jost">mesure brute</text><text x="120" y="118" '
                           'fill="#5fd4f0" font-size="12" font-family="Jost">après filtrage</text></svg>'},
            'cap': 'On garde le mouvement, on jette la vibration',
            'short': 'Comment nettoyer des mesures qui tremblent ?'},
           {'q': 'Une rafale le bouscule : comment se redresse-t-il tout seul ?',
            'a': "Il fait comme un thermostat, mais <b>400 fois par seconde</b> : il compare ce qu'il mesure à ce qu'il vise, calcule l'<b>écart</b>, et "
                 "corrige la vitesse des moteurs d'autant plus que l'écart est grand. Trop de correction, il oscille ; pas assez, il est mou. Tout l'art est "
                 'dans le <b>réglage</b>.',
            'mt': 'boucle de régulation et transformée de Laplace',
            'f': 'correction = K × écart',
            'mp': 'Le mouvement du drone obéit à une équation différentielle, difficile à résoudre. La transformée de Laplace la change en simple calcul '
                  'algébrique ; les ingénieurs règlent K sur cette version facile, puis reviennent au temps réel.',
            'morph': 'une équation différentielle devient une fraction',
            'book': {'ch': 13, 'label': 'Piloter un système', 'p': 122},
            'more': ('Aller plus loin : le régulateur PID',
                     "<p>Un vrai contrôleur de vol combine trois termes : <b>P</b> (proportionnel à l'écart actuel), <b>I</b> (qui rattrape un petit écart qui "
                     "dure, par exemple un vent constant) et <b>D</b> (qui freine si l'écart se réduit trop vite, pour éviter de dépasser).</p>"),
            'art': {'type': 'svg',
                    'svg': '<svg viewBox="0 0 220 160" aria-label="Boucle de régulation"><g font-family="Jost" font-size="12" text-anchor="middle">\n'
                           '        <rect x="70" y="14" width="80" height="32" rx="8" fill="#121839" stroke="#a78bfa"/><text x="110" y="34" '
                           'fill="#eef1fb">calcul</text>\n'
                           '        <rect x="150" y="76" width="64" height="32" rx="8" fill="#121839" stroke="#5fd4f0"/><text x="182" y="96" '
                           'fill="#eef1fb">moteurs</text>\n'
                           '        <rect x="70" y="118" width="80" height="32" rx="8" fill="#121839" stroke="#5fd1b3"/><text x="110" y="138" '
                           'fill="#eef1fb">capteurs</text>\n'
                           '        <rect x="6" y="76" width="56" height="32" rx="8" fill="#121839" stroke="#f3cf7a"/><text x="34" y="96" '
                           'fill="#eef1fb">écart</text></g>\n'
                           '        <g fill="none" stroke="#7c85ab" stroke-width="2"><path d="M150 30 Q182 30 182 74"/><path d="M182 110 Q182 134 152 '
                           '134"/><path d="M68 134 Q34 134 34 110"/><path d="M34 74 Q34 30 68 30"/></g>\n'
                           '        <text x="110" y="88" fill="#c4b5fd" font-size="13" font-family="Jost" text-anchor="middle">400 ×/s</text></svg>'},
            'cap': 'Mesurer, comparer, corriger, recommencer',
            'short': 'Comment se redresse-t-il tout seul ?'},
           {'q': 'Dehors, comment sait-il où il est ?',
            'a': "Grâce au GPS. Des satellites envoient l'heure exacte ; le drone mesure <b>combien de temps le signal a mis</b> pour arriver, et en déduit sa "
                 'distance à chaque satellite. Avec quatre satellites, une seule position colle. Surprise : il faut tenir compte de la <b>relativité '
                 "d'Einstein</b>, sinon l'erreur grandirait d'environ <b>10 km par jour</b>.",
            'mt': 'distances et relativité',
            'f': 'distance = vitesse de la lumière × durée',
            'mp': "Là-haut, les horloges des satellites avancent d'environ 38 microsecondes par jour (45,7 μs dues à la gravité, moins 7,2 μs dues à la "
                  'vitesse). Multipliées par la vitesse de la lumière, ces microsecondes donnent des kilomètres.',
            'morph': "les transformations qui conservent l'espace-temps",
            'book': {'ch': 8, 'label': 'cas concret « la correction relativiste du GPS »', 'p': 86},
            'art': {'type': 'svg',
                    'svg': '<svg viewBox="0 0 220 170" aria-label="Trois satellites et leurs distances"><g fill="none" stroke-width="1.6" stroke-dasharray="5 '
                           '5"><circle cx="40" cy="40" r="105" stroke="#5fd4f0"/><circle cx="180" cy="30" r="110" stroke="#a78bfa"/><circle cx="200" cy="150" '
                           'r="95" stroke="#f3cf7a"/></g>\n'
                           '        <g font-size="18"><text x="28" y="46">🛰️</text><text x="168" y="36">🛰️</text><text x="188" y="156">🛰️</text></g><circle '
                           'cx="113" cy="114" r="6" fill="#5fd1b3"/><text x="62" y="118" fill="#5fd1b3" font-size="12" font-family="Jost">drone</text></svg>'},
            'cap': 'Là où les cercles se croisent',
            'short': 'Comment sait-il où il est dehors ?'},
           {'q': 'Un capteur donne des valeurs absurdes : comment trouver la panne ?',
            'a': 'On enquête comme un détective : on ne voit pas la panne, seulement ses <b>effets</b>. On <b>croise plusieurs mesures</b> qui se recoupent '
                 "(gyroscope, accéléromètre, GPS) et on cherche la seule cause qui les explique toutes. C'est le même principe qu'un scanner médical, qui "
                 "reconstruit l'intérieur du corps sans l'ouvrir.",
            'mt': 'le problème inverse',
            'f': 'effets mesurés ⟶ cause cachée',
            'mp': "Aller de la cause à l'effet est facile ; remonter de l'effet à la cause est délicat, car une petite erreur de mesure peut tout fausser. On "
                  "résout un système d'équations, en filtrant pour rester stable.",
            'book': {'ch': 23, 'label': "Remonter de l'effet à la cause", 'p': 206},
            'art': {'type': 'svg',
                    'svg': '<svg viewBox="0 0 200 150" aria-label="Plusieurs mesures convergent vers une cause"><g font-family="Jost" font-size="12" '
                           'text-anchor="middle">\n'
                           '        <rect x="6" y="10" width="58" height="28" rx="7" fill="#121839" stroke="#5fd4f0"/><text x="35" y="28" '
                           'fill="#eef1fb">gyro</text>\n'
                           '        <rect x="71" y="10" width="58" height="28" rx="7" fill="#121839" stroke="#5fd4f0"/><text x="100" y="28" '
                           'fill="#eef1fb">accél.</text>\n'
                           '        <rect x="136" y="10" width="58" height="28" rx="7" fill="#121839" stroke="#5fd4f0"/><text x="165" y="28" '
                           'fill="#eef1fb">GPS</text>\n'
                           '        <circle cx="100" cy="118" r="24" fill="#2a1830" stroke="#f0719a" stroke-width="2"/><text x="100" y="122" '
                           'fill="#f0719a">cause ?</text></g>\n'
                           '        <g stroke="#7c85ab" stroke-width="2"><line x1="35" y1="40" x2="88" y2="98"/><line x1="100" y1="40" x2="100" y2="92"/><line '
                           'x1="165" y1="40" x2="112" y2="98"/></g></svg>'},
            'cap': 'Croiser les indices',
            'short': "Un capteur dit n'importe quoi : que faire ?"}],
 'bilan': {'title': "Un drone, c'est une chaîne de transformations",
           'loop': True,
           'chain': ['mouvement', 'mesure', 'filtrage', 'orientation (quaternion)', 'écart', 'correction', 'moteurs'],
           'rows': [['Déplacer (ch. 5)', 'les distances, la forme du drone', 'la position'],
                    ['Tourner (ch. 6)', 'les longueurs', "l'orientation"],
                    ['Mesurer (ch. 1)', "l'ordre des valeurs", 'la précision (arrondis)'],
                    ['Filtrer (ch. 20)', 'le mouvement lent', 'la vibration disparaît'],
                    ['Réguler (ch. 13)', 'la consigne visée', "l'écart se réduit"],
                    ['Pivoter (ch. 21)', 'la quantité de rotation totale', 'la répartition hélices / corps']]},
 'play': {'t': 'Le drone penche de 6° au lieu de 10°',
          'q': 'Écris le quaternion de cette inclinaison en roulis (axe x). Indice : cos(3°) ≈ 0,9986 et sin(3°) ≈ 0,0523.',
          'r': "q ≈ 0,9986 + 0,0523 i. La correction est q<sub>corr</sub> ≈ 0,9986 − 0,0523 i. Exercice 7 du chapitre 6 dans l'annexe C du livre."},
 'link': [8, 'Le GPS du drone, en détail']},
]
