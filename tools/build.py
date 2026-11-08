"""Gera o site estático de Mauro Borzan Advocacia em docs/.

Uso:
  python tools/build.py                   # prévia (noindex, faixa de prévia)
  python tools/build.py --env production  # versão final para www.mborzanadvocacia.com.br

Só biblioteca padrão. Conteúdo:
  src/pages/*.html   uma página por arquivo, com cabeçalho "---" (slug, title, description...)
  src/assets/        CSS, JS e imagens (copiados para docs/assets)
As páginas saem como <slug>.html, servidas pelo GitHub Pages em /<slug> (mesmas URLs do Wix).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
esc = html.escape

SITE = {
    "name": "Mauro Borzan Advocacia",
    "lawyer": "Mauro Borzan",
    "oab": "OAB/SP 531.932",
    "phone_e164": "5511917078365",
    "phone": "(11) 91707-8365",
    "email": "mborzan.adv@gmail.com",
    "street": "Rodovia Raposo Tavares, 22850, Sala 315",
    "district": "Lageadinho",
    "city": "Cotia",
    "state": "SP",
    "cep": "06709-015",
    "hours": "Segunda a sexta, das 9h às 18h",
    "maps": "https://www.google.com/maps/search/?api=1&query=Rodovia+Raposo+Tavares+22850+Cotia+SP",
    "facebook": "https://web.facebook.com/profile.php?id=61560640445558",
    "prod_url": "https://www.mborzanadvocacia.com.br",
    "preview_url": "https://mborzanadvocacia.borzanti.com",
}

NAV = [
    ("", "Início"),
    ("direito-do-passageiro-aereo", "Voos"),
    ("direito-do-consumidor", "Consumidor"),
    ("direito-trabalhista", "Trabalhista"),
    ("areas-de-atuacao", "Outras áreas"),
    ("sobre-nos", "Sobre"),
    ("contato", "Contato"),
]

ICONS = {
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.4.1-.6.3-.2.2-.8.8-.8 2s.8 2.3 1 2.5c.1.2 1.6 2.5 3.9 3.5 1.5.6 2 .7 2.7.6.4-.1 1.3-.5 1.5-1.1.2-.5.2-1 .1-1.1l-.5-.3Z"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
}


def wa(text: str) -> str:
    return f"https://wa.me/{SITE['phone_e164']}?text={quote(text)}"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8", newline="\n")


def front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[m.end():]


class Build:
    def __init__(self, env: str):
        self.prod = env == "production"
        self.base = SITE["prod_url"]          # canonical sempre no domínio oficial

    def href(self, slug: str) -> str:
        return "/" if slug == "" else f"/{slug}"

    def fill(self, body: str) -> str:
        def rep(m: re.Match) -> str:
            key, _, arg = m.group(1).partition(":")
            if key == "wa":
                return esc(wa(arg or "Olá, Dr. Mauro! Gostaria de falar sobre o meu caso."))
            if key == "icon":
                return ICONS[arg]
            if key == "link":
                return self.href(arg)
            if key == "tel":
                return f"tel:+{SITE['phone_e164']}"
            return esc(SITE[key])
        return re.sub(r"\{\{([a-z0-9_]+(?::[^}]*)?)\}\}", rep, body)

    def jsonld(self, meta: dict) -> str:
        org = {
            "@context": "https://schema.org",
            "@type": "LegalService",
            "@id": self.base + "/#escritorio",
            "name": SITE["name"],
            "url": self.base + "/",
            "image": self.base + "/assets/img/og-mauro-borzan.jpg",
            "logo": self.base + "/assets/img/logo.png",
            "telephone": "+" + SITE["phone_e164"],
            "email": SITE["email"],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": SITE["street"],
                "addressLocality": SITE["city"],
                "addressRegion": SITE["state"],
                "postalCode": SITE["cep"],
                "addressCountry": "BR",
            },
            "openingHoursSpecification": [{
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "09:00", "closes": "18:00",
            }],
            "areaServed": [{"@type": "City", "name": "Cotia"}, {"@type": "Country", "name": "Brasil"}],
            "knowsAbout": ["Direito do Passageiro Aéreo", "Direito do Consumidor", "Direito do Trabalho",
                           "Direito Previdenciário", "Direito de Família"],
            "employee": {
                "@type": "Person",
                "name": SITE["lawyer"],
                "jobTitle": "Advogado",
                "identifier": SITE["oab"],
                "image": self.base + "/assets/img/mauro-borzan.webp",
            },
            "sameAs": [SITE["facebook"]],
        }
        return json.dumps(org, ensure_ascii=False)

    def header(self, slug: str) -> str:
        links = []
        for s, label in NAV:
            cur = ' aria-current="page"' if s == slug else ""
            links.append(f'<a href="{self.href(s)}"{cur}>{label}</a>')
        links.append(f'<a class="btn btn-gold" href="{esc(wa("Olá, Dr. Mauro! Gostaria de falar sobre o meu caso."))}" target="_blank" rel="noopener">{ICONS["wa"]}WhatsApp</a>')
        bar = "" if self.prod else '<div class="preview-bar">Prévia do novo site, ainda não publicada no endereço oficial.</div>'
        return f"""{bar}<header class="top"><div class="wrap">
<a class="brand" href="/"><img src="/assets/img/monograma.png" alt="" width="44" height="44"><span><b>MAURO BORZAN</b><small>ADVOCACIA</small></span></a>
<button class="menu-btn" aria-label="Abrir menu" aria-expanded="false" aria-controls="menu">{ICONS["menu"]}</button>
<nav class="nav" id="menu" aria-label="Principal">{"".join(links)}</nav>
</div></header>"""

    def footer(self) -> str:
        s = SITE
        return f"""<footer class="foot"><div class="wrap">
<div class="foot-grid">
  <div class="stack" style="gap:14px">
    <a class="brand" href="/"><img src="/assets/img/monograma.png" alt="" width="44" height="44"><span><b>MAURO BORZAN</b><small>ADVOCACIA</small></span></a>
    <p>Dr. {s['lawyer']} · {s['oab']}<br>Atendimento presencial em Cotia e online para todo o Brasil.</p>
  </div>
  <div><h3>Contato</h3><ul>
    <li><a href="{esc(wa('Olá, Dr. Mauro! Gostaria de falar sobre o meu caso.'))}" target="_blank" rel="noopener">WhatsApp {s['phone']}</a></li>
    <li><a href="tel:+{s['phone_e164']}">Ligar: {s['phone']}</a></li>
    <li><a href="mailto:{s['email']}">{s['email']}</a></li>
    <li>{s['hours']}</li>
  </ul></div>
  <div><h3>Endereço</h3><ul>
    <li>{s['street']}<br>{s['district']}, {s['city']} – {s['state']}, CEP {s['cep']}</li>
    <li><a href="{esc(s['maps'])}" target="_blank" rel="noopener">Abrir no Google Maps</a></li>
    <li><a href="{esc(s['facebook'])}" target="_blank" rel="noopener">Facebook</a></li>
  </ul></div>
</div>
<div class="legal"><span>© {date.today().year} {s['name']} · {s['lawyer']}, {s['oab']}</span><span>Conteúdo informativo. Cada caso é analisado individualmente, sem promessa de resultado.</span></div>
</div></footer>
<a class="float-wa" href="{esc(wa('Olá, Dr. Mauro! Gostaria de falar sobre o meu caso.'))}" target="_blank" rel="noopener" aria-label="Conversar pelo WhatsApp">{ICONS["wa"]}WhatsApp</a>"""

    def page(self, meta: dict, body: str) -> str:
        slug = meta.get("slug", "")
        url = self.base + self.href(slug)
        title = meta["title"]
        desc = meta["description"]
        robots = "" if self.prod else '<meta name="robots" content="noindex, nofollow"><!-- PRÉVIA -->\n'
        preload = meta.get("preload", "")
        pre = f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">\n' if preload else ""
        return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{self.base}/assets/img/og-mauro-borzan.jpg">
<meta name="theme-color" content="#0a192f">
<link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600&family=Instrument+Sans:wght@400;500;600;700&display=swap">
{pre}<link rel="stylesheet" href="/assets/css/site.css?v={self.ver}">
<script type="application/ld+json">{self.jsonld(meta)}</script>
</head>
<body>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
{self.header(slug)}
<main id="conteudo">
{self.fill(body)}
</main>
{self.footer()}
<script src="/assets/js/site.js?v={self.ver}" defer></script>
</body>
</html>
"""

    def run(self) -> None:
        if OUT.exists():
            for p in OUT.iterdir():
                if p.name in ("CNAME", ".nojekyll"):
                    continue
                shutil.rmtree(p) if p.is_dir() else p.unlink()
        OUT.mkdir(exist_ok=True)
        shutil.copytree(SRC / "assets", OUT / "assets")
        h = hashlib.md5()
        for p in sorted((SRC / "assets").glob("*/*.*")):
            if p.suffix in (".css", ".js"):
                h.update(p.read_bytes())
        self.ver = h.hexdigest()[:8]
        urls = []
        for f in sorted((SRC / "pages").glob("*.html")):
            meta, body = front_matter(read(f))
            slug = meta.get("slug", "")
            name = "index.html" if slug == "" else ("404.html" if slug == "404" else f"{slug}.html")
            write(OUT / name, self.page(meta, body))
            if slug != "404":
                urls.append(self.base + self.href(slug))
        write(OUT / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
              + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
        if self.prod:
            write(OUT / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {self.base}/sitemap.xml\n")
            write(OUT / "CNAME", "www.mborzanadvocacia.com.br\n")
        else:
            write(OUT / "robots.txt", "# PRÉVIA: bloqueia indexação. Na versão oficial o build gera Allow + Sitemap.\nUser-agent: *\nDisallow: /\n")
            write(OUT / "CNAME", SITE["preview_url"].split("//")[1] + "\n")
        write(OUT / ".nojekyll", "")
        print(f"{len(urls)} páginas em {OUT} ({'produção' if self.prod else 'prévia'})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", choices=["staging", "production"], default="staging")
    Build(ap.parse_args().env).run()
