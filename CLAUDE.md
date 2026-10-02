# CLAUDE.md

Portal da Transparência independente de Nerópolis/GO. ETL em Python (somente stdlib) gera JSON estático, que o Angular 20 consome; hospedagem no GitHub Pages. Não há backend nem banco. O plano original fica fora do repo, mas as decisões dele estão em `docs/`.

## Comandos

```bash
python3 -m etl                                  # coleta real (SICONFI e Transferegov não exigem token)
python3 -m unittest discover -s etl/tests       # rodar SEMPRE da raiz do repo
cd frontend && npm ci && npx ng build           # build de produção (padrão)
npx ng serve                                    # dev, http://localhost:4200
npx ng build --base-href /portal-transparencia-neropolis/   # igual ao deploy
```

- Não existe `ng test` nem lint configurados; não invente esses comandos.
- `gh` pode não estar autenticado: faça push da branch, entregue o link `.../pull/new/<branch>` e a descrição do PR num arquivo do scratchpad.

## Regras do projeto

- **O frontend nunca chama APIs governamentais.** Só lê `frontend/public/data/**` via `core/data.service.ts`.
- **Todo número exibido tem fonte:** `sourceUrl` aponta para a consulta original na API. Mantenha isso ao criar dados novos.
- **Nunca fabricar valor.** Na ausência de dado, use `null` ou o texto "não informado". Exemplo: relatório de gestão "em elaboração" tem valor 0 provisório na fonte, e o portal mostra `reportedExecuted: null`.
- **Correlação indireta registra `strategy` e `confidence`** e é sinalizada na UI com `<app-info term="confianca-vinculo">`. Divergência entre fontes é exibida, não escondida.
- **A UI segue como "versão de homologação"** (banner em `app.component.html`) até ser decidido o contrário.
- **Falha de fonte não derruba o ETL.** A fonte fica `FAILED`, mantém a última versão de `data/normalized/<dataset>.json` e o restante segue. Sem token, a fonte é `SKIPPED`.
- Nenhum token no código; o único segredo previsto é `TRANSPARENCIA_API_TOKEN` (GitHub Secret).
- Texto da UI, docs e commits em pt-BR. Commits seguem Conventional Commits com escopo (`feat(etl):`, `feat(frontend):`, `ci:`, `data:`, `docs:`) e são separados por assunto. Dados regenerados vão em commit `data:` próprio.

## Identificadores

- IBGE `5214507` (filtro do SICONFI). CNPJ da Prefeitura `01105626000125` (filtro do Transferegov).
- Fundos municipais (saúde, meio ambiente) podem ter outro CNPJ; buscar só pelo CNPJ da Prefeitura pode deixar emendas de fora (ver `docs/correlation-rules.md`).

## Fontes: armadilhas conhecidas

**SICONFI** (`apidatalake.tesouro.gov.br/ords/siconfi/tt/dca`)
- Use a DCA (anual), não o RREO: o RREO não distingue função de subfunção pelo `cod_conta`.
- Anexo I-C (receitas):
  - coluna `Receitas Brutas Realizadas`;
  - total em `cod_conta = ReceitasExcetoIntraOrcamentarias`;
  - contas com prefixo `RO`; o prefixo `RI` (intra) é ignorado.
- O ementário de receitas **mudou em 2022**. Exemplo: FPM era `1.7.1.8.01.x` e passou a `1.7.1.1.51`. Os níveis `1.7.1` (União), `1.7.2` (Estado) e `1.7.5` (FUNDEB) são estáveis. Destaques usam listas de códigos alternativos (`HIGHLIGHTS`).
- Anexo I-E: funções têm o formato `NN - Nome`, subfunções `NN.SSS - Nome` e o resto `FUNN - Demais Subfunções`. Todas as linhas usam `cod_conta = TotalDespesas`.
- Anexo I-D:
  - `DO` e `DI` (intraorçamentária) **entram os dois na árvore**, porque os totais dos grupos incluem ambos;
  - por isso o total por natureza é maior que o total por função; os percentuais usam `natures.paid`.
- A API troca travessões e aspas por `¿`; `clean_name()` corrige.
- O exercício só aparece depois que a Prefeitura envia a DCA (até 30/04 do ano seguinte).

**SICONFI MSC** (`.../tt/msc_orcamentaria`, classe 6, `ending_balance`, uma chamada por mês)
- Sinal pela `natureza_conta`: C soma, D subtrai. Empenhado = contas `6221301`–`07`; liquidado = `03`, `04`, `07`; pago = `04`.
- Exclua a modalidade 91 (`natureza_despesa[2:4]`) para bater com o total por função da DCA. 2023 a 2025 batem exatamente; 2021 e 2022 não, e a diferença vai em `reconciliation`.
- 2020 tem pago > liquidado em dezembro: anos inconsistentes são descartados (`consistent()`), não corrigidos.
- Por fonte, publique só o **pago**: a fonte muda entre empenho e pagamento. Fontes antes de 2022 têm 8 dígitos (codificação antiga) e ficam com `sources: null`.
- A fonte 706 não é só emenda Pix (inclui outras transferências e rendimentos): não concilie com o Transferegov (ver `docs/correlation-rules.md`).

**Transferegov** (`api.transferegov.gestao.gov.br/transferenciasespeciais/`, PostgREST)
- Filtros: `col=eq.valor` e `col=in.(a,b)`; na URL, mantenha `.*,()` sem encode (`build_url`).
- Cadeia de tabelas:
  - `plano_acao_especial` → `executor_especial` (objeto) → `meta_especial` (por `id_executor`);
  - `empenho_especial` → `documento_habil_especial` (por `id_empenho`) → `ordem_pagamento_ordem_bancaria_especial` (por `id_dh`);
  - `plano_trabalho_especial` e `relatorio_gestao_novo_especial` saem direto do plano (por `id_plano_acao`).
- "Repassado" = OB com situação `OB Enviada à instituição bancária para pagamento`.
- `classificacao_orcamentaria_pt` é texto livre, às vezes com blocos `Investimento:`/`Custeio:` (ver `parse_budget`). **Os códigos de função nesse texto são inconsistentes** (ex.: `000051 - Urbanismo`, que é a função 15): vincule à DCA **pelo nome normalizado**.
- A área indicada no plano de ação pode diferir da função declarada pela Prefeitura; isso é exibido como divergência.

**Obrasgov**: ainda não integrado. Devolve HTTP 429 depois de poucas chamadas e não tem OpenAPI acessível. Não gaste tentativas em loop.

**Portal da Transparência (CGU)**: exige token e o endpoint `/transferencias?codigoIbge=` **nunca foi validado**.

## Arquitetura do ETL

`collectors/` (HTTP com retry em `etl/http.py`) → `normalizers/` → `validators/` (lançam `ValidationError`) → `correlators/` → `exporters/`. As fontes são declaradas em `SOURCES` (`etl/pipeline.py`).

- `data/raw/**` fica fora do Git (volume grande). `data/normalized/` é versionado e serve de fallback.
- O contrato público está em `docs/data-model.md`. Mudou o formato? Atualize junto `frontend/src/app/core/models.ts`.
- Árvores (`revenues.tree`, `expenses.natures.tree`) são listas planas. O pai é o ancestral existente mais próximo, obtido zerando o último segmento não nulo (`parent_code`).
- Os testes usam snapshots reais em `etl/tests/fixtures/` (gerados de `data/raw/*/latest.json`, recortados). Se a API mudar, regenere em vez de editar à mão.

## Frontend

- Angular 20 **zoneless** (`provideZonelessChangeDetection`); sem `zone.js` o app quebra com `NG0908`. Use signals, `toSignal` e `input()`, com `withComponentInputBinding` para route/query params.
- Estrutura:
  - `core/`: models, data service com cache, format pipes, `glossary.ts`, `tree.ts`;
  - `shared/`: `app-info`, `app-bar-list`, `app-breadcrumb`, `app-stages`, `app-year-picker`;
  - `features/`: uma pasta por área.
- Rotas por path; no Pages, o fallback é o `404.html` copiado no deploy. Drill-down por query params: `/receitas/:ano?origem=|conta=`, `/despesas/:ano?funcao=|natureza=`, `/emendas/:id`.
- `/despesas/:ano?fonte=` abre a visão por fonte de recursos (MSC). Seções que dependem da MSC somem quando `execution/{ano}.json` não existe.
- `childrenOf` pula níveis com um único filho, e `natureChildrenOf` dissolve a modalidade 90 (Aplicações Diretas): cada clique precisa ser uma escolha real.
- **Termo técnico novo na UI = entrada nova em `core/glossary.ts` + `<app-info term="...">`.** Não coloque `<app-info>` (um botão) dentro de `<a>`.
- Gráficos: barras horizontais em CSS, série única na cor `--green`, rótulo direto e `title` como tooltip. Percentuais no formato pt-BR (`pct`), nunca `35.3%`.
- Estilos globais em `src/styles.scss`: o bloco original é minificado; regras novas vão legíveis no final.

## Deploy e CI

- `update-data.yml` (cron diário) roda os testes, depois o ETL, e faz commit `data: atualização automática AAAA-MM-DD`.
- Push feito com `GITHUB_TOKEN` não dispara outros workflows; por isso `deploy.yml` escuta `workflow_run` além de `push`.
- O deploy usa `npm ci`: mantenha `frontend/package-lock.json` versionado, apontando para `registry.npmjs.org` (a máquina local pode ter registry corporativo; confira antes de commitar).

## Verificação visual

- Chrome headless tem **largura mínima de 500px**: capturas em 390px saem cortadas, mas não indicam overflow real. Meça com `document.documentElement.scrollWidth`.
- Para testar rotas, sirva o build com o `--base-href` e um servidor que devolva `404.html` em caminho inexistente (`python -m http.server` não faz isso).
- `--dump-dom` com um script injetado no `404.html` serve para checar overflow e popovers sem precisar de Puppeteer.
