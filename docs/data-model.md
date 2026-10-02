# Modelo de dados

Arquivos públicos em `frontend/public/data/` (contrato consumido pelo Angular):

| Arquivo | Conteúdo |
|---|---|
| `summary.json` | município, último exercício, anos disponíveis, totais do último ano e das emendas |
| `finances/index.json` | série anual: receita, receita por origem, empenhado e pago |
| `finances/{ano}.json` | receitas (bruta, deduções, líquida, origens, destaques) e despesas (totais e por função) |
| `amendments/index.json` | emendas com valores, prestação de contas e linha do tempo |
| `metadata/last-update.json` | status por fonte, registros, novos registros, duração e última coleta válida |

Convenções: valores em reais (número, 2 casas); datas ISO 8601 (UTC nos metadados); cada registro traz `sourceUrl` apontando para a consulta original na API oficial. `data/normalized/` guarda o mesmo conteúdo normalizado e é a base usada quando uma fonte falha.
