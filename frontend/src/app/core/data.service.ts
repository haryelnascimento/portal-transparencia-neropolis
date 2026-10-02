import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, catchError, of, shareReplay } from 'rxjs';
import { Amendment, ExecutionYear, FinanceHistory, FinanceYear, Metadata, Summary } from './models';

/** Lê exclusivamente os JSONs estáticos gerados pelo ETL; o navegador nunca chama APIs governamentais. */
@Injectable({ providedIn: 'root' })
export class DataService {
  private readonly http = inject(HttpClient);
  private readonly cache = new Map<string, Observable<unknown>>();

  summary() { return this.get<Summary>('data/summary.json'); }
  history() { return this.get<FinanceHistory[]>('data/finances/index.json'); }
  finance(year: number) { return this.get<FinanceYear>(`data/finances/${year}.json`); }
  execution(year: number) { return this.get<ExecutionYear>(`data/execution/${year}.json`); }
  amendments() { return this.get<Amendment[]>('data/amendments/index.json'); }
  metadata() { return this.get<Metadata>('data/metadata/last-update.json'); }

  /** Cada arquivo é baixado uma vez por sessão; erro vira `null` para a tela tratar. */
  private get<T>(url: string): Observable<T | null> {
    if (!this.cache.has(url)) {
      this.cache.set(url, this.http.get<T>(url).pipe(catchError(() => of(null)), shareReplay(1)));
    }
    return this.cache.get(url) as Observable<T | null>;
  }
}
