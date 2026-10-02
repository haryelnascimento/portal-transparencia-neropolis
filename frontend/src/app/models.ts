export interface Summary {
  municipality: { name: string; state: string; ibgeCode: string };
  updatedAt: string;
  totals: { received: number; committed: number; liquidated: number; paid: number };
  counts: { transfers: number; amendments: number; agreements: number; works: number; suppliers: number };
}

export interface Transfer {
  id: string; title: string; agency: string; type: string; status: string; year: number;
  purpose: string; transferred: number; paid: number; sourceUrl: string;
}
