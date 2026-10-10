# Snake en ligne de commande : document étudiant

Spécification fonctionnelle v1.1 et tickets de support

## Partie I : Spécification fonctionnelle

### 1. Objectif

Application de jeu Snake en ligne de commande. Le joueur choisit une direction à chaque tour, le serpent avance, le terminal est rafraîchi.

### 2. Règles du jeu

1. **Plateau** : rectangle de `W` colonnes et `H` lignes, entiers strictement positifs, sans borne maximale. Les cases sont repérées par `(ligne, colonne)`, à partir de 0 en haut à gauche.
2. **Serpent** : suite ordonnée de cases contiguës, la première étant la tête. Au départ, il a une longueur de 1, occupe la case `(H // 2, W // 2)` et n'a pas de direction.
3. **Pomme** : placée sur une case libre tirée au hasard avec un `random.Random` injecté. Le tirage se fait parmi les cases libres triées par ligne puis par colonne, pour être reproductible avec une graine fixe. S'il n'existe aucune case libre (par exemple en 1×1), aucune pomme n'est placée et la partie continue.
4. **Tour de jeu** : le joueur saisit une direction, le serpent avance d'une case. Le compteur de déplacements augmente de 1 à chaque tour, y compris pour le déplacement fatal. Il n'existe pas de déplacement invalide.
5. **Murs** : mortels. Si la nouvelle tête sort du plateau, c'est une défaite.
6. **Collision avec le corps** : c'est une défaite si la nouvelle tête arrive sur une case occupée par le serpent, **à l'exception de la queue**, qui libère sa case au moment où la tête avance. Conséquences :
   - le premier déplacement est toujours libre ;
   - à la longueur 2, le demi-tour est autorisé et échange la tête et la queue ;
   - à partir de la longueur 3, le demi-tour est mortel ;
   - poursuivre sa propre queue est sans danger (possible à partir de la longueur 4).
7. **Pomme mangée** : si la nouvelle tête est sur la pomme, le serpent grandit (sa queue n'est pas retirée) et le compteur de pommes augmente de 1. Si ce compteur est inférieur à 10, une nouvelle pomme est placée sur une case libre, calculée **après** l'ajout de la nouvelle tête.
8. **Victoire** : dès que 10 pommes ont été mangées. La partie s'arrête immédiatement et aucune nouvelle pomme n'est générée.
9. **Statut** : `PLAYING`, `WON` ou `LOST`.

### 3. Interface

**Écran de lancement**

```
=== SNAKE ===
Top scores
 #  Player                Apples  Moves  Grid
 1  carol                 10      41     6x6
 2  alice                 10      23     8x8
 3  bob                   7       31     10x10

(q = quit)
Width [8]:
Height [8]:
```

- Les lignes s'affichent dans cet ordre : titre, tableau, ligne vide, rappel `(q = quit)`, puis les invites `Width [8]:` et `Height [8]:` posées l'une après l'autre.
- Le tableau est relu depuis le fichier à chaque affichage de l'écran, sans cache. Il montre les 10 premiers scores. S'il n'y a aucun score, seule la ligne d'en-tête est affichée.
- La touche Entrée seule (ou une saisie réduite à des espaces) accepte la valeur par défaut (8). Les espaces autour de la saisie sont ignorés. Toute saisie qui n'est pas un entier strictement positif écrit en chiffres ASCII provoque une nouvelle invite, sans message d'erreur.
- `q` ou `Q` quitte l'application à chaque invite.
- Ctrl+C ou Ctrl+D à n'importe quelle invite quitte l'application proprement : un simple saut de ligne, sans trace d'erreur.

**Écran de jeu** (exemple en 8×3, après deux déplacements : un premier vers la gauche qui a mangé une pomme, puis un demi-tour vers la droite)

```
Moves: 2   Apples: 1
+--------+
|········|
|···0@···|
|······*·|
+--------+
Direction (h/b/g/d, q = abandon):
```

- Avant chaque saisie, le terminal est effacé (séquence ANSI `ESC[2J` suivie de `ESC[H`), puis l'écran est redessiné : ligne de compteurs, plateau, invite.
- Caractères : `·` (point médian U+00B7) pour une case vide, `@` pour la tête, `0` (chiffre zéro) pour le corps, `*` pour la pomme, `+`, `-` et `|` pour les murs. Priorité d'affichage quand deux éléments coïncident : tête, corps, pomme.
- Touches : `h` (haut), `b` (bas), `g` (gauche), `d` (droite), insensibles à la casse, validées par Entrée (`input()`). `q` (ou `Q`) abandonne la partie. Toute autre saisie (y compris vide, ou entourée d'espaces) provoque une nouvelle invite, après effacement et redessin de l'écran, sans effet sur les compteurs.
- Le point d'entrée force l'encodage UTF-8 de la sortie standard (`sys.stdout.reconfigure`).

**Fin de partie** : le plateau n'est pas redessiné et le terminal n'est pas effacé. Le programme affiche le message de victoire (`You won!`) ou de défaite (`Game over.`), rappelle les deux compteurs (même format que l'écran de jeu), puis pose l'invite `Player name:`. Le score est ensuite enregistré, sans message de confirmation, et l'application revient à l'écran de lancement. Un **abandon** (`q`) n'enregistre aucun score et ramène directement à l'écran de lancement.

### 4. Scores

- Fichier `scores.json` situé à côté de l'application, créé s'il n'existe pas. Il contient une liste d'objets.
- Champs d'une entrée : `player`, `apples`, `moves`, `width`, `height`, `date` (ISO 8601, à la seconde).
- **Nom** : les espaces de début et de fin sont retirés ; un nom vide (y compris un nom qui n'était composé que d'espaces) devient `anonymous` ; le résultat est tronqué à 20 caractères. Cette normalisation est faite dans le ViewModel.
- **Classement** : pommes décroissantes, puis surface `W × H` croissante, puis déplacements croissants, puis date croissante. Il est global, toutes tailles de grille confondues.
- **Enregistrement** : cycle de lecture de toutes les entrées, ajout de la nouvelle, réécriture complète du fichier.
- **Fichier corrompu** : est corrompu un fichier dont le contenu n'est pas du JSON valide, ou n'est pas une liste d'objets possédant exactement les six champs ci-dessus avec les types attendus (chaînes pour `player` et `date`, entiers pour les autres). Un avertissement est émis par le module `warnings` (sortie d'erreur) et le contenu est traité comme vide. Avec la configuration par défaut de Python, cet avertissement n'apparaît qu'une fois par session. Le fichier n'est écrasé qu'à la sauvegarde suivante, qui perd donc son ancien contenu.
- **Tableau** : colonnes `#`, `Player`, `Apples`, `Moves`, `Grid` (format `WxH`), séparées par deux espaces. Largeurs fixes : 2 (alignée à droite), 20, 6, 5, libre. Les quatre premières colonnes sont complétées par des espaces à droite (sauf `#`, complétée à gauche) ; un texte plus long que sa colonne n'est pas tronqué et décale la suite de la ligne.

### 5. Architecture MVVM

| Couche | Fichier | Responsabilité |
| --- | --- | --- |
| Model | `game_model.py` | `Direction`, `GameStatus`, `GameModel` : état, déplacement, collisions, pomme, victoire |
| Model | `score_repository.py` | `ScoreEntry`, `ScoreRepository` : lecture, écriture et classement du JSON |
| ViewModel | `game_view_model.py` | Compteurs, plateau sous forme de lignes de texte, statut ; traduction des touches ; normalisation du nom ; enregistrement du score |
| ViewModel | `launch_view_model.py` | Mise en forme du tableau des scores ; détection de la touche de sortie ; validation des dimensions saisies |
| View | `launch_view.py` | Écran de lancement |
| View | `game_view.py` | Boucle de jeu, affichage, saisies |
| View | `main.py` | Point d'entrée et composition des dépendances : seul fichier qui instancie les classes du Model pour les injecter dans les ViewModels ; gère l'interruption clavier (Ctrl+C, Ctrl+D) |

Les dépendances vont de la View vers le ViewModel puis vers le Model. Le Model ne connaît ni le ViewModel ni la View. Hors de la composition des dépendances dans `main.py`, la View ne manipule jamais le Model directement : `launch_view.py` et `game_view.py` n'importent que des ViewModels.

### 6. Tests

Des tests unitaires (`unittest`) couvrent la couche Model : état initial, déplacements, croissance, collisions, victoire, placement de la pomme et dépôt de scores (fichiers temporaires).

## Partie II : Tickets de support

Les tickets ci-dessous ont été remontés par des utilisateurs. Ils décrivent ce que ces personnes ont observé, avec leurs mots : leurs descriptions peuvent être imprécises, incomplètes, voire en partie inexactes. À vous de reproduire, diagnostiquer et corriger.

### Ticket #214 : Des joueurs à 0 pomme en haut du classement

- **Signalé par** : Camille Renaudin
- **Date** : 2026-09-14 à 18:42
- **Priorité perçue** : moyenne

Bonjour,

J'ai lancé le jeu plusieurs soirs de suite avec des amis. Parfois, en regardant le tableau des meilleurs scores, je vois des joueurs avec 0 pomme placés tout en haut, au-dessus de gens qui ont réussi à manger 7 pommes. Ça n'a aucun sens pour moi : un score à 0 ne devrait pas être devant.

Ça ne m'arrive pas à chaque fois. Je dirais une fois sur deux ou trois selon les jours. Je me demande si le classement n'est pas simplement mélangé quand il y a trop de monde dans la liste.

Merci de regarder ça, c'est un peu gênant quand on veut se comparer entre nous !

### Ticket #217 : Les touches de direction ne marchent qu'en minuscules

- **Signalé par** : Mathis Delaporte
- **Date** : 2026-09-16 à 21:07
- **Priorité perçue** : haute

Salut,

Les touches de direction (h, b, g, d) sont sensibles à la casse. En minuscule, le serpent avance normalement. Si je tape la même lettre en majuscule (H, B, G ou D), rien ne se passe : pas de message, pas de mouvement, le compteur de déplacements reste identique et le jeu me redemande simplement une direction.

### Ticket #221 : Je sors du plateau ou je meurs sur des murs qu'on ne voit pas

- **Signalé par** : Inès Marchetti
- **Date** : 2026-09-21 à 09:55
- **Priorité perçue** : haute

Bonjour,

Je vous écris car j'ai un comportement très étrange avec le plateau. Il m'arrive de lancer une partie et de ne pas voir mon serpent au départ. Et puis je joue quand même, et soudain la partie se termine alors que je n'étais visiblement pas près d'un mur. D'autres fois, j'ai l'impression que mon serpent sort du cadre dessiné.

C'est aléatoire : certaines parties se passent parfaitement bien, d'autres sont complètement incompréhensibles. Je pensais que c'était lié à un problème de rafraîchissement du terminal, parce que mon terminal est assez petit.

Je n'ai pas réussi à trouver ce qui déclenche le problème. Pouvez-vous regarder ?

### Ticket #226 : Les caractères accentués abîment le tableau des scores

- **Signalé par** : Baptiste Okonkwo
- **Date** : 2026-09-28 à 20:31
- **Priorité perçue** : basse

Bonjour,

Je m'appelle José et j'ai voulu saisir mon prénom à la fin d'une partie. Au retour sur l'écran de lancement, mon nom apparaît avec des petits symboles bizarres à la place de la lettre accentuée, et le reste de la ligne est décalé par rapport aux autres.

J'ai ensuite fait une deuxième partie sous un autre nom. Cette fois, ça s'est aggravé : le nom de ma première partie est toujours abîmé. Une amie a essayé avec un petit smiley dans son pseudo et c'est encore pire.

Je soupçonne mon terminal de ne pas gérer correctement les accents, même si les autres programmes les affichent bien. Je ne sais pas si le problème vient de la saisie ou de l'affichage.
