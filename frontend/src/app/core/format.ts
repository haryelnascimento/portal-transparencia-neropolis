import { Pipe, PipeTransform } from '@angular/core';

const BRL = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
const BRL_COMPACT = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', notation: 'compact', maximumFractionDigits: 1 });

export function money(value: number | null | undefined) { return value === null || value === undefined ? '—' : BRL.format(value); }
export function compact(value: number | null | undefined) { return value === null || value === undefined ? '—' : BRL_COMPACT.format(value); }
export function share(part: number, total: number) { return total ? Math.round((part / total) * 1000) / 10 : 0; }
export function pct(value: number) { return `${value.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`; }

@Pipe({ name: 'money' })
export class MoneyPipe implements PipeTransform {
  transform(value: number | null | undefined, mode: 'full' | 'compact' = 'full') { return mode === 'compact' ? compact(value) : money(value); }
}

@Pipe({ name: 'pct' })
export class PctPipe implements PipeTransform {
  /** `value | pct` formata um percentual; `part | pct: total` calcula a participação. */
  transform(value: number, total?: number) { return pct(total === undefined ? value : share(value, total)); }
}
