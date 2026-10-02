# Portal da Transparência de Nerópolis

Portal cívico independente para tornar rastreáveis e compreensíveis os recursos públicos destinados a **Nerópolis/GO** (IBGE `5214507`). A primeira vertical já conecta a estrutura de coleta federal, normalização, JSON estático e um dashboard Angular responsivo.

> Os dados versionados neste bootstrap são demonstrativos e estão identificados como `MOCK`. Não devem ser interpretados como prestação de contas oficial.

## Arquitetura

```text
Portal da Transparência → ETL Python → JSON estático → Angular → GitHub Pages
```

- `etl/collectors`: acesso isolado às fontes oficiais;
- `etl/normalizers`: conversão para o modelo comum;
- `data/raw`: resposta original, ignorada pelo Git por padrão;
- `data/normalized`: resultado auditável intermediário;
- `frontend/public/data`: arquivos pequenos consumidos pela interface;
- `docs`: decisões, fontes e contratos de dados.

O navegador nunca acessa APIs governamentais nem recebe tokens.

## Desenvolvimento

Requisitos: Node.js 20+, npm e Python 3.11+.

```bash
cd frontend
npm install
npm start
```

Acesse `http://localhost:4200`. Para os testes do ETL:

```bash
python3 -m unittest discover -s etl/tests
```

## Coleta real

Configure o token somente no ambiente e execute a pipeline:

```bash
export TRANSPARENCIA_API_TOKEN='...'
python3 -m etl
```

O coletor envia o código IBGE de Nerópolis à API. Se uma coleta local falhar, os dados públicos anteriores são preservados; em CI, a falha é explícita para impedir a publicação silenciosa de dados inválidos. Consulte [fontes e limitações](docs/data-sources.md).

## Aviso

Projeto independente, sem vínculo oficial com a Prefeitura de Nerópolis ou com o Governo Federal. Cada item oferece um link para a fonte pública de origem.

