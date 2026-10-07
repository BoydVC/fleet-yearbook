#!/usr/bin/env python3
"""Build dist/fleet-yearbook-snapshot.html (offline, self-contained: CSS, JS, data, fonts inlined)
and dist/fleet-yearbook.pdf (headless Chrome print of ?print=1, US Letter, one yearbook page per sheet)."""
import base64, json, os, subprocess, sys, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
G = "/usr/share/fonts/truetype/sand-box/google/"
FONTS = [("Caveat", "Caveat/Caveat-VariableFont_wght.ttf", "normal", "400 700"),
         ("Oswald", "Oswald/Oswald-VariableFont_wght.ttf", "normal", "200 700"),
         ("Playfair Display", "Playfair Display/PlayfairDisplay-VariableFont_wght.ttf", "normal", "400 900"),
         ("Playfair Display", "Playfair Display/PlayfairDisplay-Italic-VariableFont_wght.ttf", "italic", "400 900"),
         ("UnifrakturMaguntia", "UnifrakturMaguntia/UnifrakturMaguntia-Regular.ttf", "normal", "400")]

def snapshot():
    w = lambda n: open(os.path.join(HERE, "web", n), encoding="utf-8").read()
    safe = lambda s: s.replace("</script", "<\\/script")
    data = json.load(open(os.path.join(HERE, "data", "yearbook.json")))
    css = ""
    for fam, f, style, wt in FONTS:
        p = G + f
        if os.path.exists(p):
            css += f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{wt};src:url(data:font/ttf;base64,{base64.b64encode(open(p,'rb').read()).decode()}) format('truetype')}}\n"
    html = w("index.html")
    html = html.replace("<!--FONTS-->", f"<style>{css}</style>")
    html = html.replace('<link rel="stylesheet" href="style.css">', "<style>\n" + w("style.css") + "\n</style>")
    html = html.replace("<!--INLINE-DATA-->", "<script>window.__YB__=" + safe(json.dumps(data, separators=(",", ":"))) + ";window.__YB_PDF__='fleet-yearbook.pdf';</script>")
    for js in ("portrait.js", "app.js"):
        html = html.replace(f'<script src="{js}"></script>', "<script>\n" + safe(w(js)) + "\n</script>")
    out = os.path.join(HERE, "dist", "fleet-yearbook-snapshot.html")
    open(out, "w", encoding="utf-8").write(html)
    print(out, f"{os.path.getsize(out)/1024:.0f} KB")

def pdf(port=4251):
    d = tempfile.mkdtemp(prefix="fy-pdf-")
    out = os.path.join(HERE, "dist", "fleet-yearbook.pdf")
    try:
        subprocess.run(["nice", "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", f"--user-data-dir={d}",
                        "--no-pdf-header-footer", "--virtual-time-budget=6000", f"--print-to-pdf={out}",
                        f"http://127.0.0.1:{port}/?print=1"], check=True, capture_output=True, timeout=240)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(out, f"{os.path.getsize(out)/1024:.0f} KB")

if __name__ == "__main__":
    snapshot()
    if "--no-pdf" not in sys.argv:
        pdf()
