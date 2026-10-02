import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Amendment, FinanceHistory, FinanceYear, Metadata, Summary } from './models';

/** Lê exclusivamente os JSONs estáticos gerados pelo ETL; o navegador nunca chama APIs governamentais. */
@Injectable({ providedIn: 'root' })
export class DataService {
  private readonly http = inject(HttpClient);
  summary() { return this.http.get<Summary>('data/summary.json'); }
  history() { return this.http.get<FinanceHistory[]>('data/finances/index.json'); }
  finance(year: number) { return this.http.get<FinanceYear>(`data/finances/${year}.json`); }
  amendments() { return this.http.get<Amendment[]>('data/amendments/index.json'); }
  metadata() { return this.http.get<Metadata>('data/metadata/last-update.json'); }
}
