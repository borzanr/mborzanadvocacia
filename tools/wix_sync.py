#!/usr/bin/env python3
"""Copia a versão oficial do site para o projeto Wix Headless (wix-headless/).

O site continua sendo gerado por tools/build.py; este script só leva o resultado para o
projeto Astro que o Wix hospeda:
  - páginas HTML  -> wix-headless/src/site/*.html  (servidas por src/pages/[...slug].ts)
  - assets, robots.txt e sitemap.xml -> wix-headless/public/

Uso:  python tools/wix_sync.py   (depois: cd wix-headless && npx wix build / wix release)
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROD = ROOT / "site-publicar"
WIX = ROOT / "wix-headless"


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools" / "build.py"), "--env", "production"], check=True)

    site = WIX / "src" / "site"
    if site.exists():
        shutil.rmtree(site)
    site.mkdir(parents=True)
    pages = sorted(PROD.glob("*.html"))
    for p in pages:
        shutil.copy(p, site / p.name)

    public = WIX / "public"
    if (public / "assets").exists():
        shutil.rmtree(public / "assets")
    shutil.copytree(PROD / "assets", public / "assets")
    for name in ("robots.txt", "sitemap.xml"):
        shutil.copy(PROD / name, public / name)
    # O Wix intercepta /robots.txt e /sitemap.xml no domínio oficial (o sitemap dá 404).
    # Este endereço passa: é o que vai no Editor de robots.txt do Wix e no Search Console.
    shutil.copy(PROD / "sitemap.xml", public / "mapa-do-site.xml")

    print(f"{len(pages)} páginas e assets copiados para {WIX}")


if __name__ == "__main__":
    main()
