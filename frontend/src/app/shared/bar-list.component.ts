import { Component, computed, input } from '@angular/core';
import { NgTemplateOutlet } from '@angular/common';
import { Params, RouterLink } from '@angular/router';

export interface BarRow {
  key: string;
  label: string;
  value: number;
  display: string;
  note?: string;
  title?: string;
  link?: unknown[] | null;
  query?: Params;
}

/**
 * Barras horizontais de série única (magnitude por categoria). A largura é proporcional ao maior valor,
 * ou à base informada em `scale` quando as barras representam participação num total.
 * Linhas com `link` levam ao próximo nível de detalhe.
 */
@Component({
  selector: 'app-bar-list',
  imports: [NgTemplateOutlet, RouterLink],
  template: `
    <ul class="hbars">
      @for (row of bars(); track row.key) {
        <li>
          @if (row.link) {
            <a class="row link" [routerLink]="row.link" [queryParams]="row.query" [title]="row.title ?? row.label + ': ' + row.display">
              <ng-container *ngTemplateOutlet="content; context: { $implicit: row }" />
            </a>
          } @else {
            <div class="row" [title]="row.title ?? row.label + ': ' + row.display">
              <ng-container *ngTemplateOutlet="content; context: { $implicit: row }" />
            </div>
          }
        </li>
      } @empty {
        <li class="empty-row">Sem valores publicados para este nível.</li>
      }
    </ul>
    <ng-template #content let-row>
      <span class="label">{{ row.label }}</span>
      <span class="track"><i [style.width.%]="row.width"></i></span>
      <span class="value">{{ row.display }}@if (row.note) { <small>{{ row.note }}</small> }</span>
      <span class="chevron" aria-hidden="true">{{ row.link ? '›' : '' }}</span>
    </ng-template>
  `,
})
export class BarListComponent {
  readonly rows = input.required<BarRow[]>();
  readonly scale = input<number | null>(null);
  readonly bars = computed(() => {
    const rows = this.rows();
    const max = this.scale() ?? Math.max(...rows.map(r => r.value), 0);
    return rows.map(row => ({ ...row, width: max > 0 ? Math.max((row.value / max) * 100, 0) : 0 }));
  });
}
