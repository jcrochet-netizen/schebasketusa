# Widget calendrier Ligue 1 2026-27

Calendrier de la saison, club par club, extrait du PDF officiel LFP
(`L1_MD_2627_CALENDRIER_SOMBRE_920e8f5afd.pdf`).

Même widget que le [calendrier NBA](../README.md), adapté au championnat.

## Intégration

Identique à la NBA : coller **`embed-wordpress.html`** dans un bloc « HTML
personnalisé ». Ne pas coller l'iframe seule — le contenu d'une iframe n'est pas
attribué à la page parente par Google.

URL de l'iframe : `https://jcrochet-netizen.github.io/schebasketusa/ligue1/`

Ouvrir sur un club précis : ajouter `?club=OM` (codes `PSG`, `OM`, `OL`, `LEN`,
`LIL`, `ASM`, `NIC`, `SRF`, `RCS`, `TFC`, `BRE`, `HAC`, `LMS`, `LOR`, `PFC`,
`AUX`, `ANG`, `TRO`). Un code inconnu retombe sur le PSG.

Le préfixe CSS est `.busa-l1` et le message de hauteur `busa-l1-height` : les deux
calendriers peuvent coexister sur une même page sans collision.

## Différences avec le calendrier NBA

| | NBA | Ligue 1 |
| --- | --- | --- |
| Horaires | convertis ET → heure française | **aucun horaire** dans le PDF |
| Regroupement | par mois | par mois, avec le numéro de journée |
| Équipes | 30, groupées par conférence | 18, liste alphabétique |
| Matchs | 82 (80 programmés) | 34 |

⚠️ **Le PDF de la LFP ne contient aucun horaire de coup d'envoi**, seulement la date
de journée (le samedi). Les jours et horaires réels sont fixés plus tard selon la
programmation TV, et une journée se dispute du vendredi au dimanche. Le widget et le
texte d'intro le disent explicitement pour ne pas induire le lecteur en erreur.

Si vous voulez les horaires exacts et leur mise à jour en cours de saison, il faudra
brancher SportMonks (ligue `301`, saison `28082`) sur le modèle décrit dans la mémoire
projet — un script serveur + une GitHub Action en cron.

## Logos

Aucun logo pour l'instant : chaque club affiche un **monogramme** à ses couleurs.
Pour les ajouter, déposer `logos/<CODE>.svg` (ou `.png`) et relancer le build.
Le widget reprend automatiquement les deux traitements de la version NBA : pastille
claire en mode sombre, pastille foncée pour un logo servi entièrement en blanc.

## Régénérer

```bash
python3 parse_schedule.py && python3 build_widget.py
```

- `parse_schedule.py` — lit le PDF, produit `schedule.json`
- `build_widget.py` — assemble `widget.css` + `widget.html` + `widget.js`
- `clubs.py` — noms, noms courts, codes, couleurs

## Contrôles automatiques

Vérifié sur les données produites :

- 34 journées, **306 matchs** (34 × 9)
- chaque club apparaît **exactement une fois par journée**
- **17 matchs à domicile et 17 à l'extérieur** pour les 18 clubs
- les **153 paires possibles** (C(18,2)) se rencontrent exactement deux fois,
  une fois chez chacun — zéro incohérence
- dates strictement croissantes, du 22/08/2026 au 29/05/2027
