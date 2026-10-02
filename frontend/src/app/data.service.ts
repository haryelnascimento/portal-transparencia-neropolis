import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Summary, Transfer } from './models';

@Injectable({ providedIn: 'root' })
export class DataService {
  private readonly http = inject(HttpClient);
  summary() { return this.http.get<Summary>('data/summary.json'); }
  transfers() { return this.http.get<Transfer[]>('data/transfers/index.json'); }
}
