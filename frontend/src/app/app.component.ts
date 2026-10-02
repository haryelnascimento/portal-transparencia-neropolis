import { DatePipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { Observable, catchError, of, switchMap } from 'rxjs';
import { DataService } from './data.service';

const SOURCES: Record<string, { label: string; url: string }> = {
  siconfi: { label: 'SICONFI — Tesouro Nacional', url: 'https://siconfi.tesouro.gov.br' },
  transferegov: { label: 'Transferegov — transferências especiais', url: 'https://www.gov.br/transferegov' },
  transparencia: { label: 'Portal da Transparência do Governo Federal', url: 'https://portaldatransparencia.gov.br' },
};

const STATUS: Record<string, string> = { SUCCESS: 'Atualizada', FAILED: 'Falhou — exibindo última coleta válida', SKIPPED: 'Ainda não integrada' };

function safe<T>(source: Observable<T>) { return source.pipe(catchError(() => of(null))); }

@Component({
  selector: 'app-root',
  imports: [DatePipe],
  templateUrl: './app.component.html',
})
export class AppComponent {
  private readonly data = inject(DataService);
  readonly sources = SOURCES;
  readonly statusLabel = STATUS;

  readonly summary = toSignal(safe(this.data.summary()));
  readonly history = toSignal(safe(this.data.history()), { initialValue: null });
  readonly amendments = toSignal(safe(this.data.amendments()), { initialValue: null });
  readonly metadata = toSignal(safe(this.data.metadata()), { initialValue: null });

  private readonly chosenYear = signal<number | null>(null);
  readonly year = computed(() => this.chosenYear() ?? this.summary()?.latestYear ?? null);
  readonly finance = toSignal(toObservable(this.year).pipe(switchMap(year => (year ? safe(this.data.finance(year)) : of(null)))), { initialValue: null });

  readonly origins = computed(() => {
    const finance = this.finance();
    if (!finance) return [];
    return finance.revenues.origins.filter(o => o.value > 0).map(o => ({ ...o, share: this.share(o.value, finance.revenues.gross) }));
  });
  readonly highlights = computed(() => this.bars(this.finance()?.revenues.highlights.slice(0, 8) ?? [], h => h.value));
  readonly functions = computed(() => this.bars(this.finance()?.expenses.functions.slice(0, 10) ?? [], f => f.paid));
  readonly yearly = computed(() => this.bars(this.history() ?? [], h => h.revenues));
  readonly sourceList = computed(() => Object.entries(this.metadata()?.sources ?? {}).map(([key, status]) => ({ key, ...SOURCES[key], ...status })));

  menuOpen = false;

  selectYear(year: number) { this.chosenYear.set(year); }

  money(value: number | null | undefined) {
    if (value === null || value === undefined) return '—';
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value);
  }

  compact(value: number) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', notation: 'compact', maximumFractionDigits: 1 }).format(value);
  }

  pct(value: number) { return `${value.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`; }

  share(part: number, total: number) { return total ? Math.round((part / total) * 1000) / 10 : 0; }

  /** Barras horizontais de série única: largura proporcional ao maior valor do conjunto. */
  private bars<T>(items: T[], value: (item: T) => number) {
    const max = Math.max(...items.map(value), 0);
    return items.map(item => ({ item, value: value(item), width: max ? (value(item) / max) * 100 : 0 }));
  }
}
