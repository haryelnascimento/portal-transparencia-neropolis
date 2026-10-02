import { Routes } from '@angular/router';
import { AmendmentDetailComponent } from './features/amendments/amendment-detail.component';
import { AmendmentListComponent } from './features/amendments/amendment-list.component';
import { ExpenseExplorerComponent } from './features/expenses/expense-explorer.component';
import { GlossaryComponent } from './features/glossary/glossary.component';
import { OverviewComponent } from './features/overview/overview.component';
import { RevenueExplorerComponent } from './features/revenues/revenue-explorer.component';

/** Do geral ao específico: visão geral → receitas/despesas por ano → linha, área ou tipo de gasto → emenda. */
export const routes: Routes = [
  { path: '', component: OverviewComponent, title: 'Transparência Nerópolis' },
  { path: 'receitas', component: RevenueExplorerComponent, title: 'Receitas · Transparência Nerópolis' },
  { path: 'receitas/:year', component: RevenueExplorerComponent, title: 'Receitas · Transparência Nerópolis' },
  { path: 'despesas', component: ExpenseExplorerComponent, title: 'Despesas · Transparência Nerópolis' },
  { path: 'despesas/:year', component: ExpenseExplorerComponent, title: 'Despesas · Transparência Nerópolis' },
  { path: 'emendas', component: AmendmentListComponent, title: 'Emendas · Transparência Nerópolis' },
  { path: 'emendas/:id', component: AmendmentDetailComponent, title: 'Emenda · Transparência Nerópolis' },
  { path: 'glossario', component: GlossaryComponent, title: 'Glossário · Transparência Nerópolis' },
  { path: '**', redirectTo: '' },
];
