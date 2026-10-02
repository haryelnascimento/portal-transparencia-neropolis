import { DatePipe } from '@angular/common';
import { Component, computed, inject, input } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { DataService } from '../../core/data.service';
import { MoneyPipe, PctPipe } from '../../core/format';
import { BudgetBlock } from '../../core/models';
import { BreadcrumbComponent } from '../../shared/breadcrumb.component';
import { InfoTipComponent } from '../../shared/info-tip.component';

const BUDGET_LABELS: [keyof BudgetBlock, string][] = [
  ['organ', 'Órgão'], ['unit', 'Secretaria / unidade'], ['function', 'Área de governo'], ['subfunction', 'Subárea'],
  ['program', 'Programa'], ['action', 'Projeto / atividade'], ['element', 'Tipo de despesa'], ['fundingSource', 'Fonte do recurso'],
];

@Component({
  selector: 'app-amendment-detail',
  imports: [BreadcrumbComponent, DatePipe, InfoTipComponent, MoneyPipe, PctPipe, RouterLink],
  templateUrl: './amendment-detail.component.html',
})
export class AmendmentDetailComponent {
  private readonly data = inject(DataService);
  readonly id = input.required<string>();
  readonly summary = toSignal(this.data.summary());
  readonly amendments = toSignal(this.data.amendments());
  readonly amendment = computed(() => this.amendments()?.find(a => a.id === this.id()) ?? null);
  readonly budgetLabels = BUDGET_LABELS;
  readonly loaded = computed(() => this.amendments() !== undefined);
}
