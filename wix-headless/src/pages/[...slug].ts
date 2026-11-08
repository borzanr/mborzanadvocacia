// Serve as páginas do site (geradas por tools/build.py e copiadas por tools/wix_sync.py)
// com os mesmos endereços do site antigo no Wix: /contato, /sobre-nos, etc.
// Também faz os redirecionamentos 301 dos endereços antigos e põe os cabeçalhos de segurança.
import type { APIRoute } from "astro";

export const prerender = false;

const files = import.meta.glob("../site/*.html", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

const pages = new Map<string, string>();
for (const [path, html] of Object.entries(files)) {
  const name = path.split("/").pop()!.replace(/\.html$/, "");
  pages.set(name === "index" ? "" : name, html);
}
const notFound = pages.get("404") ?? "<h1>Página não encontrada</h1>";
pages.delete("404");

// Endereços do Wix antigo que não existem mais (301: o Google transfere a relevância).
const REDIRECTS: Array<[RegExp, string]> = [
  [/^book-online(\/.*)?$/, "/contato"],
  [/^service-page\/assessoria-trabalhista$/, "/direito-trabalhista"],
  [/^service-page(\/.*)?$/, "/areas-de-atuacao"],
  [/^blog(\/.*)?$/, "/"],
  [/^post(\/.*)?$/, "/areas-de-atuacao"],
  [/^(pages|blog-posts|blog-categories|booking-services)-sitemap\.xml$/, "/sitemap.xml"],
];

const SECURITY: Record<string, string> = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Content-Security-Policy": "frame-ancestors 'none'",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
};

const html = (body: string, status = 200) =>
  new Response(body, {
    status,
    headers: { "Content-Type": "text/html; charset=utf-8", ...SECURITY },
  });

const redirect = (to: string) =>
  new Response(null, { status: 301, headers: { Location: to, ...SECURITY } });

export const GET: APIRoute = ({ params }) => {
  const raw = params.slug ?? "";
  let slug: string;
  try {
    slug = decodeURIComponent(raw);
  } catch {
    slug = raw;
  }

  // /contato/ e /contato.html -> /contato
  if (slug.endsWith("/")) return redirect("/" + slug.replace(/\/+$/, ""));
  if (slug.endsWith(".html")) {
    const base = slug.slice(0, -5);
    if (pages.has(base === "index" ? "" : base)) return redirect(base === "index" ? "/" : "/" + base);
  }

  const page = pages.get(slug);
  if (page !== undefined) return html(page);

  for (const [re, to] of REDIRECTS) if (re.test(slug)) return redirect(to);

  return html(notFound, 404);
};
