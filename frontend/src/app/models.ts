export interface Municipality { name: string; state: string; ibgeCode: string; cnpj: string }

export interface Origin { key: 'union' | 'state' | 'fundeb' | 'own' | 'other'; label: string; value: number }

export interface Summary {
  municipality: Municipality;
  updatedAt: string;
  environment: string;
  latestYear: number | null;
  years: number[];
  finances: { revenues: number; origins: Origin[]; committed: number; liquidated: number; paid: number } | null;
  amendments: { count: number; planned: number; transferred: number };
}

export interface FinanceYear {
  year: number;
  revenues: {
    gross: number; deductions: number; net: number; origins: Origin[];
    highlights: { key: string; label: string; origin: string; value: number }[];
    sourceUrl: string;
  };
  expenses: {
    committed: number; liquidated: number; paid: number;
    functions: { code: string; name: string; committed: number; liquidated: number; paid: number }[];
    sourceUrl: string;
  };
}

export interface FinanceHistory { year: number; revenues: number; origins: Record<string, number>; committed: number; paid: number }

export interface Amendment {
  id: string; code: string; year: number; type: string; parliamentarian: string; amendmentNumber: string;
  area: string; purpose: string; agency: string; status: string;
  values: { planned: number; committed: number; transferred: number; reportedExecuted: number | null };
  managementReport: { type: string; status: string; date: string } | null;
  timeline: { date: string; label: string; amount: number | null }[];
  sourceUrl: string;
}

export interface SourceStatus { status: 'SUCCESS' | 'FAILED' | 'SKIPPED'; records?: number; message?: string; lastSuccessAt: string | null }

export interface Metadata { startedAt: string; finishedAt: string; status: string; sources: Record<string, SourceStatus> }
