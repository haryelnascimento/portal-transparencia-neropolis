import { DatePipe } from '@angular/common';
import { Component, computed, inject } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { of, switchMap } from 'rxjs';
import { DataService } from '../../core/data.service';
import { compact, MoneyPipe, pct, PctPipe, share } from '../../core/format';
import { BarListComponent, BarRow } from '../../shared/bar-list.component';
import { InfoTipComponent } from '../../shared/info-tip.component';
import { StagesComponent } from '../../shared/stages.component';

const SOURCES: Record<string, { label: string; url: string }> = {
  siconfi: { label: 'SICONFI — Tesouro Nacional', url: 'https://siconfi.tesouro.gov.br' },
  'siconfi-msc': { label: 'SICONFI — execução mensal (MSC)', url: 'https://siconfi.tesouro.gov.br' },
  transferegov: { label: 'Transferegov — transferências especiais', url: 'https://www.gov.br/transferegov' },
  transparencia: { label: 'Portal da Transparência do Governo Federal', url: 'https://portaldatransparencia.gov.br' },
};
const STATUS: Record<string, string> = { SUCCESS: 'Atualizada', FAILED: 'Falhou — exibindo última coleta válida', SKIPPED: 'Ainda não integrada' };

@Component({
  selector: 'app-overview',
  imports: [BarListComponent, DatePipe, InfoTipComponent, MoneyPipe, PctPipe, RouterLink, StagesComponent],
  templateUrl: './overview.component.html',
})
export class OverviewComponent {
  private readonly data = inject(DataService);
  readonly statusLabel = STATUS;
  readonly summary = toSignal(this.data.summary());
  readonly history = toSignal(this.data.history());
  readonly amendments = toSignal(this.data.amendments());
  readonly metadata = toSignal(this.data.metadata());
  readonly year = computed(() => this.summary()?.latestYear ?? null);
  readonly finance = toSignal(toObservable(this.year).pipe(switchMap(y => (y ? this.data.finance(y) : of(null)))));

  readonly originCards = computed(() => {
    const f = this.finance();
    return f ? f.revenues.origins.filter(o => o.key !== 'other' && o.value > 0) : [];
  });

  readonly highlightRows = computed<BarRow[]>(() => {
    const f = this.finance();
    if (!f) return [];
    return f.revenues.highlights.slice(0, 8).map(h => ({ key: h.key, label: h.label, value: h.value, display: compact(h.value), link: h.codes.length ? ['/receitas', f.year] : null, query: { conta: h.codes[0] } }));
  });

  readonly functionRows = computed<BarRow[]>(() => {
    const f = this.finance();
    if (!f) return [];
    return f.expenses.functions.slice(0, 8).map(fn => ({ key: fn.code, label: fn.name, value: fn.paid, display: compact(fn.paid), note: pct(share(fn.paid, f.expenses.paid)), link: ['/despesas', f.year], query: { funcao: fn.code } }));
  });

  readonly yearRows = computed<BarRow[]>(() => (this.history() ?? []).map(h => ({ key: String(h.year), label: String(h.year), value: h.revenues, display: compact(h.revenues), title: `${h.year}: receita ${compact(h.revenues)}, pago ${compact(h.paid)}`, link: ['/receitas', h.year] })));

  readonly topAmendments = computed(() => [...(this.amendments() ?? [])].sort((a, b) => b.values.planned - a.values.planned).slice(0, 3));

  readonly sourceList = computed(() => Object.entries(this.metadata()?.sources ?? {}).map(([key, status]) => ({ key, ...SOURCES[key], ...status })));
}
