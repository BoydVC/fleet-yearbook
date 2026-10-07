#!/usr/bin/env python3
"""Fleet Yearbook server on :4251 — serves web/, /api/yearbook.json and the PDF. Read-only."""
import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", 4251))

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=os.path.join(HERE, "web"), **k)
    def log_message(self, *a):
        pass
    def do_GET(self):
        p = self.path.split("?")[0]
        f = {"/api/yearbook.json": ("data/yearbook.json", "application/json"), "/fleet-yearbook.pdf": ("dist/fleet-yearbook.pdf", "application/pdf"),
             "/healthz": (None, "text/plain")}.get(p)
        if f:
            body = b"ok" if f[0] is None else open(os.path.join(HERE, f[0]), "rb").read()
            self.send_response(200); self.send_header("Content-Type", f[1]); self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body); return
        return super().do_GET()

if __name__ == "__main__":
    print(f"Fleet Yearbook on http://127.0.0.1:{PORT}/", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
