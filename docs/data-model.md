# Modelo de dados

Arquivos públicos em `frontend/public/data/` (contrato consumido pelo Angular):

| Arquivo | Conteúdo |
|---|---|
| `summary.json` | município, último exercício, anos disponíveis, totais do último ano e das emendas |
| `finances/index.json` | série anual: receita, receita por origem, empenhado e pago |
| `finances/{ano}.json` | receitas (totais, origens, destaques e `tree` completa por código de natureza) e despesas (totais, funções com subfunções e `natures.tree` por natureza, incluindo intraorçamentárias) |
| `amendments/index.json` | emendas com valores, empenhos, ordens bancárias, plano de trabalho (classificação orçamentária), metas, prestação de contas, vínculo com função e linha do tempo |
| `metadata/last-update.json` | status por fonte, registros, novos registros, duração e última coleta válida |

Convenções: valores em reais (número, 2 casas); datas ISO 8601 (UTC nos metadados); cada registro traz `sourceUrl` apontando para a consulta original na API oficial. `data/normalized/` guarda o mesmo conteúdo normalizado e é a base usada quando uma fonte falha.

## Árvores (drill-down)

`revenues.tree` e `expenses.natures.tree` são listas planas de nós `{code, name, parent, ...valores}`. O pai é o ancestral existente mais próximo, obtido zerando o último segmento não nulo do código (`1.7.1.1.51.1.0` → `1.7.1.1.51.0.0`). O frontend pula níveis com um único filho e dissolve a modalidade "90 – Aplicações Diretas", para que cada clique ofereça uma escolha real.
