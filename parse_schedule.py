#!/usr/bin/env python3
"""Extrait le calendrier NBA 2026-27 du PDF officiel vers un JSON exploitable.

- ignore les colonnes DAY / LOCAL / NAT TV
- 'at X' => match a l'exterieur
- convertit l'heure ET en heure de Paris (gere les bascules d'heure d'ete)
- recupere les notes de salle (Paris, Manchester, Mexico, Austin)
"""
import json
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import pdfplumber

PDF = "2026-27-NBA-Regular-Season-Schedule-By-Team.pdf"
ET = ZoneInfo("America/New_York")
PARIS = ZoneInfo("Europe/Paris")

ROW = re.compile(
    r"^(\d+)\s+(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+"      # numero + jour (ignore)
    r"(\d{1,2}/\d{1,2}/\d{2})\s+"                        # date
    r"(.+?)\s+"                                          # adversaire
    r"(?:\d{1,2}:\d{2}\s*[AP]M)\s+"                      # LOCAL (ignore)
    r"(\d{1,2}:\d{2}\s*[AP]M)"                           # ET
    r"(?:\s+.*)?$"                                       # NAT TV (ignore)
)

# une "moitie" de ligne est un vrai match si elle porte une date ET une heure
LOOKS_LIKE_GAME = re.compile(r"\d{1,2}/\d{1,2}/\d{2}.*\d{1,2}:\d{2}\s*[AP]M")

VENUE = re.compile(
    r"GAMES? ON (.+?) TO BE PLAYED IN (.+?)(?=\s*(?:;|GAMES? ON |$))"
)

# les matchs de phase de groupes de l'Emirates NBA Cup sont ecrits en bleu
CUP_BLUE = (0.0, 0.439, 0.753)


def parse_cup_dates(page):
    """Dates (US) des matchs de poule de la NBA Cup, reperes a la couleur du texte."""
    blue = "".join(
        ch["text"] for ch in page.chars if ch.get("non_stroking_color") == CUP_BLUE
    )
    return set(re.findall(r"\d{1,2}/\d{1,2}/\d{2}", blue))


def to_paris(date_us: str, time_et: str):
    """'10/21/26' + '7:00 PM' (ET) -> (date ISO Paris, 'HH:MM' Paris)."""
    naive = datetime.strptime(f"{date_us} {time_et.replace(' ', '')}", "%m/%d/%y %I:%M%p")
    paris = naive.replace(tzinfo=ET).astimezone(PARIS)
    return paris.strftime("%Y-%m-%d"), paris.strftime("%H:%M")


def parse_venues(lines):
    """Les 'ARENA NOTES' -> {'2026-11-07': 'ARENA CDMX, MEXICO CITY', ...}"""
    buf, collecting = [], False
    for line in lines:
        if line.startswith("ARENA NOTE"):
            collecting = True
        elif line.startswith("NATIONAL TV"):
            collecting = False
        if collecting:
            buf.append(line)
    text = " ".join(buf).replace("•", " ")

    venues = {}
    for dates_part, place in VENUE.findall(text):
        for md in re.findall(r"(\d{1,2})/(\d{1,2})", dates_part):
            month, day = int(md[0]), int(md[1])
            year = 2026 if month >= 9 else 2027
            venues[f"{year}-{month:02d}-{day:02d}"] = place.strip().rstrip(".,")
    return venues


def main():
    teams = {}
    problems = []

    with pdfplumber.open(PDF) as pdf:
        for page in pdf.pages:
            lines = [l.strip() for l in page.extract_text().split("\n") if l.strip()]
            tricode, full_name = lines[0], lines[1]
            venues = parse_venues(lines)
            cup_dates = parse_cup_dates(page)
            games = []

            for line in lines[2:]:
                # deux colonnes de matchs separees par '#'
                for half in line.split("#"):
                    half = half.strip()
                    if not half:
                        continue
                    m = ROW.match(half)
                    if not m:
                        if LOOKS_LIKE_GAME.search(half):
                            problems.append(f"{tricode}: {half}")
                        continue  # texte libre (notes NBA Cup, salles, en-tetes)
                    num, date_us, opponent, et = m.groups()
                    away = opponent.startswith("at ")
                    opponent = opponent[3:] if away else opponent
                    date_fr, time_fr = to_paris(date_us, et)
                    us_iso = datetime.strptime(date_us, "%m/%d/%y").strftime("%Y-%m-%d")
                    game = {
                        "n": int(num),
                        "opp": opponent.strip(),
                        "away": away,
                        "date": date_fr,       # date a Paris
                        "time": time_fr,       # heure de Paris (HF)
                        "et": et.replace(" ", ""),
                    }
                    if us_iso in venues:
                        game["venue"] = venues[us_iso]
                    if date_us in cup_dates:
                        game["cup"] = True
                    games.append(game)

            games.sort(key=lambda g: (g["date"], g["time"]))
            teams[tricode] = {"name": full_name, "games": games}

    print(f"{len(teams)} equipes", file=sys.stderr)
    for tri, t in sorted(teams.items()):
        if len(t["games"]) != 80:
            print(f"  {tri}: {len(t['games'])} matchs  <-- inattendu", file=sys.stderr)
    counts = {len(t["games"]) for t in teams.values()}
    print(f"nb de matchs par equipe: {counts} (82 - 2 dates NBA Cup a determiner)", file=sys.stderr)

    if problems:
        print("Lignes non parsees:", file=sys.stderr)
        for p in problems:
            print("   " + p, file=sys.stderr)

    venues = {g.get("venue") for t in teams.values() for g in t["games"]} - {None}
    print(f"Salles neutres: {sorted(venues)}", file=sys.stderr)

    cup = {tri: sum(1 for g in t["games"] if g.get("cup")) for tri, t in teams.items()}
    odd = {tri: n for tri, n in cup.items() if n != 4}
    print(f"Matchs de poule NBA Cup par equipe: {sorted(set(cup.values()))}"
          + (f"  anomalies: {odd}" if odd else ""), file=sys.stderr)

    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(teams, f, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
