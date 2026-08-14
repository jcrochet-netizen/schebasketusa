#!/usr/bin/env python3
"""Telecharge les logos officiels des 30 franchises depuis le CDN de la NBA,
puis les minifie dans logos/.

Usage editorial (BasketUSA est un media) : les logos restent la propriete
de la NBA et de ses franchises.
"""
import re
import subprocess
import sys
from pathlib import Path

CDN = "https://cdn.nba.com/logos/nba/{id}/primary/L/logo.svg"

TEAM_IDS = {
    "ATL": 1610612737, "BOS": 1610612738, "CLE": 1610612739, "NOP": 1610612740,
    "CHI": 1610612741, "DAL": 1610612742, "DEN": 1610612743, "GSW": 1610612744,
    "HOU": 1610612745, "LAC": 1610612746, "LAL": 1610612747, "MIA": 1610612748,
    "MIL": 1610612749, "MIN": 1610612750, "BKN": 1610612751, "NYK": 1610612752,
    "ORL": 1610612753, "IND": 1610612754, "PHI": 1610612755, "PHX": 1610612756,
    "POR": 1610612757, "SAC": 1610612758, "SAS": 1610612759, "OKC": 1610612760,
    "TOR": 1610612761, "UTA": 1610612762, "MEM": 1610612763, "WAS": 1610612764,
    "DET": 1610612765, "CHA": 1610612766,
}

OUT = Path("logos")


def minify(svg: str) -> str:
    svg = re.sub(r"<\?xml.*?\?>", "", svg, flags=re.S)
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<!DOCTYPE.*?>", "", svg, flags=re.S)
    svg = re.sub(r">\s+<", "><", svg)
    return re.sub(r"\s{2,}", " ", svg).strip()


def main():
    OUT.mkdir(exist_ok=True)
    total = 0
    for tri, tid in sorted(TEAM_IDS.items()):
        url = CDN.format(id=tid)
        res = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "30", "-w", "%{http_code}", url],
            capture_output=True, text=True,
        )
        body, code = res.stdout[:-3], res.stdout[-3:]
        if code != "200" or "<svg" not in body:
            print(f"  !! {tri}: HTTP {code}", file=sys.stderr)
            continue
        svg = minify(body)
        (OUT / f"{tri}.svg").write_text(svg, encoding="utf-8")
        total += len(svg.encode())
        print(f"  {tri}  {len(svg.encode())/1024:5.1f} Ko")

    n = len(list(OUT.glob("*.svg")))
    print(f"\n{n}/30 logos, {total/1024:.0f} Ko au total", file=sys.stderr)
    if n != 30:
        sys.exit(1)


if __name__ == "__main__":
    main()
