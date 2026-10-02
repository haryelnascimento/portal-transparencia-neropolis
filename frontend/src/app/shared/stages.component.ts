import { Component, input } from '@angular/core';
import { MoneyPipe, PctPipe } from '../core/format';
import { Stages } from '../core/models';
import { InfoTipComponent } from './info-tip.component';

/** As três etapas da despesa pública lado a lado, com a proporção de cada uma sobre o empenhado. */
@Component({
  selector: 'app-stages',
  imports: [InfoTipComponent, MoneyPipe, PctPipe],
  template: `
    <dl class="stages">
      <div><dt>Empenhado <app-info term="empenho" /></dt><dd>{{ value().committed | money }}</dd><span class="bar"><i style="width: 100%"></i></span></div>
      <div><dt>Liquidado <app-info term="liquidacao" /></dt><dd>{{ value().liquidated | money }}</dd><span class="bar"><i [style.width.%]="ratio(value().liquidated)"></i></span><small>{{ value().liquidated | pct: value().committed }} do empenhado</small></div>
      <div><dt>Pago <app-info term="pagamento" /></dt><dd>{{ value().paid | money }}</dd><span class="bar"><i [style.width.%]="ratio(value().paid)"></i></span><small>{{ value().paid | pct: value().committed }} do empenhado</small></div>
    </dl>
  `,
})
export class StagesComponent {
  readonly value = input.required<Stages>();
  ratio(part: number) { const total = this.value().committed; return total ? (part / total) * 100 : 0; }
}
