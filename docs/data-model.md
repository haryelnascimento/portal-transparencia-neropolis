# Modelo de dados

Arquivos públicos em `frontend/public/data/` (contrato consumido pelo Angular):

| Arquivo | Conteúdo |
|---|---|
| `summary.json` | município, último exercício, anos disponíveis, totais do último ano e das emendas |
| `finances/index.json` | série anual: receita, receita por origem, empenhado e pago |
| `finances/{ano}.json` | receitas (totais, origens, destaques e `tree` completa por código de natureza) e despesas (totais, funções com subfunções e `natures.tree` por natureza, incluindo intraorçamentárias) |
| `execution/{ano}.json` | execução mensal da MSC: acumulado por mês (`months`), funções com série mensal, elementos e fontes (`functions`), fontes de recursos com recebido, pago e onde foram pagas (`sources`, `null` antes de 2022) e conferência com a DCA (`reconciliation`) |
| `amendments/index.json` | emendas com valores, empenhos, ordens bancárias, plano de trabalho (classificação orçamentária), metas, prestação de contas, vínculo com função e linha do tempo |
| `metadata/last-update.json` | status por fonte, registros, novos registros, duração e última coleta válida |

Convenções: valores em reais (número, 2 casas); datas ISO 8601 (UTC nos metadados); cada registro traz `sourceUrl` apontando para a consulta original na API oficial. `data/normalized/` guarda o mesmo conteúdo normalizado e é a base usada quando uma fonte falha.

## Árvores (drill-down)

`revenues.tree` e `expenses.natures.tree` são listas planas de nós `{code, name, parent, ...valores}`. O pai é o ancestral existente mais próximo, obtido zerando o último segmento não nulo do código (`1.7.1.1.51.1.0` → `1.7.1.1.51.0.0`). O frontend pula níveis com um único filho e dissolve a modalidade "90 – Aplicações Diretas", para que cada clique ofereça uma escolha real.

## Execução mensal (MSC)

`execution/{ano}.json` vem da Matriz de Saldos Contábeis (classe 6, saldo no fim de cada mês) e complementa a DCA:

- `months`: valores **acumulados no ano** até o fim de cada mês (`committed`, `liquidated`, `paid`). O valor de um mês é a diferença para o mês anterior; um mês não enviado fica de fora, e o seguinte cobre o intervalo.
- `functions[]`: função com os mesmos estágios, série mensal (`months`), `elements` (elemento de despesa, código no formato da DCA, ex.: `3.3.90.30.00.00`) e `sources` (fontes que pagaram a função).
- `sources[]`: fonte de recursos pelo código de 3 dígitos da STN (`706`), com `name` oficial, `shortName` (rótulo do portal), `received` (receita do ano já descontadas as deduções), `paid`, `paidFromPreviousYears` (pago com saldo de anos anteriores, fontes `2xxx`) e onde foi paga (`functions`, `elements`). **Por fonte só há valor pago**, porque a Prefeitura pode trocar a fonte entre o empenho e o pagamento.
- `reconciliation`: diferença entre dezembro da MSC e a DCA do ano (`null` sem DCA ou com o ano incompleto). A diferença é exibida e nunca ajustada.
- Despesas intraorçamentárias (modalidade 91) ficam de fora, como no total por função da DCA. Anos com matriz inconsistente (pago acima do liquidado em algum mês) não geram arquivo.
