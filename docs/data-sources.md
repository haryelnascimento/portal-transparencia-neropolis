# Fontes de dados

Todas as fontes abaixo são públicas. O navegador nunca as consulta: o ETL coleta, valida e publica JSON estático.

| Fonte | Status | Autenticação | Chave de filtro |
|---|---|---|---|
| SICONFI — DCA (Tesouro Nacional) | ✅ integrada | nenhuma | IBGE `5214507` |
| Transferegov — transferências especiais | ✅ integrada | nenhuma | CNPJ `01105626000125` |
| Portal da Transparência (CGU) | ⏸ aguardando token | `TRANSPARENCIA_API_TOKEN` | IBGE |
| Obrasgov | 🔜 próxima | nenhuma | a definir |

## SICONFI — Declaração de Contas Anuais

- API: `https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca`, parâmetros `an_exercicio`, `no_anexo`, `id_ente`.
- **Anexo I-C** (receitas orçamentárias): coluna `Receitas Brutas Realizadas`; o total usa `cod_conta = ReceitasExcetoIntraOrcamentarias`.
- **Anexo I-E** (despesas por função): colunas `Despesas Empenhadas`, `Liquidadas` e `Pagas`; funções são as contas no formato `NN - Nome`.
- Exercícios coletados: de 2020 até o último publicado. A DCA anual só existe depois do envio pela Prefeitura (prazo: 30/04 do ano seguinte).
- O ementário de receitas mudou em 2022 (ex.: FPM `1.7.1.8.01.x` → `1.7.1.1.51`). Os níveis de origem (`1.7.1` União, `1.7.2` Estado, `1.7.5` FUNDEB) são estáveis; os destaques mapeiam as duas versões em `etl/normalizers/siconfi.py`.
- Os valores são **declarados pelo município** e podem ser retificados.

## Transferegov — transferências especiais (emendas Pix)

- API PostgREST: `https://api.transferegov.gestao.gov.br/transferenciasespeciais/`.
- Cadeia coletada: `plano_acao_especial` → `executor_especial` (objeto) → `empenho_especial` → `documento_habil_especial` → `ordem_pagamento_ordem_bancaria_especial` (data do repasse) → `relatorio_gestao_novo_especial` (prestação de contas).
- "Repassado" = documentos hábeis com ordem bancária na situação *OB Enviada à instituição bancária para pagamento*.
- Relatórios de gestão em elaboração têm valor executado provisório (0); o portal só exibe execução declarada de relatórios entregues.

## Portal da Transparência do Governo Federal

Coletor existente (`etl/collectors/transparencia.py`), executado apenas quando o secret `TRANSPARENCIA_API_TOKEN` está configurado; sem ele a fonte aparece como *Ainda não integrada*. O endpoint e os parâmetros ainda precisam ser validados com um token real.

## Obrasgov

API `https://api.obrasgov.gestao.gov.br/obrasgov/api/projeto-investimento` responde, mas aplica limite de taxa agressivo (HTTP 429) e não publica a especificação OpenAPI. A integração será feita após identificar o filtro por município.
