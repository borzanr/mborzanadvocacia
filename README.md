# Site — Mauro Borzan Advocacia

Nova versão do site **www.mborzanadvocacia.com.br** (hoje no Wix), feita a partir da análise em
`relatorio-site-mauro-borzan.html` (arquivo local, fora do Git). HTML e CSS estáticos, gerados por um script Python (só biblioteca padrão)
e pensados para o GitHub Pages.

- Prévia (quando publicada): **https://mborzanadvocacia.borzanti.com**, com `noindex`
- Produção (futuro): **https://www.mborzanadvocacia.com.br**

As páginas mantêm os mesmos endereços do Wix (`/direito-trabalhista`, `/sobre-nos`, `/contato`…), para não perder
o que o Google já conhece. Página nova: `/direito-do-consumidor`. A `/book-online` do Wix (com preços) não existe aqui.

## Estrutura

```
src/pages/*.html       uma página por arquivo, cabeçalho "---" com slug, title e description
src/assets/css/site.css  visual (paleta e fonte do site original: #0A192F, #B59410, Instrument Sans)
src/assets/js/site.js    menu do celular, botão flutuante e formulário → WhatsApp
src/assets/img/          imagens otimizadas (WebP)
tools/build.py           gera docs/
tools/serve.py           servidor local que imita o GitHub Pages (/pagina → pagina.html)
docs/                    site gerado (é o que o GitHub Pages publica)
_orig/                   imagens baixadas do Wix (fora do Git)
_gen/                    imagens originais do Higgsfield, em PNG (fora do Git)
```

Dados do escritório (telefone, OAB, endereço, horário) ficam no dicionário `SITE` em `tools/build.py`.
Nos textos das páginas: `{{wa:mensagem pronta}}`, `{{tel}}`, `{{phone}}`, `{{oab}}`, `{{hours}}`, `{{link:slug}}`, `{{icon:wa}}`.

## Uso

```bash
python tools/build.py                   # prévia (noindex + faixa "Prévia")
python tools/build.py --env production  # versão oficial (indexável, CNAME do domínio oficial)
python tools/serve.py                   # http://localhost:8090
```

## Imagens do Higgsfield (08/11/2026, ~18,75 créditos)

- `mauro-borzan.webp`: foto real do Mauro com o fundo trocado (Seedream 5.0 Pro). O fundo original tinha o
  logo da OAB Cotia, e o Provimento 205/2021 veda símbolos da OAB na publicidade. `mauro-borzan-claro.webp` é a
  alternativa com fundo claro.
- `topo-*.webp` e `area-*.webp`: cenas sem pessoas identificáveis (GPT Image 2.5), na paleta do site.

## Regras de conteúdo (OAB, Provimento 205/2021)

- Sem “especialista” até ele concluir a pós (está cursando consumidor/aviação).
- Sem promessa de resultado, sem preços, sem depoimentos de clientes.
- Nome e OAB/SP 531.932 em todas as páginas (rodapé).
- Não citar a Magitronic por enquanto.

## Para ir ao ar no domínio oficial

- [ ] Aprovação do Mauro (textos, foto e áreas).
- [ ] `python tools/build.py --env production` (remove `noindex`, troca `robots.txt` e `CNAME`).
- [ ] Apontar o DNS de `mborzanadvocacia.com.br` para o GitHub Pages e sair do Wix.
- [ ] Search Console: cadastrar o site e enviar `sitemap.xml`.
- [ ] Perfil da Empresa no Google apontando para o site.

## A confirmar

- Perfil da Empresa no Google, redes sociais usadas, horário exato (hoje “segunda a sexta, 9h às 18h”).
