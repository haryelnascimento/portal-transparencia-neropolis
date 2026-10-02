# Regras de correlação

Correlações indiretas devem registrar estratégia e confiança, nunca sendo apresentadas como vínculo oficial sem indicação. Ordem de preferência: número do instrumento, convênio, emenda, CNPJ.

## Vínculos atuais (diretos, confiança 1.0)

- Emenda ↔ empenho ↔ documento hábil ↔ ordem bancária: chaves `id_plano_acao`, `id_empenho`, `id_dh` do próprio Transferegov.

## Emenda → área de governo (estratégia `work-plan-function`, confiança 0.9)

O plano de trabalho do Transferegov traz, em texto livre, a classificação orçamentária declarada pela Prefeitura (órgão, unidade, função, subfunção, programa, ação, elemento e fonte). O ETL extrai a **função** e a liga à função da DCA **pelo nome normalizado** (sem acentos e caixa). O código não é usado porque o texto às vezes traz códigos inconsistentes — ex.: plano 70089 declara `000051 - Urbanismo`, cujo código nacional é `15`.

O portal mostra esse vínculo na página da área ("Emendas destinadas a esta área") e na emenda, com o ícone explicativo de vínculo entre bases. Quando a área indicada pelo parlamentar difere da classificação municipal (ex.: lago municipal indicado como Urbanismo e classificado em Desporto e Lazer), a divergência é exibida.

## Conciliação SICONFI × Transferegov (em aberto)

A receita "Transferência Especial da União" declarada na DCA deveria bater com as ordens bancárias do Transferegov no mesmo ano:

| Ano | DCA (1.7.1.9.57 + 2.4.1.9.51) | Transferegov (OBs ao CNPJ da Prefeitura) |
|---|---|---|
| 2024 | R$ 4.300.000 | R$ 4.250.000 |
| 2025 | R$ 500.000 | R$ 0 |

As diferenças podem vir de beneficiários com outro CNPJ (fundos municipais), de transferências especiais estaduais classificadas na mesma natureza ou de defasagem de datas. Investigar antes de exibir a conciliação no portal.

## Fonte 706 (Transferência Especial da União) × Transferegov (em aberto)

Pela MSC, a fonte 706 mostra onde a Prefeitura pagou o dinheiro registrado como transferência especial da União. O portal liga essa fonte às emendas Pix apenas como contexto (página da fonte e da emenda), **sem conciliar valores**, porque a fonte reúne outras receitas:

| Ano | Recebido na fonte 706 (MSC) | Composição por natureza da receita | OBs no Transferegov |
|---|---|---|---|
| 2024 | R$ 4.636.819 | 2.4.1.9.51 R$ 4.110.000 · 1.7.1.9.57 R$ 190.000 · 1.7.1.9.99 R$ 218.161 · 2.4.1.9.99 R$ 99.944 · rendimentos R$ 18.715 | R$ 4.250.000 |
| 2025 | R$ 2.245.237 | 1.7.1.9.99 R$ 1.250.000 · 1.7.1.9.57 R$ 500.000 · rendimentos R$ 395.280 · 2.4.1.9.99 R$ 99.957 | R$ 0 |

Na tela, os dois totais aparecem lado a lado com o aviso de que a conciliação está em análise.
