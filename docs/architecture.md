# Arquitetura

O MVP é uma aplicação estática. A atualização diária coleta os registros, preserva a camada bruta, normaliza entidades, valida a saída e exporta somente os arquivos necessários ao Angular. O frontend depende do contrato JSON, permitindo trocar o armazenamento por uma API futura sem redesenhar a experiência.

Uma indisponibilidade de fonte não apaga o último conjunto válido. O metadado `last-update.json` registra a situação por fonte. Dados brutos podem conter grande volume e por isso não são versionados; sua estrutura de diretórios e os dados normalizados são auditáveis no repositório.

