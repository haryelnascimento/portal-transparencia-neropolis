import { Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { DataService } from '../../core/data.service';
import { MoneyPipe } from '../../core/format';
import { BreadcrumbComponent } from '../../shared/breadcrumb.component';
import { InfoTipComponent } from '../../shared/info-tip.component';

@Component({
  selector: 'app-amendment-list',
  imports: [BreadcrumbComponent, InfoTipComponent, MoneyPipe, RouterLink],
  template: `
    <section class="explorer">
      <app-breadcrumb [crumbs]="[{ label: 'Emendas parlamentares' }]" />
      <header class="explorer-title">
        <span class="eyebrow">EMENDAS PARLAMENTARES</span>
        <h1>Emendas Pix para Nerópolis <app-info term="transferencia-especial" /></h1>
        <p class="big">{{ total() | money }} <small>repassados</small></p>
        <p class="muted">{{ list().length }} emendas indicadas por parlamentares desde 2020. Clique em uma emenda para seguir o caminho do dinheiro.</p>
      </header>
      <ul class="link-list cards-list">
        @for (a of list(); track a.id) {
          <li>
            <a [routerLink]="['/emendas', a.id]">
              <strong>{{ a.purpose }}</strong>
              <span>{{ a.parliamentarian }} · {{ a.area }} · emenda {{ a.year }}</span>
              <span class="amounts"><em>{{ a.values.transferred | money }}</em> de {{ a.values.planned | money }} repassados</span>
              <span class="status" [class.pending]="a.values.reportedExecuted === null"><i></i>Prestação de contas: {{ a.managementReport ? a.managementReport.status.toLowerCase() : 'não enviada' }}</span>
              <b aria-hidden="true">›</b>
            </a>
          </li>
        }
      </ul>
      <p class="source">Fonte: Transferegov — transferências especiais <app-info term="transferegov" /></p>
    </section>
  `,
})
export class AmendmentListComponent {
  private readonly data = inject(DataService);
  readonly amendments = toSignal(this.data.amendments());
  readonly list = computed(() => [...(this.amendments() ?? [])].sort((a, b) => b.values.planned - a.values.planned));
  readonly total = computed(() => this.list().reduce((sum, a) => sum + a.values.transferred, 0));
}
