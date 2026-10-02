# Fontes de dados

## Portal da Transparência do Governo Federal

- Uso: transferências federais destinadas a Nerópolis.
- Filtro: código IBGE `5214507`.
- Autenticação: variável `TRANSPARENCIA_API_TOKEN` / GitHub Secret de mesmo nome.
- Proveniência: `source.system = TRANSPARENCIA_GOV_BR` e link público em cada registro.

O endpoint e seu contrato podem mudar. A amostra inicial da interface é demonstrativa até que o secret seja configurado e a primeira coleta seja validada.

## Próximas integrações

Transferegov, Obrasgov e SICONFI serão incorporados incrementalmente. Diretórios RAW já reservam a proveniência sem misturar respostas de sistemas distintos.

