"""Servidor local que imita o GitHub Pages: /pagina -> pagina.html, 404.html para o resto.
Uso: python tools/serve.py [porta]   (padrão 8090)"""
import http.server
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(DOCS), **k)

    def send_head(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        target = DOCS / path.lstrip("/")
        if path != "/" and not target.exists() and (DOCS / (path.strip("/") + ".html")).exists():
            self.path = path.rstrip("/") + ".html"
        elif path != "/" and not target.exists():
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            body = (DOCS / "404.html").read_bytes()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return None
        return super().send_head()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    print(f"http://localhost:{port}")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
