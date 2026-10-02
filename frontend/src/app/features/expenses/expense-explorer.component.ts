import { Component, computed, inject, input } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { of, switchMap } from 'rxjs';
import { DataService } from '../../core/data.service';
import { compact, MoneyPipe, pct, PctPipe, share } from '../../core/format';
import { FundingSource, MonthStages, PaidItem, SourceRef, Stages } from '../../core/models';
import { ancestorsOf, childrenOf, hasChildren, isDirectApplication, natureChildrenOf, natureLabel } from '../../core/tree';
import { BarListComponent, BarRow } from '../../shared/bar-list.component';
import { BreadcrumbComponent, Crumb } from '../../shared/breadcrumb.component';
import { InfoTipComponent } from '../../shared/info-tip.component';
import { StagesComponent } from '../../shared/stages.component';
import { YearPickerComponent } from '../../shared/year-picker.component';

type Mode = 'root' | 'function' | 'nature' | 'source';
interface View { mode: Mode; title: string; stages: Stages | null; crumbs: Crumb[]; rows: BarRow[]; code: string | null }

export const MONTHS = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

function rowsFor<T extends Stages & { code: string; name: string }>(items: T[], total: number, link: (item: T) => { link: unknown[] | null; query?: Record<string, string> }): BarRow[] {
  return [...items].sort((a, b) => b.paid - a.paid).map(item => ({
    key: item.code, label: item.name, value: item.paid, display: compact(item.paid), note: pct(share(item.paid, total)),
    title: `${item.name}: empenhado ${compact(item.committed)}, liquidado ${compact(item.liquidated)}, pago ${compact(item.paid)}`,
    ...link(item),
  }));
}

type Linker = (item: { code: string }) => { link: unknown[] | null; query?: Record<string, string> };
const noLink: Linker = () => ({ link: null });

/** Itens com valor pago apenas (áreas e elementos dentro de uma fonte). */
function paidRows(items: PaidItem[], total: number, link: Linker = noLink): BarRow[] {
  return items.map(item => ({ key: item.code, label: item.name, value: item.paid, display: compact(item.paid), note: pct(share(item.paid, total)), ...link(item) }));
}

export function sourceName(source: SourceRef) {
  return source.shortName ?? source.name ?? `Fonte ${source.code} (fora da tabela nacional)`;
}

/** Fontes por valor pago; além de `limit`, as menores são somadas numa linha só, sem link. */
function sourceRowsFor(items: (SourceRef & { paid: number })[], total: number, link: Linker, limit = Infinity): BarRow[] {
  const rows: BarRow[] = items.filter(s => s.paid > 0).map(s => ({
    key: s.code, label: sourceName(s), value: s.paid, display: compact(s.paid), note: pct(share(s.paid, total)),
    title: `${s.name ?? sourceName(s)} (fonte ${s.code}): ${compact(s.paid)} pagos`, ...link(s),
  }));
  if (rows.length <= limit) return rows;
  const rest = rows.slice(limit - 1);
  const paid = rest.reduce((sum, r) => sum + r.value, 0);
  return [...rows.slice(0, limit - 1), { key: 'demais', label: `Demais ${rest.length} fontes`, value: paid, display: compact(paid), note: pct(share(paid, total)), title: rest.map(r => r.label).join(', '), link: null }];
}

/**
 * Valor pago em cada mês, a partir do acumulado no ano. Se a Prefeitura não enviou algum mês,
 * a linha seguinte cobre o intervalo inteiro (ex.: "fevereiro a março").
 */
function monthRows(months: MonthStages[]): BarRow[] {
  return months.map((m, i) => {
    const previous = months[i - 1];
    const paid = m.paid - (previous?.paid ?? 0);
    const first = (previous?.month ?? 0) + 1;
    const label = first === m.month ? MONTHS[m.month - 1] : `${MONTHS[first - 1]} a ${MONTHS[m.month - 1]}`;
    return {
      key: String(m.month), label, value: paid, display: compact(paid), note: `acumulado ${compact(m.paid)}`,
      title: `${label}: pago ${compact(paid)} no período; no ano, até o fim do mês: empenhado ${compact(m.committed)}, liquidado ${compact(m.liquidated)}, pago ${compact(m.paid)}`,
    };
  });
}

@Component({
  selector: 'app-expense-explorer',
  imports: [BarListComponent, BreadcrumbComponent, InfoTipComponent, MoneyPipe, PctPipe, RouterLink, StagesComponent, YearPickerComponent],
  templateUrl: './expense-explorer.component.html',
})
export class ExpenseExplorerComponent {
  private readonly data = inject(DataService);
  /** Parâmetros de rota: /despesas/:year?funcao=<código>, ?natureza=<código> ou ?fonte=<código>. */
  readonly year = input<string>();
  readonly funcao = input<string>();
  readonly natureza = input<string>();
  readonly fonte = input<string>();

  readonly months = MONTHS;
  readonly abs = Math.abs;
  readonly summary = toSignal(this.data.summary());
  readonly amendments = toSignal(this.data.amendments());
  readonly selectedYear = computed(() => Number(this.year()) || this.summary()?.latestYear || null);
  private readonly year$ = toObservable(this.selectedYear);
  readonly finance = toSignal(this.year$.pipe(switchMap(y => (y ? this.data.finance(y) : of(null)))));
  /** Execução mensal (MSC). Pode faltar para um ano; nesse caso a página mostra só o balanço anual. */
  readonly execution = toSignal(this.year$.pipe(switchMap(y => (y ? this.data.execution(y) : of(null)))));

  readonly source = computed<FundingSource | null>(() => this.execution()?.sources?.find(s => s.code === this.fonte()) ?? null);

  readonly view = computed<View | null>(() => {
    const finance = this.finance();
    if (!finance) return null;
    const year = finance.year;
    const { functions, natures } = finance.expenses;
    const root: Crumb = { label: `Despesas ${year}`, link: ['/despesas', year] };

    const fn = functions.find(f => f.code === this.funcao());
    if (fn) {
      return { mode: 'function', title: fn.name, stages: fn, code: fn.code, crumbs: [root, { label: 'Por área de governo', link: ['/despesas', year] }, { label: fn.name }], rows: rowsFor(fn.subfunctions, fn.paid, () => ({ link: null })) };
    }
    const node = natures.tree.find(n => n.code === this.natureza());
    if (node) {
      const crumbs = [root, { label: 'Por tipo de gasto', link: ['/despesas', year] }, ...ancestorsOf(natures.tree, node.code).filter(a => !isDirectApplication(a.code)).map(a => ({ label: natureLabel(a), link: ['/despesas', year], query: { natureza: a.code } })), { label: natureLabel(node) }];
      return { mode: 'nature', title: natureLabel(node), stages: node, code: node.code, crumbs, rows: rowsFor(natureChildrenOf(natures.tree, node.code).map(c => ({ ...c, name: natureLabel(c) })), node.paid, c => ({ link: hasChildren(natures.tree, c.code) ? ['/despesas', year] : null, query: { natureza: c.code } })) };
    }
    const source = this.source();
    if (source) {
      const rows = paidRows(source.functions, source.paid, f => ({ link: functions.some(d => d.code === f.code) ? ['/despesas', year] : null, query: { funcao: f.code } }));
      return { mode: 'source', title: sourceName(source), stages: null, code: source.code, crumbs: [root, { label: 'Por fonte de recursos', link: ['/despesas', year] }, { label: sourceName(source) }], rows };
    }
    return { mode: 'root', title: 'Todas as despesas', stages: finance.expenses, code: null, crumbs: [root], rows: rowsFor(functions, finance.expenses.paid, f => ({ link: ['/despesas', year], query: { funcao: f.code } })) };
  });

  readonly natureRows = computed<BarRow[]>(() => {
    const finance = this.finance();
    if (!finance) return [];
    const tree = finance.expenses.natures.tree;
    // Primeiro nível útil: grupos (pessoal, custeio, investimentos...), pulando "Correntes/Capital" quando só há um filho.
    const groups = childrenOf(tree, null).flatMap(category => natureChildrenOf(tree, category.code));
    return rowsFor(groups, finance.expenses.natures.paid, g => ({ link: hasChildren(tree, g.code) ? ['/despesas', finance.year] : null, query: { natureza: g.code } }));
  });

  /** Despesas intraorçamentárias (entre órgãos do município) entram no total por natureza, mas não no total por função. */
  readonly intraTotal = computed(() => {
    const finance = this.finance();
    return finance ? Math.max(finance.expenses.natures.paid - finance.expenses.paid, 0) : 0;
  });

  /** Execução da área selecionada (MSC). */
  readonly functionExecution = computed(() => {
    const view = this.view();
    return view?.mode === 'function' ? this.execution()?.functions.find(f => f.code === view.code) ?? null : null;
  });

  /** Linha do tempo: o que foi pago a cada mês, no município todo ou na área selecionada. */
  readonly timeline = computed<BarRow[]>(() => {
    const mode = this.view()?.mode;
    if (mode === 'root') return monthRows(this.execution()?.months ?? []);
    if (mode === 'function') return monthRows(this.functionExecution()?.months ?? []);
    return [];
  });

  /** Primeiro mês em que metade do valor do período já estava paga — resume o ritmo do gasto. */
  readonly halfPaidMonth = computed(() => {
    const months = this.view()?.mode === 'function' ? this.functionExecution()?.months : this.execution()?.months;
    const total = months?.at(-1)?.paid ?? 0;
    const month = months?.find(m => total > 0 && m.paid >= total / 2)?.month;
    return month ? MONTHS[month - 1] : null;
  });

  readonly elementRows = computed<BarRow[]>(() => {
    const view = this.view();
    if (view?.mode === 'function') {
      const fn = this.functionExecution();
      return fn ? rowsFor(fn.elements, fn.paid, () => ({ link: null })) : [];
    }
    const source = this.source();
    return view?.mode === 'source' && source ? paidRows(source.elements, source.paid) : [];
  });

  readonly sourceRows = computed<BarRow[]>(() => {
    const execution = this.execution();
    const view = this.view();
    if (!execution?.sources || !view) return [];
    const link = (s: { code: string }) => ({ link: execution.sources!.some(x => x.code === s.code) ? ['/despesas', execution.year] : null, query: { fonte: s.code } });
    if (view.mode === 'root') return sourceRowsFor(execution.sources, execution.paid, link, 12);
    if (view.mode === 'function') {
      const fn = this.functionExecution();
      return fn ? sourceRowsFor(fn.sources, fn.paid, link) : [];
    }
    return [];
  });

  /** Emendas cujo plano de trabalho declara esta função (vínculo indicado, ver glossário). */
  readonly linkedAmendments = computed(() => {
    const view = this.view();
    if (view?.mode !== 'function') return [];
    return (this.amendments() ?? []).filter(a => a.links.function?.code === view.code);
  });

  /** Fonte 706 (Transferência Especial da União): emendas Pix com repasse no ano, para comparar com o declarado na fonte. */
  readonly specialTransfers = computed(() => {
    const year = String(this.selectedYear());
    if (this.view()?.mode !== 'source' || this.source()?.code !== '706') return null;
    const amendments = (this.amendments() ?? []).filter(a => a.payments.some(p => p.date.startsWith(year)));
    const transferred = amendments.flatMap(a => a.payments).filter(p => p.date.startsWith(year)).reduce((sum, p) => sum + p.amount, 0);
    return { amendments, transferred };
  });
}
