"""Metadonnees des 30 franchises : nom FR, conference, couleur d'accent.

Deux couleurs par equipe : une lisible sur fond clair, une sur fond sombre.
Beaucoup de primaires officielles sont des bleus marine tres sombres
(Denver, Utah, Minnesota...) : elles disparaitraient en dark mode, on bascule
alors sur la couleur secondaire officielle (or, orange, vert).
"""

# tricode: (nom, surnom court (mobile), conference, couleur clair, couleur sombre)
# les 30 surnoms sont uniques dans la ligue : aucun risque d'ambiguite.
TEAMS = {
    "ATL": ("Atlanta Hawks",          "Hawks",        "E", "#C8102E", "#FF6B6E"),
    "BOS": ("Boston Celtics",         "Celtics",      "E", "#007A33", "#3FCB78"),
    "BKN": ("Brooklyn Nets",          "Nets",         "E", "#1A1A1A", "#E8EAED"),
    "CHA": ("Charlotte Hornets",      "Hornets",      "E", "#1D1160", "#3FC7D8"),
    "CHI": ("Chicago Bulls",          "Bulls",        "E", "#CE1141", "#FF5F79"),
    "CLE": ("Cleveland Cavaliers",    "Cavaliers",    "E", "#860038", "#FDBB30"),
    "DET": ("Detroit Pistons",        "Pistons",      "E", "#C8102E", "#FF6B7E"),
    "IND": ("Indiana Pacers",         "Pacers",       "E", "#002D62", "#FDBB30"),
    "MIA": ("Miami Heat",             "Heat",         "E", "#98002E", "#F9A01B"),
    "MIL": ("Milwaukee Bucks",        "Bucks",        "E", "#00471B", "#4FBF6E"),
    "NYK": ("New York Knicks",        "Knicks",       "E", "#0057A8", "#F58426"),
    "ORL": ("Orlando Magic",          "Magic",        "E", "#0077C0", "#4FB0E8"),
    "PHI": ("Philadelphia 76ers",     "76ers",        "E", "#0057A8", "#5AA9E8"),
    "TOR": ("Toronto Raptors",        "Raptors",      "E", "#CE1141", "#FF5F79"),
    "WAS": ("Washington Wizards",     "Wizards",      "E", "#002B5C", "#F05A72"),
    "DAL": ("Dallas Mavericks",       "Mavericks",    "O", "#00538C", "#5AA9E8"),
    "DEN": ("Denver Nuggets",         "Nuggets",      "O", "#0E2240", "#FEC524"),
    "GSW": ("Golden State Warriors",  "Warriors",     "O", "#1D428A", "#FFC72C"),
    "HOU": ("Houston Rockets",        "Rockets",      "O", "#CE1141", "#FF5F79"),
    "LAC": ("Los Angeles Clippers",   "Clippers",     "O", "#C8102E", "#FF6B7E"),
    "LAL": ("Los Angeles Lakers",     "Lakers",       "O", "#552583", "#FDB927"),
    "MEM": ("Memphis Grizzlies",      "Grizzlies",    "O", "#4C6BA5", "#8FAEE0"),
    "MIN": ("Minnesota Timberwolves", "Timberwolves", "O", "#0C2340", "#8FD44A"),
    "NOP": ("New Orleans Pelicans",   "Pelicans",     "O", "#0C2340", "#D4B876"),
    "OKC": ("Oklahoma City Thunder",  "Thunder",      "O", "#007AC1", "#4FB0E8"),
    "PHX": ("Phoenix Suns",           "Suns",         "O", "#1D1160", "#F07C2E"),
    "POR": ("Portland Trail Blazers", "Trail Blazers","O", "#C8102E", "#FF6B6E"),
    "SAC": ("Sacramento Kings",       "Kings",        "O", "#5A2D81", "#A97FD8"),
    "SAS": ("San Antonio Spurs",      "Spurs",        "O", "#2A2E33", "#C4CED4"),
    "UTA": ("Utah Jazz",              "Jazz",         "O", "#002B5C", "#F9A01B"),
}

# libelle 'OPPONENT' du PDF -> tricode
OPP_TO_TRI = {
    "Atlanta": "ATL", "Boston": "BOS", "Brooklyn": "BKN", "Charlotte": "CHA",
    "Chicago": "CHI", "Cleveland": "CLE", "Dallas": "DAL", "Denver": "DEN",
    "Detroit": "DET", "Golden State": "GSW", "Houston": "HOU", "Indiana": "IND",
    "LA Clippers": "LAC", "LA Lakers": "LAL", "Memphis": "MEM", "Miami": "MIA",
    "Milwaukee": "MIL", "Minnesota": "MIN", "New Orleans": "NOP",
    "New York": "NYK", "Oklahoma City": "OKC", "Orlando": "ORL",
    "Philadelphia": "PHI", "Phoenix": "PHX", "Portland": "POR",
    "Sacramento": "SAC", "San Antonio": "SAS", "Toronto": "TOR",
    "Utah": "UTA", "Washington": "WAS",
}

# Prefixe d'URL des logos, utilise par la version "liee" du widget.
# En local, "logos/" permet de previsualiser directement.
# Sur BasketUSA, remplacer par l'URL du dossier une fois les fichiers deposes,
# par ex. "https://www.basketusa.com/wp-content/uploads/nba-logos/".
# Le widget construit l'URL finale ainsi : LOGO_BASE + tricode + ".svg"
LOGO_BASE = "logos/"

# Equipes sans logo (le widget retombe alors sur le monogramme couleur).
LOGOS_MANQUANTS = set()

# salle neutre du PDF -> libelle court affiche dans le widget
VENUE_LABELS = {
    "ACCOR ARENA, PARIS": "Paris",
    "CO-OP LIVE, MANCHESTER": "Manchester",
    "ARENA CDMX, MEXICO CITY": "Mexico",
    "MOODY CENTER, AUSTIN, TX": "Austin",
}
