#!/usr/bin/env python3
"""Telecharge les logos des 18 clubs depuis le CDN de la LFP vers logos/.

Attention : la LFP ne publie que des logos MONOCHROMES BLANCS, prevus pour un
fond sombre. Verifie a l'analyse des pixels : 100% des pixels visibles sont
blancs. Le widget les pose donc sur une pastille foncee dans les deux themes.
Aucune variante couleur n'existe sur ce CDN (teste : L1/, color/, couleur/,
full/, official/, logos/, en .png et .svg -> 404), et il n'y a pas d'API publique.

Usage editorial. Les logos restent la propriete des clubs et de la LFP.
"""
import subprocess
import sys
from pathlib import Path

CDN = "https://ligue1.com/images/clubs/monochrome/L1/{nom}.webp"

# code interne -> nom de fichier chez la LFP
FICHIERS = {
    "ANG": "Angers",    "AUX": "Auxerre",   "BRE": "Brest",      "HAC": "Le-Havre",
    "LMS": "Le-Mans",   "LEN": "Lens",      "LIL": "Lille",      "LOR": "Lorient",
    "OL":  "Lyon",      "OM":  "Marseille", "ASM": "Monaco",     "NIC": "Nice",
    "PFC": "Paris_FC",  "PSG": "Paris",     "SRF": "Rennes",     "RCS": "Strasbourg",
    "TFC": "Toulouse",  "TRO": "Troyes",
}

OUT = Path("logos")


def main():
    OUT.mkdir(exist_ok=True)
    total = 0
    for code, nom in sorted(FICHIERS.items()):
        cible = OUT / f"{code}.webp"
        res = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "30", "-o", str(cible),
             "-w", "%{http_code}", CDN.format(nom=nom)],
            capture_output=True, text=True,
        )
        code_http = res.stdout.strip()[-3:]
        if code_http != "200" or not cible.exists() or cible.stat().st_size < 500:
            print(f"  !! {code} ({nom}) : HTTP {code_http}", file=sys.stderr)
            cible.unlink(missing_ok=True)
            continue
        total += cible.stat().st_size
        print(f"  {code:4} {nom:12} {cible.stat().st_size/1024:5.1f} Ko")

    n = len(list(OUT.glob("*.webp")))
    print(f"\n{n}/18 logos, {total/1024:.0f} Ko au total", file=sys.stderr)
    if n != 18:
        sys.exit(1)


if __name__ == "__main__":
    main()
