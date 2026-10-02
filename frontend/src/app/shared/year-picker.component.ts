import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';

/** Troca o exercício mantendo o nível de detalhe aberto (query params preservados). */
@Component({
  selector: 'app-year-picker',
  imports: [RouterLink],
  template: `
    <div class="years" role="group" aria-label="Exercício">
      @for (y of years(); track y) {
        <a [routerLink]="[base(), y]" queryParamsHandling="preserve" [class.active]="y === selected()" [attr.aria-current]="y === selected() ? 'true' : null">{{ y }}</a>
      }
    </div>
  `,
})
export class YearPickerComponent {
  readonly years = input.required<number[]>();
  readonly selected = input<number | null>(null);
  readonly base = input.required<string>();
}
