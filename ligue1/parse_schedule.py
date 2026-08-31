#!/usr/bin/env python3
"""Extrait le calendrier de Ligue 1 2026-27 du PDF officiel LFP vers un JSON.

Le PDF presente 3 journees par ligne, sur 2 pages (aller / retour). Le texte
extrait fusionne les colonnes : on decoupe donc sur la position du separateur
'/', toujours a la meme abscisse pour une colonne donnee.

Le PDF ne contient aucun horaire de coup d'envoi : la LFP ne publie que la date
de journee, les horaires etant fixes plus tard selon la programmation TV.
"""
import json
import re
import sys
import unicodedata
from datetime import date

import pdfplumber

PDF = "L1_MD_2627_CALENDRIER_SOMBRE_920e8f5afd.pdf"

# frontieres des 3 colonnes de journees (le '/' tombe a x ~115, ~296, ~478)
BORNES = (200, 400)

MOIS = {
    "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11,
    "decembre": 12,
}

RE_JOURNEE = re.compile(r"^(\d+)\s*(?:ERE|EME)\s+JOURNEE\s+(.+)$")
RE_DATE = re.compile(r"([A-Z]+)\s+(\d{1,2})\s+([A-Z]+)\s+(\d{4})")


def sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def colonne(x):
    return 0 if x < BORNES[0] else (1 if x < BORNES[1] else 2)


def lire_date(txt):
    m = RE_DATE.search(txt)
    if not m:
        return None
    _, jour, mois, annee = m.groups()
    mois = MOIS.get(mois.lower())
    return date(int(annee), mois, int(jour)).isoformat() if mois else None


def main():
    journees = {}

    with pdfplumber.open(PDF) as pdf:
        for page in pdf.pages:
            lignes = {}
            for w in page.extract_words():
                lignes.setdefault(round(w["top"] / 3), []).append(w)

            courante = {}  # colonne -> numero de journee
            for cle in sorted(lignes):
                mots = sorted(lignes[cle], key=lambda a: a["x0"])
                cols = {0: [], 1: [], 2: []}
                for w in mots:
                    cols[colonne(w["x0"])].append(w)

                for ci, ws in cols.items():
                    if not ws:
                        continue
                    txt = sans_accents(" ".join(w["text"] for w in ws)).upper()
                    txt = re.sub(r"\s+", " ", txt).strip()

                    m = RE_JOURNEE.match(txt)
                    if m:  # en-tete de journee
                        num = int(m.group(1))
                        courante[ci] = num
                        journees[num] = {"date": lire_date(m.group(2)),
                                         "matchs": []}
                        continue

                    # une rencontre : "DOMICILE / EXTERIEUR"
                    barres = [i for i, w in enumerate(ws) if w["text"] == "/"]
                    if len(barres) != 1 or ci not in courante:
                        continue
                    i = barres[0]
                    dom = " ".join(w["text"] for w in ws[:i]).strip()
                    ext = " ".join(w["text"] for w in ws[i + 1:]).strip()
                    if dom and ext:
                        journees[courante[ci]]["matchs"].append(
                            {"dom": dom, "ext": ext})

    # ---- controles ----
    print(f"{len(journees)} journees", file=sys.stderr)
    for n in sorted(journees):
        j = journees[n]
        if len(j["matchs"]) != 9 or not j["date"]:
            print(f"  !! J{n}: {len(j['matchs'])} matchs, date={j['date']}",
                  file=sys.stderr)

    clubs = sorted({c for j in journees.values() for m in j["matchs"]
                    for c in (m["dom"], m["ext"])})
    print(f"{len(clubs)} clubs distincts", file=sys.stderr)
    for c in clubs:
        print("   " + c, file=sys.stderr)

    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump({"journees": journees}, f, ensure_ascii=False,
                  separators=(",", ":"))


if __name__ == "__main__":
    main()
