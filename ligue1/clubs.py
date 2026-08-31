"""Metadonnees des 18 clubs de Ligue 1 2026-27.

Comme pour la NBA, deux couleurs par club : une lisible sur fond clair, une sur
fond sombre. Les bleus marine (OL, PSG, Le Havre) disparaitraient en dark mode.
"""

# libelle du PDF : (nom, nom court (mobile), code, couleur claire, couleur sombre)
CLUBS = {
    "ANGERS SCO":             ("Angers SCO",            "Angers",     "ANG",  "#1A1A1A", "#E8EAED"),
    "AJ AUXERRE":             ("AJ Auxerre",            "Auxerre",    "AUX",  "#0B5BA8", "#4FA3E8"),
    "STADE BRESTOIS 29":      ("Stade Brestois 29",     "Brest",      "BRE",  "#D2001A", "#FF6B6E"),
    "LE HAVRE":               ("Le Havre AC",           "Le Havre",   "HAC",  "#0A4595", "#6FB4F0"),
    "LE MANS FC":             ("Le Mans FC",            "Le Mans",    "LMS",  "#8F6314", "#F2C230"),
    "RC LENS":                ("RC Lens",               "Lens",       "LEN",  "#D10012", "#FFE000"),
    "LOSC":                   ("LOSC Lille",            "LOSC",       "LIL",  "#C8102E", "#FF6B6E"),
    "FC LORIENT":             ("FC Lorient",            "Lorient",    "LOR",  "#C75300", "#FF9E42"),
    "OLYMPIQUE LYONNAIS":     ("Olympique Lyonnais",    "Lyon",       "OL",   "#0B3C8C", "#6E9BEF"),
    "OLYMPIQUE DE MARSEILLE": ("Olympique de Marseille", "Marseille", "OM",   "#0E7EB0", "#4FC3F7"),
    "AS MONACO":              ("AS Monaco",             "Monaco",     "ASM",  "#CE1126", "#FF6B7E"),
    "OGC NICE":               ("OGC Nice",              "Nice",       "NIC",  "#B01028", "#FF7A8A"),
    "PARIS FC":               ("Paris FC",              "Paris FC",   "PFC",  "#0057B8", "#5AA9E8"),
    "PARIS SAINT-GERMAIN":    ("Paris Saint-Germain",   "PSG",        "PSG",  "#004170", "#E8637A"),
    "STADE RENNAIS FC":       ("Stade Rennais FC",      "Rennes",     "SRF",  "#C6001C", "#FF6B6E"),
    "RC STRASBOURG ALSACE":   ("RC Strasbourg Alsace",  "Strasbourg", "RCS",  "#0B4EA2", "#5AA9E8"),
    "TOULOUSE FC":            ("Toulouse FC",           "Toulouse",   "TFC",  "#6A2C8F", "#B98FE0"),
    "ESTAC TROYES":           ("ESTAC Troyes",          "Troyes",     "TRO",  "#0F4C9A", "#5AA9E8"),
}

# Logos : meme principe que pour la NBA, fichiers servis a cote du widget.
# Un club sans logo affiche un monogramme a ses couleurs.
LOGO_BASE = "logos/"
LOGOS_MANQUANTS = set()
