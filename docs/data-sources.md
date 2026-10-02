# Fontes de dados

Todas as fontes abaixo são públicas. O navegador nunca as consulta: o ETL coleta, valida e publica JSON estático.

| Fonte | Status | Autenticação | Chave de filtro |
|---|---|---|---|
| SICONFI — DCA (Tesouro Nacional) | ✅ integrada | nenhuma | IBGE `5214507` |
| SICONFI — MSC (Tesouro Nacional) | ✅ integrada | nenhuma | IBGE `5214507` |
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

## SICONFI — Matriz de Saldos Contábeis (MSC)

- API: `https://apidatalake.tesouro.gov.br/ords/siconfi/tt/msc_orcamentaria`, parâmetros `id_ente`, `an_referencia`, `me_referencia`, `co_tipo_matriz=MSCC`, `classe_conta=6`, `id_tv=ending_balance` (saldo acumulado no fim do mês). Uma chamada por mês, cerca de 4 mil linhas cada.
- Contas usadas (PCASP): empenhado = 6.2.2.1.3.01 a .07; liquidado = .03, .04 e .07; pago = .04. Receita por fonte = 6.2.1.2 (realizada) + 6.2.1.3 (deduções). Saldo credor soma e saldo devedor subtrai.
- A modalidade 91 (intraorçamentária) é excluída para comparar com o total por função da DCA.
- **Conferência com a DCA:** 2023, 2024 e 2025 batem centavo por centavo, no total e em cada função. 2021 e 2022 ficam abaixo da DCA (pago: −R$ 5,5 mi e −R$ 9,0 mi); a matriz de encerramento (MSCE) tem a mesma diferença. A diferença é publicada e exibida.
- **2020 não é publicado:** a matriz de dezembro tem saldo devedor de R$ 8,3 mi em "liquidado a pagar", e o pago fica acima do liquidado.
- **Fontes de recursos:** codificação nacional (Portaria STN nº 710/2021) a partir de 2022; 2020 e 2021 usam códigos antigos de 8 dígitos e ficam sem detalhamento por fonte. Os nomes vêm das tabelas da STN de 2022 a 2026, gravadas em `etl/reference/fontes_stn.json`. O primeiro dígito indica exercício corrente (1) ou anteriores (2).
- A troca de fonte entre empenho e pagamento é comum (ex.: 2025, fonte 2706 com "liquidado a pagar" negativo); por isso só o valor pago é publicado por fonte.
- Elementos e funções recebem o nome usado na DCA; códigos ausentes de todas as DCAs usam as tabelas nacionais (Portarias 42/1999 e 163/2001).
- Volume: cerca de 200 MB brutos por coleta completa (2020 até o mês corrente), fora do Git.

## Transferegov — transferências especiais (emendas Pix)

- API PostgREST: `https://api.transferegov.gestao.gov.br/transferenciasespeciais/`.
- Cadeia coletada: `plano_acao_especial` → `executor_especial` (objeto) → `empenho_especial` → `documento_habil_especial` → `ordem_pagamento_ordem_bancaria_especial` (data do repasse) → `relatorio_gestao_novo_especial` (prestação de contas).
- "Repassado" = documentos hábeis com ordem bancária na situação *OB Enviada à instituição bancária para pagamento*.
- Relatórios de gestão em elaboração têm valor executado provisório (0); o portal só exibe execução declarada de relatórios entregues.

## Portal da Transparência do Governo Federal

Coletor existente (`etl/collectors/transparencia.py`), executado apenas quando o secret `TRANSPARENCIA_API_TOKEN` está configurado; sem ele a fonte aparece como *Ainda não integrada*. O endpoint e os parâmetros ainda precisam ser validados com um token real.

## Obrasgov

API `https://api.obrasgov.gestao.gov.br/obrasgov/api/projeto-investimento` responde, mas aplica limite de taxa agressivo (HTTP 429) e não publica a especificação OpenAPI. A integração será feita após identificar o filtro por município.
