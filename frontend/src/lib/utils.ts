import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function fmt(val: number | null | undefined, decimals = 2): string {
  if (val == null) return '—';
  return val.toLocaleString('de-DE', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

export function fmtPct(val: number | null | undefined): string {
  if (val == null) return '—';
  const sign = val >= 0 ? '+' : '';
  return `${sign}${(val * 100).toFixed(2)}%`;
}

export function fmtEur(val: number | null | undefined): string {
  if (val == null) return '—';
  return `€${fmt(val)}`;
}

export function fmtKeur(val: number | null | undefined): string {
  if (val == null) return '—';
  return `€${fmt(val / 1000, 1)}k`;
}

export function violationColor(v: string): string {
  switch (v) {
    case 'ROTTEN_APPLE': return 'bg-red-100 text-red-800 border border-red-300';
    case 'MIN': return 'bg-amber-100 text-amber-800 border border-amber-300';
    case 'MAX': return 'bg-blue-100 text-blue-800 border border-blue-300';
    default: return 'bg-green-100 text-green-800 border border-green-300';
  }
}

export function violationLabel(v: string): string {
  switch (v) {
    case 'ROTTEN_APPLE': return '🔴 Rotten Apple';
    case 'MIN': return '🟡 MIN Violation';
    case 'MAX': return '🔵 MAX Violation';
    default: return '✅ OK';
  }
}

export function abcColor(abc: string | null): string {
  switch (abc) {
    case 'A': return 'bg-purple-100 text-purple-800';
    case 'B': return 'bg-blue-100 text-blue-800';
    case 'C': return 'bg-gray-100 text-gray-700';
    case 'D': return 'bg-red-50 text-red-700';
    default: return 'bg-gray-50 text-gray-500';
  }
}

export const RRP_HISTORY_LABELS = [
  '01-2023', '04-2023', '07-2023', '10-2023',
  '01-2024', '04-2024', '07-2024', '10-2024',
  '01-2025', '04-2025', '07-2025', '10-2025',
  '01-2026',
];

export const COMMENT_FIELDS: Array<{ key: string; label: string }> = [
  { key: 'comment_04_2023', label: '04-2023' },
  { key: 'comment_07_2023', label: '07-2023' },
  { key: 'comment_04_2024', label: '04-2024' },
  { key: 'comment_07_2024', label: '07-2024' },
  { key: 'comment_01_2025', label: '01-2025' },
  { key: 'comment_04_2025', label: '04-2025' },
  { key: 'comment_07_2025', label: '07-2025' },
  { key: 'comment_10_2025', label: '10-2025' },
  { key: 'comment_01_2026', label: '01-2026' },
  { key: 'comment_04_2026', label: '04-2026 (current)' },
];
