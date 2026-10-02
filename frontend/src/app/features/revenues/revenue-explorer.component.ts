import { Component, computed, inject, input } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { of, switchMap } from 'rxjs';
import { DataService } from '../../core/data.service';
import { compact, MoneyPipe, pct, PctPipe, share } from '../../core/format';
import { GlossaryTerm } from '../../core/glossary';
import { OriginKey, RevenueNode } from '../../core/models';
import { ancestorsOf, childrenOf, hasChildren } from '../../core/tree';
import { BarListComponent, BarRow } from '../../shared/bar-list.component';
import { BreadcrumbComponent, Crumb } from '../../shared/breadcrumb.component';
import { InfoTipComponent } from '../../shared/info-tip.component';
import { YearPickerComponent } from '../../shared/year-picker.component';

/** Termo do glossário associado a uma linha de receita, pelo nome. */
function termFor(name: string): GlossaryTerm | null {
  const n = name.toLowerCase();
  if (n.includes('fundo de participação dos municípios')) return 'fpm';
  if (n.includes('icms')) return 'icms';
  if (n.includes('ipva')) return 'ipva';
  if (n.includes('sistema único de saúde') || n.includes('sus')) return 'sus';
  if (n.includes('fundo de manutenção e desenvolvimento da educação')) return 'fundeb';
  if (n.includes('serviços de qualquer natureza')) return 'iss';
  if (n.includes('predial e territorial urbana')) return 'iptu';
  if (n.includes('inter vivos')) return 'itbi';
  if (n.startsWith('transferências')) return 'transferencias';
  return null;
}

interface View { title: string; value: number; parentValue: number | null; children: RevenueNode[]; crumbs: Crumb[]; term: GlossaryTerm | null; code: string | null }

@Component({
  selector: 'app-revenue-explorer',
  imports: [BarListComponent, BreadcrumbComponent, InfoTipComponent, MoneyPipe, PctPipe, RouterLink, YearPickerComponent],
  templateUrl: './revenue-explorer.component.html',
})
export class RevenueExplorerComponent {
  private readonly data = inject(DataService);
  /** Parâmetros de rota: /receitas/:year?conta=<código>&origem=<chave>. */
  readonly year = input<string>();
  readonly conta = input<string>();
  readonly origem = input<OriginKey>();

  readonly summary = toSignal(this.data.summary());
  readonly selectedYear = computed(() => Number(this.year()) || this.summary()?.latestYear || null);
  readonly finance = toSignal(toObservable(this.selectedYear).pipe(switchMap(y => (y ? this.data.finance(y) : of(null)))));

  readonly view = computed<View | null>(() => {
    const finance = this.finance();
    if (!finance) return null;
    const { tree, gross, origins } = finance.revenues;
    const year = finance.year;
    const root: Crumb = { label: `Receitas ${year}`, link: ['/receitas', year] };
    const origin = origins.find(o => o.key === this.origem());
    const node = tree.find(n => n.code === this.conta());

    if (node) {
      const parent = tree.find(n => n.code === node.parent);
      const crumbs = [root, ...ancestorsOf(tree, node.code).map(a => ({ label: a.name, link: ['/receitas', year], query: { conta: a.code } })), { label: node.name }];
      return { title: node.name, value: node.value, parentValue: parent?.value ?? gross, children: childrenOf(tree, node.code), crumbs, term: termFor(node.name), code: node.code };
    }
    if (origin) {
      const children = tree.filter(n => origin.codes.includes(n.code));
      return { title: origin.label, value: origin.value, parentValue: gross, children: children.length === 1 ? childrenOf(tree, children[0].code) : children, crumbs: [root, { label: origin.label }], term: origin.key === 'own' ? 'arrecadacao-propria' : origin.key === 'fundeb' ? 'fundeb' : 'origem', code: null };
    }
    return { title: 'Todas as receitas', value: gross, parentValue: null, children: childrenOf(tree, null), crumbs: [root], term: 'receita-bruta', code: null };
  });

  readonly notFound = computed(() => !!this.finance() && !!this.conta() && !this.finance()!.revenues.tree.some(n => n.code === this.conta()));

  readonly rows = computed<BarRow[]>(() => {
    const view = this.view();
    const tree = this.finance()?.revenues.tree ?? [];
    if (!view) return [];
    // Itens com o mesmo nome (ex.: "Transferências da União" correntes e de capital) recebem o nível raiz no rótulo.
    const repeated = new Set(view.children.map(c => c.name).filter((name, i, all) => all.indexOf(name) !== i));
    const rootName = (code: string) => tree.find(n => n.code === ancestorsOf(tree, code)[0]?.code)?.name.replace(/^Receitas /, '').toLowerCase();
    return [...view.children].sort((a, b) => b.value - a.value).map(child => ({
      key: child.code,
      label: repeated.has(child.name) ? `${child.name} (${rootName(child.code) ?? child.code})` : child.name,
      value: child.value,
      display: compact(child.value),
      note: pct(share(child.value, view.value)),
      title: `${child.name}: ${compact(child.value)} — ${pct(share(child.value, view.value))} de “${view.title}”`,
      link: hasChildren(tree, child.code) ? ['/receitas', this.selectedYear()] : null,
      query: { conta: child.code },
    }));
  });

  readonly originRows = computed<BarRow[]>(() => {
    const finance = this.finance();
    if (!finance) return [];
    return finance.revenues.origins.filter(o => o.value > 0).map(o => ({
      key: o.key, label: o.label, value: o.value, display: compact(o.value), note: pct(share(o.value, finance.revenues.gross)),
      link: o.codes.length ? ['/receitas', finance.year] : null, query: { origem: o.key },
    }));
  });
}
