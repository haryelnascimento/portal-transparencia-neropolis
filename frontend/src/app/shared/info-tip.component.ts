import { Component, ElementRef, computed, inject, input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { GLOSSARY, GlossaryTerm } from '../core/glossary';

let nextId = 0;

/** Ícone "i" que explica um termo técnico em linguagem simples, com link para o glossário. */
@Component({
  selector: 'app-info',
  imports: [RouterLink],
  host: { class: 'info', '(document:click)': 'onDocumentClick($event)', '(document:keydown.escape)': 'open.set(false)' },
  template: `
    <button type="button" class="info-btn" [attr.aria-expanded]="open()" [attr.aria-controls]="id" [attr.aria-label]="'O que é ' + entry().term + '?'" (click)="toggle($event)">i</button>
    @if (open()) {
      <span class="info-pop" role="dialog" [id]="id" [class.right]="alignRight()" [attr.aria-label]="entry().term">
        <strong>{{ entry().term }}</strong>
        <span>{{ entry().short }}</span>
        <a [routerLink]="['/glossario']" [fragment]="term()" (click)="open.set(false)">Ver no glossário →</a>
      </span>
    }
  `,
})
export class InfoTipComponent {
  readonly term = input.required<GlossaryTerm>();
  readonly entry = computed(() => GLOSSARY[this.term()]);
  readonly open = signal(false);
  readonly alignRight = signal(false);
  readonly id = `info-${nextId++}`;
  private readonly host = inject(ElementRef<HTMLElement>);

  toggle(event: MouseEvent) {
    event.stopPropagation();
    const rect = this.host.nativeElement.getBoundingClientRect();
    this.alignRight.set(rect.left + 300 > window.innerWidth);
    this.open.update(open => !open);
  }

  onDocumentClick(event: MouseEvent) {
    if (this.open() && !this.host.nativeElement.contains(event.target as Node)) this.open.set(false);
  }
}
