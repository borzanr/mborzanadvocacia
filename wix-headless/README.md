# Site oficial no Wix Headless

Hospeda www.mborzanadvocacia.com.br desde 08/11/2026 (migração do site do editor Wix para
headless, mesmo plano Premium e domínio). As páginas continuam sendo geradas por
`tools/build.py`; este projeto Astro só as serve.

- `src/pages/[...slug].ts`: serve as páginas em `/contato`, `/sobre-nos`…, faz os 301 dos
  endereços antigos do Wix e envia os cabeçalhos de segurança.
- `src/site/` e `public/`: cópias geradas, fora do Git.
- `.env.local` (fora do Git): credenciais do projeto, criadas por `npx wix env pull`.

## Publicar uma alteração

```bash
python tools/wix_sync.py          # na raiz do repositório: gera e copia o site
cd wix-headless
npx wix build                     # o release NÃO faz build sozinho
npx wix release                   # publica em www.mborzanadvocacia.com.br
```

## Observações

- O Wix responde sozinho a `/robots.txt` e `/sitemap.xml` (este dá 404). O mapa do site
  está em `/mapa-do-site.xml`, enviado ao Search Console.
- Para voltar ao site antigo: painel do Wix › Configurações › Headless Settings › Switch back.
