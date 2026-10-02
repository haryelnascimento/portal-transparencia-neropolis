import { Component, input } from '@angular/core';
import { Params, RouterLink } from '@angular/router';

export interface Crumb { label: string; link?: unknown[]; query?: Params }

/** Caminho percorrido do geral ao específico; cada nível anterior é clicável. */
@Component({
  selector: 'app-breadcrumb',
  imports: [RouterLink],
  template: `
    <nav class="crumbs" aria-label="Você está em">
      <ol>
        @for (crumb of crumbs(); track $index; let last = $last) {
          <li>
            @if (crumb.link && !last) {
              <a [routerLink]="crumb.link" [queryParams]="crumb.query ?? {}">{{ crumb.label }}</a>
            } @else {
              <span [attr.aria-current]="last ? 'page' : null">{{ crumb.label }}</span>
            }
          </li>
        }
      </ol>
    </nav>
  `,
})
export class BreadcrumbComponent {
  readonly crumbs = input.required<Crumb[]>();
}
