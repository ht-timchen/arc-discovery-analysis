#!/usr/bin/env python3
"""
HTTP server with / mapped to index.html. Serves from site/ by default (repo root).
"""

from __future__ import annotations

import argparse
import http.server
import socketserver
import sys
from pathlib import Path
from urllib.parse import urlparse

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import paths as P


def make_handler_class(directory: Path):
    root = str(directory.resolve())

    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=root, **kwargs)

        def do_GET(self):
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            if path == "/":
                self.path = "/index.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    return CustomHTTPRequestHandler


def run_server(port: int = 8000, directory: Path | None = None) -> None:
    root = directory or P.SITE_DIR
    if not root.is_dir():
        print(f"Warning: directory does not exist yet: {root}", file=sys.stderr)
    Handler = make_handler_class(root)
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Server running at http://localhost:{port}")
        print(f"Serving files from: {root.resolve()}")
        print(f"Default page: http://localhost:{port}/ (index.html)")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def main() -> None:
    p = argparse.ArgumentParser(description="Serve the static site bundle")
    p.add_argument(
        "--directory",
        type=Path,
        default=P.SITE_DIR,
        help=f"Document root (default: {P.SITE_DIR})",
    )
    p.add_argument("--port", type=int, default=8000, help="Listen port")
    args = p.parse_args()
    run_server(port=args.port, directory=args.directory)


if __name__ == "__main__":
    main()
