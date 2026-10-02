import { Component } from '@angular/core';
import { GLOSSARY, GlossaryEntry } from '../../core/glossary';
import { BreadcrumbComponent } from '../../shared/breadcrumb.component';

const GROUPS: GlossaryEntry['group'][] = ['Receitas', 'Despesas', 'Emendas', 'Fontes de dados'];

@Component({
  selector: 'app-glossary',
  imports: [BreadcrumbComponent],
  template: `
    <section class="explorer">
      <app-breadcrumb [crumbs]="[{ label: 'Glossário' }]" />
      <header class="explorer-title">
        <span class="eyebrow">GLOSSÁRIO</span>
        <h1>Entenda os termos</h1>
        <p class="muted">As contas públicas usam uma linguagem própria. Aqui está o significado de cada termo que aparece no portal, em palavras simples.</p>
      </header>
      @for (group of groups; track group) {
        <h2 class="glossary-group">{{ group }}</h2>
        <dl class="glossary">
          @for (item of byGroup(group); track item.key) {
            <div [id]="item.key"><dt>{{ item.term }}</dt><dd>{{ item.short }}@if (item.more) { <span>{{ item.more }}</span> }</dd></div>
          }
        </dl>
      }
    </section>
  `,
})
export class GlossaryComponent {
  readonly groups = GROUPS;
  private readonly entries = Object.entries(GLOSSARY).map(([key, entry]) => ({ key, ...(entry as GlossaryEntry) }));
  byGroup(group: GlossaryEntry['group']) { return this.entries.filter(e => e.group === group); }
}
