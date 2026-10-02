export interface GlossaryEntry {
  term: string;
  /** Explicação curta, exibida no ícone informativo. */
  short: string;
  /** Complemento exibido apenas na página do glossário. */
  more?: string;
  group: 'Receitas' | 'Despesas' | 'Emendas' | 'Fontes de dados';
}

/** Termos técnicos explicados em linguagem simples. A chave é usada em `<app-info term="...">` e como âncora em /glossario. */
export const GLOSSARY = {
  'receita-bruta': {
    group: 'Receitas', term: 'Receita bruta realizada',
    short: 'Todo o dinheiro que efetivamente entrou nos cofres do município no ano: impostos, taxas, repasses de outros governos e rendimentos.',
    more: 'É “realizada” porque conta o que de fato foi arrecadado, e não o que estava previsto no orçamento.',
  },
  'deducoes': {
    group: 'Receitas', term: 'Deduções da receita',
    short: 'Parte da receita que o município arrecada, mas precisa repassar. A principal é a contribuição obrigatória ao FUNDEB: 20% de alguns impostos e repasses.',
  },
  'origem': {
    group: 'Receitas', term: 'Origem do recurso',
    short: 'Quem forneceu o dinheiro: a União (Governo Federal), o Estado de Goiás, o FUNDEB ou a própria Prefeitura, com seus impostos e taxas.',
  },
  'arrecadacao-propria': {
    group: 'Receitas', term: 'Arrecadação própria',
    short: 'Dinheiro que a própria Prefeitura cobra: impostos municipais (IPTU, ISS, ITBI), taxas, contribuições e rendimentos de aplicações.',
  },
  'transferencias': {
    group: 'Receitas', term: 'Transferências',
    short: 'Repasses de outro governo para o município. Algumas são automáticas e garantidas pela Constituição (FPM, ICMS); outras dependem de programas, convênios ou emendas.',
    more: 'Transferências correntes pagam o dia a dia (salários, manutenção). Transferências de capital financiam obras e compra de equipamentos.',
  },
  'fpm': {
    group: 'Receitas', term: 'FPM — Fundo de Participação dos Municípios',
    short: 'Parte do Imposto de Renda e do IPI arrecadados pela União que é dividida entre todos os municípios, conforme a população. É o maior repasse federal da maioria das cidades pequenas.',
  },
  'icms': {
    group: 'Receitas', term: 'Cota-parte do ICMS',
    short: '25% do ICMS arrecadado pelo Estado pertence aos municípios. A divisão leva em conta a atividade econômica de cada cidade.',
  },
  'ipva': {
    group: 'Receitas', term: 'Cota-parte do IPVA',
    short: 'Metade do IPVA dos veículos registrados no município volta para a Prefeitura.',
  },
  'sus': {
    group: 'Receitas', term: 'Repasses do SUS',
    short: 'Dinheiro enviado pela União e pelo Estado diretamente ao Fundo Municipal de Saúde para custear atendimentos, programas e estrutura da saúde pública.',
  },
  'fundeb': {
    group: 'Receitas', term: 'FUNDEB',
    short: 'Fundo da educação básica. Estado e municípios depositam parte dos impostos e o fundo redistribui conforme o número de alunos matriculados. O valor só pode ser gasto em educação.',
  },
  'iss': { group: 'Receitas', term: 'ISS', short: 'Imposto Sobre Serviços, cobrado pela Prefeitura de quem presta serviços no município.' },
  'iptu': { group: 'Receitas', term: 'IPTU', short: 'Imposto Predial e Territorial Urbano, pago anualmente pelos donos de imóveis na zona urbana.' },
  'itbi': { group: 'Receitas', term: 'ITBI', short: 'Imposto cobrado pela Prefeitura quando um imóvel é vendido ou transferido.' },
  'natureza-receita': {
    group: 'Receitas', term: 'Código de natureza da receita',
    short: 'Classificação padronizada nacionalmente que diz de onde vem cada receita, do nível mais geral (ex.: Transferências) ao mais específico (ex.: FPM – cota mensal).',
  },
  'empenho': {
    group: 'Despesas', term: 'Empenho',
    short: 'Primeira etapa da despesa: a Prefeitura reserva o dinheiro no orçamento para um gasto específico. Ainda não houve entrega nem pagamento.',
  },
  'liquidacao': {
    group: 'Despesas', term: 'Liquidação',
    short: 'Segunda etapa: a Prefeitura confirma que o produto foi entregue ou o serviço foi prestado. Só então o pagamento pode ser feito.',
  },
  'pagamento': {
    group: 'Despesas', term: 'Pagamento',
    short: 'Última etapa: o dinheiro sai da conta da Prefeitura para o fornecedor, servidor ou beneficiário.',
  },
  'restos-a-pagar': {
    group: 'Despesas', term: 'Restos a pagar',
    short: 'Despesas empenhadas em um ano que só serão pagas no ano seguinte. Por isso o valor pago costuma ser menor que o empenhado.',
  },
  'funcao': {
    group: 'Despesas', term: 'Função de governo',
    short: 'A grande área em que o dinheiro foi gasto: Saúde, Educação, Urbanismo, Assistência Social etc. É uma classificação padronizada em todo o país.',
  },
  'subfuncao': {
    group: 'Despesas', term: 'Subfunção',
    short: 'O detalhamento da área de governo. Por exemplo, dentro de Saúde: Atenção Básica (postos de saúde) e Assistência Hospitalar.',
  },
  'natureza-despesa': {
    group: 'Despesas', term: 'Natureza da despesa',
    short: 'Classifica o que foi comprado ou pago: salários, material de consumo, serviços de empresas, obras, equipamentos etc.',
    more: 'Vai do geral (Despesas Correntes ou de Capital) ao grupo (Pessoal, Outras Despesas Correntes, Investimentos) e ao elemento (ex.: Obras e Instalações).',
  },
  'elemento-despesa': {
    group: 'Despesas', term: 'Elemento de despesa',
    short: 'O nível mais detalhado do tipo de gasto nos balanços públicos: salários, material de consumo, serviços de empresas, obras, equipamentos…',
  },
  'fonte-recursos': {
    group: 'Despesas', term: 'Fonte de recursos',
    short: 'Etiqueta que o dinheiro recebe ao entrar no caixa da Prefeitura e que acompanha cada pagamento: diz de onde ele veio (impostos, SUS, FUNDEB, emendas…) e em que pode ser usado. É o que permite seguir o dinheiro da entrada até o gasto.',
    more: 'A codificação é nacional desde 2022 (Portaria STN nº 710/2021). Como a Prefeitura pode trocar a fonte de um gasto entre o empenho e o pagamento, o portal mostra por fonte apenas o valor pago.',
  },
  'saldo-anos-anteriores': {
    group: 'Despesas', term: 'Saldo de anos anteriores',
    short: 'Dinheiro recebido em anos anteriores que ficou em caixa e foi gasto neste ano. Por isso, numa fonte, o valor pago pode superar o recebido no ano.',
  },
  'intraorcamentaria': {
    group: 'Despesas', term: 'Despesa intraorçamentária',
    short: 'Pagamento de um órgão do município para outro órgão do próprio município — por exemplo, a Prefeitura recolhendo a contribuição patronal ao seu regime próprio de previdência. Aparece no detalhamento por tipo de gasto, mas não é contado duas vezes no total por área.',
  },
  'custeio-investimento': {
    group: 'Despesas', term: 'Custeio e investimento',
    short: 'Custeio mantém os serviços funcionando (salários, materiais, contas). Investimento cria ou amplia patrimônio (obras, equipamentos, veículos).',
  },
  'emenda-parlamentar': {
    group: 'Emendas', term: 'Emenda parlamentar',
    short: 'Parte do orçamento federal cujo destino é indicado por um deputado federal ou senador, normalmente para um município ou entidade da sua base.',
  },
  'transferencia-especial': {
    group: 'Emendas', term: 'Transferência especial (emenda Pix)',
    short: 'Tipo de emenda em que o dinheiro cai direto na conta da Prefeitura, sem convênio prévio. Em troca, o município precisa informar no Transferegov como vai usar e prestar contas.',
  },
  'plano-acao': {
    group: 'Emendas', term: 'Plano de ação',
    short: 'Registro da emenda no Transferegov: quem indicou, quanto, para qual área e se o valor é de custeio ou investimento.',
  },
  'plano-trabalho': {
    group: 'Emendas', term: 'Plano de trabalho',
    short: 'Documento em que a Prefeitura declara o que vai fazer com o dinheiro, em quanto tempo e em qual parte do orçamento municipal o recurso entra (secretaria, programa, tipo de despesa).',
  },
  'ordem-bancaria': {
    group: 'Emendas', term: 'Ordem bancária',
    short: 'Comando de pagamento do Tesouro Nacional. Quando é enviada ao banco, o dinheiro está a caminho da conta do município — é o “repasse” de fato.',
  },
  'relatorio-gestao': {
    group: 'Emendas', term: 'Relatório de gestão',
    short: 'Prestação de contas que a Prefeitura envia ao Transferegov dizendo quanto da emenda já executou. Enquanto está “em elaboração”, o valor informado é provisório.',
  },
  'metas': {
    group: 'Emendas', term: 'Metas',
    short: 'O que a Prefeitura se comprometeu a entregar com a emenda, com quantidade, unidade e prazo.',
  },
  'confianca-vinculo': {
    group: 'Fontes de dados', term: 'Vínculo entre bases',
    short: 'Quando duas bases oficiais não compartilham um identificador, o portal liga os registros por outra informação (aqui, o nome da área de governo declarada no plano de trabalho). Esses vínculos são indicados e podem conter imprecisões.',
  },
  'dca': {
    group: 'Fontes de dados', term: 'DCA — Declaração de Contas Anuais',
    short: 'Balanço anual que a Prefeitura é obrigada a enviar ao Tesouro Nacional até 30 de abril do ano seguinte, com todas as receitas e despesas do ano.',
  },
  'siconfi': {
    group: 'Fontes de dados', term: 'SICONFI',
    short: 'Sistema do Tesouro Nacional que recebe as contas de União, estados e municípios. Os dados são declarados pela própria Prefeitura e podem ser retificados.',
  },
  'msc': {
    group: 'Fontes de dados', term: 'MSC — Matriz de Saldos Contábeis',
    short: 'Relatório contábil que a Prefeitura envia todo mês ao Tesouro Nacional. Mostra o gasto mês a mês, por tipo de despesa e por fonte de recursos.',
    more: 'O mês de dezembro é conferido com a DCA. Quando os dois não batem, a diferença é mostrada na página.',
  },
  'transferegov': {
    group: 'Fontes de dados', term: 'Transferegov',
    short: 'Plataforma do Governo Federal que registra convênios, emendas e transferências para estados e municípios, do empenho à prestação de contas.',
  },
  'valores-nominais': {
    group: 'Fontes de dados', term: 'Valores nominais',
    short: 'Valores na moeda da época, sem correção pela inflação. Comparar anos distantes exige cuidado: parte do crescimento é apenas inflação.',
  },
  'exercicio': {
    group: 'Fontes de dados', term: 'Exercício',
    short: 'O ano do orçamento público, de 1º de janeiro a 31 de dezembro.',
  },
} satisfies Record<string, GlossaryEntry>;

export type GlossaryTerm = keyof typeof GLOSSARY;
