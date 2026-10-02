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
