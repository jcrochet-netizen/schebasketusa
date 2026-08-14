#!/usr/bin/env python3
"""Petit serveur statique pour tester le rendu exactement comme GitHub Pages.

Usage : python3 serve.py  puis http://localhost:8899/
(le module http.server lance en -m appelle os.getcwd(), bloque ici)
"""
import functools
import http.server
import socketserver
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent)
PORT = 8899

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
    print(f"http://localhost:{PORT}/  ->  {ROOT}", flush=True)
    httpd.serve_forever()
