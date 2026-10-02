export interface Municipality { name: string; state: string; ibgeCode: string; cnpj: string }

export type OriginKey = 'union' | 'state' | 'fundeb' | 'own' | 'other';
export interface Origin { key: OriginKey; label: string; codes: string[]; value: number }

export interface Summary {
  municipality: Municipality;
  updatedAt: string;
  environment: string;
  latestYear: number | null;
  years: number[];
  finances: { revenues: number; origins: Origin[]; committed: number; liquidated: number; paid: number } | null;
  amendments: { count: number; planned: number; transferred: number };
}

export interface Stages { committed: number; liquidated: number; paid: number }
export interface RevenueNode { code: string; name: string; value: number; parent: string | null }
export interface NatureNode extends Stages { code: string; name: string; parent: string | null; intra: boolean }
export interface Subfunction extends Stages { code: string; name: string }
export interface FunctionExpense extends Stages { code: string; name: string; subfunctions: Subfunction[] }

export interface FinanceYear {
  year: number;
  revenues: {
    gross: number; deductions: number; net: number; origins: Origin[];
    highlights: { key: string; label: string; origin: OriginKey; codes: string[]; value: number }[];
    tree: RevenueNode[];
    sourceUrl: string;
  };
  expenses: Stages & {
    functions: FunctionExpense[];
    natures: { tree: NatureNode[]; paid: number; sourceUrl: string };
    sourceUrl: string;
  };
}

/** Execução mensal da MSC: valores acumulados no ano até o fim de cada mês, sem as despesas intraorçamentárias. */
export interface MonthStages extends Stages { month: number }
export interface ElementExpense extends Stages { code: string; name: string }
export interface PaidItem { code: string; name: string; paid: number }
/** Fonte de recursos: `name` é o nome oficial da STN e `shortName`, o rótulo curto do portal (ambos `null` fora da tabela nacional). */
export interface SourceRef { code: string; name: string | null; shortName: string | null }
export interface FunctionExecution extends Stages { code: string; name: string; months: MonthStages[]; elements: ElementExpense[]; sources: (SourceRef & { paid: number })[] }
/** Por fonte só há valor pago: a Prefeitura pode trocar a fonte de um gasto entre o empenho e o pagamento. */
export interface FundingSource extends SourceRef { received: number; paid: number; paidFromPreviousYears: number; functions: PaidItem[]; elements: PaidItem[] }
export interface ExecutionYear extends Stages {
  year: number;
  lastMonth: number;
  months: MonthStages[];
  functions: FunctionExecution[];
  /** `null` antes da codificação nacional de fontes (2022). */
  sources: FundingSource[] | null;
  /** Conferência de dezembro com a DCA; `null` quando o ano não está completo ou não há DCA. */
  reconciliation: { reference: 'DCA'; matches: boolean; differences: Stages } | null;
  sourceUrl: string;
}

export interface FinanceHistory { year: number; revenues: number; origins: Record<string, number>; committed: number; paid: number }

export interface BudgetItem { code: string; name: string }
export interface BudgetBlock { organ?: BudgetItem; unit?: BudgetItem; function?: BudgetItem; subfunction?: BudgetItem; program?: BudgetItem; action?: BudgetItem; element?: BudgetItem; fundingSource?: BudgetItem }

export interface Amendment {
  id: string; code: string; year: number; type: string; parliamentarian: string; amendmentNumber: string;
  area: string; purpose: string; agency: string; status: string; costing: number; investment: number;
  values: { planned: number; committed: number; transferred: number; reportedExecuted: number | null };
  managementReport: { type: string; status: string; date: string } | null;
  workPlan: { status: string; start: string | null; end: string | null; months: number | null; budget: BudgetBlock[] } | null;
  goals: { name: string; description: string; unit: string; quantity: number; months: number | null; amount: number; ownResources: number }[];
  commitments: { number: string; date: string; amount: number; category: string | null; status: string }[];
  payments: { order: string; document: string; date: string; amount: number; status: string }[];
  links: { function: { code: string; name: string; strategy: string; confidence: number } | null };
  timeline: { date: string; label: string; amount: number | null }[];
  sourceUrl: string;
}

export interface SourceStatus { status: 'SUCCESS' | 'FAILED' | 'SKIPPED'; records?: number; message?: string; lastSuccessAt: string | null }
export interface Metadata { startedAt: string; finishedAt: string; status: string; sources: Record<string, SourceStatus> }
