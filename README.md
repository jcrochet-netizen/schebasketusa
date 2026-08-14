# Widget calendrier NBA 2026-27 — BasketUSA

Calendrier de la saison régulière, franchise par franchise, extrait du PDF officiel NBA
(`2026-27-NBA-Regular-Season-Schedule-By-Team.pdf`, version du 13/08/2026).

## Intégration recommandée : GitHub Pages + iframe

C'est la méthode la plus robuste sur WordPress. Un `<iframe>` est **une seule balise,
sans `<script>` ni `<style>`** : il n'y a plus rien que `wpautop` puisse casser, ni que
le filtrage de contenu puisse vider. Le code s'exécute sur GitHub Pages, WordPress ne
fait que l'afficher.

Dépôt : https://github.com/jcrochet-netizen/schebasketusa

### 1. Activer GitHub Pages

https://github.com/jcrochet-netizen/schebasketusa/settings/pages
→ **Source : `Deploy from a branch` → branche `main` → dossier `/ (root)` → Save**

L'URL `https://jcrochet-netizen.github.io/schebasketusa/` répond après une minute.

### 2. Coller le bloc dans WordPress

Coller **`embed-wordpress.html`** en entier dans un bloc « HTML personnalisé ».
Ne pas coller l'iframe seule : voir la section SEO ci-dessous.

**Ouvrir sur une franchise précise** — utile pour les pages d'équipe : ajouter
`?team=LAL` à l'URL de l'iframe. Les 30 tricodes fonctionnent, majuscules ou non ;
un tricode inconnu retombe sur Atlanta.

## SEO et sécurité de l'intégration

Le contenu d'une iframe **n'est pas attribué à la page parente** par Google : il
appartient au domaine source (github.io). Une page qui ne contiendrait que l'iframe
serait donc quasi vide pour le référencement. `embed-wordpress.html` répond à ça :

| Point | Mise en œuvre |
| --- | --- |
| Contenu crawlable | H2 avec le mot-clé, ~290 mots d'intro, et **35 éléments de liste HTML réelle** : dates clés + premier match des 30 franchises (soit 60 mentions d'équipes indexables) |
| Pas de duplicate | la page de l'iframe est en `noindex,follow` — le contenu doit être attribué à BasketUSA, pas à github.io |
| Anti-CLS | `min-height:3300px`, mesuré sur le pire cas réel (mobile, 80 matchs = 3220 px) |
| Anti double-scroll mobile | `scrolling="no"` + `overflow:hidden`, la liste s'affiche en entier et c'est la page qui défile |
| Auto-hauteur | l'outil émet `postMessage({type:'busa-nba-height'})` au `load`, au `resize` et via `ResizeObserver` |
| Sécurité | le script parent vérifie `e.origin`, met la référence de l'iframe en cache avec repli, et valide la hauteur (`parseInt`, rejet si `<1`) |
| Autres attributs | `title` descriptif, `loading="lazy"`, `referrerpolicy="strict-origin-when-cross-origin"` |

**Le script parent est une amélioration progressive.** S'il est filtré par WordPress,
le `min-height` suffit à tout afficher sans rien tronquer. Le script remet
`min-height` à `0` dès qu'il connaît la hauteur exacte, sinon le plancher calculé
pour mobile laisserait un blanc sur desktop.

Garde-fous vérifiés en conditions réelles : origine pirate, mauvais type de message,
hauteur non numérique, nulle, négative, et `data` absent — les six sont ignorés,
le message légitime est bien appliqué.

Le site étant monolingue, les `hreflang` réciproques ne s'appliquent pas ici. Un
JSON-LD `ItemList` des dates clés reste possible si vous le souhaitez.

Le paramètre accepte les 30 tricodes (`ATL`, `BOS`, `LAL`…), en majuscules ou non.
Un tricode inconnu retombe sur Atlanta.

La page de l'iframe **épouse la hauteur qu'on lui donne** : c'est la liste des matchs
qui prend la place restante. Changer `height="700"` suffit, rien à recalculer.

### Mettre à jour plus tard

```bash
python3 build_widget.py && git commit -am "maj calendrier" && git push
```

Tous les articles qui affichent l'iframe sont à jour immédiatement, sans toucher à
WordPress. C'est l'autre gros avantage sur le copier-coller.

## Intégration alternative : coller le HTML — pas à pas

1. Ouvrir l'article dans l'éditeur de blocs (Gutenberg)
2. Ajouter un bloc **« HTML personnalisé »** (`/html` puis Entrée)
3. Ouvrir `widget-wordpress-inline.html`, tout sélectionner (`Cmd+A`), copier
4. Coller dans le bloc
5. Cliquer sur **« Aperçu »** dans le bloc pour vérifier, puis publier

C'est tout : le fichier contient le CSS, le HTML et le JS, il n'y a rien d'autre à faire.

### Les trois pièges à connaître

**Ne jamais repasser le contenu dans l'éditeur Visuel de l'ancien éditeur.** WordPress
y supprime les balises `<style>` et `<script>` et casse le widget définitivement. Avec
l'éditeur de blocs et un bloc « HTML personnalisé », il n'y a aucun risque : `wpautop`
ne s'applique pas à l'intérieur de ce bloc.

**Il faut être Administrateur ou Éditeur.** WordPress ne conserve `<script>` et
`<style>` que pour les comptes ayant le droit `unfiltered_html`. Un Auteur qui
enregistre l'article ensuite peut vider le bloc de son script. Sur une installation
multisite, seul le Super Admin a ce droit par défaut.

**Un seul widget par page.** Les identifiants HTML sont uniques : deux widgets collés
sur le même article se marcheraient dessus, le second ne réagirait pas.

### Si le widget doit servir sur beaucoup d'articles

Plutôt que de coller le bloc partout, créer une **composition synchronisée**
(anciennement « bloc réutilisable ») : sélectionner le bloc → menu ⋮ → « Créer une
composition », en cochant *Synchronisé*. Le widget s'insère ensuite en deux clics et
une seule modification le met à jour sur tous les articles.

Encore mieux pour un média : une extension maison exposant un shortcode
`[calendrier-nba]`, qui charge le CSS et le JS en fichiers séparés — donc mis en cache
une fois pour toutes au lieu d'être rechargés à chaque page vue.

## Les deux versions du widget

Dans les deux cas, tout le CSS est préfixé par `.busa-nba` et ne peut pas déborder
sur le thème.

| Version | Poids transféré | Logos |
| --- | --- | --- |
| **`widget-wordpress.html`** (recommandé) | **16 Ko** gzip | fichiers servis à part, 1 requête pour le logo affiché, mise en cache entre articles |
| `widget-wordpress-inline.html` | 104 Ko gzip | embarqués dans le HTML, aucun fichier à déposer |

La version recommandée est 6,5× plus légère. Elle demande une étape : déposer le
dossier `logos/` sur le serveur, puis renseigner `LOGO_BASE` dans `teams.py` :

```python
LOGO_BASE = "https://www.basketusa.com/wp-content/uploads/nba-logos/"
```

et relancer `python3 build_widget.py`.

⚠️ **WordPress refuse les SVG à l'upload par défaut** (raison de sécurité). Le plus
simple est de déposer le dossier par FTP ou via le gestionnaire de fichiers de
l'hébergeur, ce qui ne demande aucun plugin. Sinon, extension « Safe SVG ».

Si vous préférez ne rien déposer, prenez la version inline : elle marche telle quelle.

Options communes :

| Besoin | À faire |
| --- | --- |
| Ouvrir sur une franchise précise | ajouter l'ancre `#LAL` à l'URL de l'article |
| Forcer le mode clair (thème du site clair) | `<div class="busa-nba" data-busa-theme="light" ...>` |
| Élargir le widget | modifier `max-width:640px` dans `.busa-nba` |

Par défaut le widget suit le thème clair/sombre du visiteur.

## Logos des franchises

Les 30 logos officiels sont téléchargés depuis le CDN de la NBA par `fetch_logos.py`,
puis minifiés dans `logos/` (244 Ko au total, ~5 Ko par logo). Usage éditorial ; les
logos restent la propriété de la NBA et de ses franchises.

Deux traitements automatiques, déduits de l'analyse des couleurs de chaque SVG :

- **fond sombre** — les logos NBA sont dessinés pour un fond clair, ils sont donc posés
  sur une pastille claire en mode sombre (sans quoi les marques monochromes, comme
  celle d'Utah, disparaîtraient)
- **logos entièrement blancs** — la NBA ne sert le logo de Brooklyn qu'en blanc, prévu
  pour un fond noir. Il est détecté à la couleur et posé sur une pastille foncée dans
  les deux thèmes. La règle est générale, pas un cas particulier codé en dur.

Si un logo manque ou si son URL renvoie une erreur, le widget retombe automatiquement
sur un **monogramme** (tricode aux couleurs du club). Pour retirer volontairement une
équipe, l'ajouter à `LOGOS_MANQUANTS` dans `teams.py`.

## Régénérer

```bash
python3 fetch_logos.py && python3 parse_schedule.py && python3 build_widget.py
```

- `fetch_logos.py` — télécharge et minifie les 30 logos dans `logos/`
- `parse_schedule.py` — lit le PDF, produit `schedule.json`
- `build_widget.py` — produit les fichiers HTML
- `teams.py` — noms, surnoms, conférences, couleurs, `LOGO_BASE`

Dépendance : `pdfplumber`.

## Traitement des données

- colonnes `DAY`, `LOCAL` et `NAT TV` du PDF ignorées, comme demandé
- `at Orlando` → match à l'extérieur (✈️), sinon domicile (🏠)
- colonne `ET` convertie en **heure française** via `zoneinfo`, ce qui gère les quatre
  bascules d'heure d'été de la saison (les États-Unis et l'Europe ne changent pas
  d'heure aux mêmes dates : l'écart oscille entre +5 h et +6 h)
- un match du soir aux États-Unis bascule au lendemain en France ; il est daté au
  **jour français**, celui où le lecteur le regarde
- matchs de poule de l'Emirates NBA Cup détectés à la couleur du texte dans le PDF
- salles neutres récupérées depuis les « ARENA NOTES » (Paris, Manchester, Mexico, Austin)

## Contrôles automatiques

`parse_schedule.py` vérifie à chaque exécution :

- 30 équipes, **80 matchs chacune** (82 moins les 2 dates de décembre qui dépendent
  du parcours en NBA Cup et ne sont pas encore programmées)
- 4 matchs de poule de NBA Cup par équipe
- toute ligne du PDF contenant une date et une heure mais non interprétée est signalée

Contrôle croisé effectué : **1200 matchs uniques**, chacun présent des deux côtés
(domicile et extérieur) avec des date et heure identiques — zéro incohérence.
