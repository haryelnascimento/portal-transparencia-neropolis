import { Component, computed, inject, input } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { of, switchMap } from 'rxjs';
import { DataService } from '../../core/data.service';
import { compact, MoneyPipe, pct, PctPipe, share } from '../../core/format';
import { Stages } from '../../core/models';
import { ancestorsOf, childrenOf, hasChildren, isDirectApplication, natureChildrenOf, natureLabel } from '../../core/tree';
import { BarListComponent, BarRow } from '../../shared/bar-list.component';
import { BreadcrumbComponent, Crumb } from '../../shared/breadcrumb.component';
import { InfoTipComponent } from '../../shared/info-tip.component';
import { StagesComponent } from '../../shared/stages.component';
import { YearPickerComponent } from '../../shared/year-picker.component';

type Mode = 'root' | 'function' | 'nature';
interface View { mode: Mode; title: string; stages: Stages; crumbs: Crumb[]; rows: BarRow[]; code: string | null }

function rowsFor<T extends Stages & { code: string; name: string }>(items: T[], total: number, link: (item: T) => { link: unknown[] | null; query?: Record<string, string> }): BarRow[] {
  return [...items].sort((a, b) => b.paid - a.paid).map(item => ({
    key: item.code, label: item.name, value: item.paid, display: compact(item.paid), note: pct(share(item.paid, total)),
    title: `${item.name}: empenhado ${compact(item.committed)}, liquidado ${compact(item.liquidated)}, pago ${compact(item.paid)}`,
    ...link(item),
  }));
}

@Component({
  selector: 'app-expense-explorer',
  imports: [BarListComponent, BreadcrumbComponent, InfoTipComponent, MoneyPipe, PctPipe, RouterLink, StagesComponent, YearPickerComponent],
  templateUrl: './expense-explorer.component.html',
})
export class ExpenseExplorerComponent {
  private readonly data = inject(DataService);
  /** Parâmetros de rota: /despesas/:year?funcao=<código> ou ?natureza=<código>. */
  readonly year = input<string>();
  readonly funcao = input<string>();
  readonly natureza = input<string>();

  readonly summary = toSignal(this.data.summary());
  readonly amendments = toSignal(this.data.amendments());
  readonly selectedYear = computed(() => Number(this.year()) || this.summary()?.latestYear || null);
  readonly finance = toSignal(toObservable(this.selectedYear).pipe(switchMap(y => (y ? this.data.finance(y) : of(null)))));

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

  /** Emendas cujo plano de trabalho declara esta função (vínculo indicado, ver glossário). */
  readonly linkedAmendments = computed(() => {
    const view = this.view();
    if (view?.mode !== 'function') return [];
    return (this.amendments() ?? []).filter(a => a.links.function?.code === view.code);
  });
}
