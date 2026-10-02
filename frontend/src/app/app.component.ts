import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { catchError, of } from 'rxjs';
import { DataService } from './data.service';
import { Summary, Transfer } from './models';

const EMPTY: Summary = { municipality: { name: 'Nerópolis', state: 'GO', ibgeCode: '5214507' }, updatedAt: '', totals: { received: 0, committed: 0, liquidated: 0, paid: 0 }, counts: { transfers: 0, amendments: 0, agreements: 0, works: 0, suppliers: 0 } };

@Component({
  selector: 'app-root', standalone: true, imports: [CommonModule],
  templateUrl: './app.component.html'
})
export class AppComponent {
  private readonly data = inject(DataService);
  readonly summary$ = this.data.summary().pipe(catchError(() => of(EMPTY)));
  readonly transfers$ = this.data.transfers().pipe(catchError(() => of([] as Transfer[])));
  menuOpen = false;
  format(value: number) { return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value); }
  percentage(part: number, total: number) { return total ? Math.round(part / total * 100) : 0; }
}
