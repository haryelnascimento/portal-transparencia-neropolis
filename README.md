# Portal da Transparência de Nerópolis

Portal cívico independente para tornar rastreáveis e compreensíveis os recursos públicos de **Nerópolis/GO** (IBGE `5214507`).

> **Versão de homologação.** Os dados são reais, coletados do SICONFI (Tesouro Nacional) e do Transferegov, mas ainda estão em validação. Não substituem o portal oficial da Prefeitura.

O portal vai do geral ao específico: cada número da visão geral é clicável e leva ao próximo nível, até o menor detalhe publicado pelas fontes. Termos técnicos têm um ícone ⓘ com explicação em linguagem simples e um [glossário](frontend/src/app/core/glossary.ts) completo.

```text
Visão geral → Receitas por origem → União → SUS → blocos de repasse
            → Despesas por área → Saúde → Atenção Básica (+ emendas ligadas à área)
            → Despesas por tipo → Outras Despesas Correntes → Serviços de Terceiros – PJ
            → Emendas → emenda → indicação, empenho, repasse, orçamento municipal, metas, prestação de contas
```

O que o portal mostra hoje:

- receitas de 2020 em diante por origem (União, Estado, FUNDEB, arrecadação própria) e principais impostos/repasses;
- despesas empenhadas, liquidadas e pagas, por área de governo;
- emendas parlamentares Pix destinadas ao município, com linha do tempo do empenho ao repasse e situação da prestação de contas.

## Arquitetura

```text
SICONFI + Transferegov (+ Portal da Transparência) → ETL Python → JSON estático → Angular → GitHub Pages
```

- `etl/collectors`: acesso isolado às fontes oficiais;
- `etl/normalizers`: conversão para o modelo comum;
- `data/raw`: resposta original, ignorada pelo Git por padrão;
- `data/normalized`: resultado auditável intermediário;
- `frontend/public/data`: arquivos pequenos consumidos pela interface;
- `docs`: decisões, fontes e contratos de dados.

O navegador nunca acessa APIs governamentais nem recebe tokens.

## Desenvolvimento

Requisitos: Node.js 20+, npm e Python 3.11+ (somente biblioteca padrão).

```bash
cd frontend
npm install
npm start
```

Acesse `http://localhost:4200`. Para os testes do ETL:

```bash
python3 -m unittest discover -s etl/tests
```

## Coleta

```bash
python3 -m etl                      # SICONFI e Transferegov não exigem token
export TRANSPARENCIA_API_TOKEN='...'  # opcional: habilita o Portal da Transparência
```

Cada fonte é coletada, normalizada e validada isoladamente. Se uma falhar, o ETL mantém a última versão válida dela (`data/normalized/`), atualiza as demais e registra a falha em `metadata/last-update.json`, exibido na seção "Sobre os dados". O workflow diário publica o portal automaticamente ao terminar. Consulte [fontes e limitações](docs/data-sources.md).

## Aviso

Projeto independente, sem vínculo oficial com a Prefeitura de Nerópolis ou com o Governo Federal. Cada item oferece um link para a fonte pública de origem.

