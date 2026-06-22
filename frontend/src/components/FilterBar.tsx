import { useQuery } from '@tanstack/react-query';
import { Search, X } from 'lucide-react';
import { api } from '../api/client';
import type { Filters } from '../api/types';

interface Props {
  filters: Filters;
  onChange: (f: Partial<Filters>) => void;
  onReset: () => void;
}

const VIOLATION_OPTIONS = [
  { value: '', label: 'All violations' },
  { value: 'any', label: 'Any violation' },
  { value: 'ROTTEN_APPLE', label: '🔴 Rotten Apple' },
  { value: 'MIN', label: '🟡 MIN violation' },
  { value: 'MAX', label: '🔵 MAX violation' },
];

const STATUS_OPTIONS = ['Active', 'Inactive', 'Blocked'];
const ABC_OPTIONS = ['A', 'B', 'C', 'D'];

export function FilterBar({ filters, onChange, onReset }: Props) {
  const { data: pg1List } = useQuery({ queryKey: ['pg1'], queryFn: api.getPg1 });
  const { data: pg2List } = useQuery({
    queryKey: ['pg2', filters.pg1],
    queryFn: () => api.getPg2(filters.pg1 || undefined),
  });
  const { data: discountGroups } = useQuery({
    queryKey: ['discount-groups'],
    queryFn: api.getDiscountGroups,
  });

  const activeCount = Object.values(filters).filter(v => v !== '').length;

  return (
    <div className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="flex flex-wrap gap-2 items-center">
        {/* Search */}
        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search part number or description..."
            value={filters.search}
            onChange={e => onChange({ search: e.target.value })}
            className="pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg w-72 focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
          {filters.search && (
            <button onClick={() => onChange({ search: '' })} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
              <X size={13} />
            </button>
          )}
        </div>

        {/* PG1 */}
        <select
          value={filters.pg1}
          onChange={e => onChange({ pg1: e.target.value, pg2: '' })}
          className="text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="">All PG1</option>
          {pg1List?.map(p => (
            <option key={p.code} value={p.code}>{p.code} – {p.description}</option>
          ))}
        </select>

        {/* PG2 */}
        <select
          value={filters.pg2}
          onChange={e => onChange({ pg2: e.target.value })}
          disabled={!filters.pg1}
          className="text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-300 disabled:opacity-50"
        >
          <option value="">All PG2</option>
          {pg2List?.map(p => (
            <option key={p.code} value={p.code}>{p.code} – {p.description}</option>
          ))}
        </select>

        {/* Status */}
        <select
          value={filters.status}
          onChange={e => onChange({ status: e.target.value })}
          className="text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="">All statuses</option>
          {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
        </select>

        {/* ABC */}
        <select
          value={filters.abc_sales}
          onChange={e => onChange({ abc_sales: e.target.value })}
          className="text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="">All ABC</option>
          {ABC_OPTIONS.map(a => <option key={a} value={a}>ABC-Sales: {a}</option>)}
        </select>

        {/* Violations */}
        <select
          value={filters.violation}
          onChange={e => onChange({ violation: e.target.value })}
          className="text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          {VIOLATION_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>

        {/* Discount Group */}
        <select
          value={filters.discount_group}
          onChange={e => onChange({ discount_group: e.target.value })}
          className="text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          <option value="">All DG</option>
          {discountGroups?.map(d => <option key={d} value={d}>{d}</option>)}
        </select>

        {/* Reset */}
        {activeCount > 0 && (
          <button
            onClick={onReset}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800 px-2 py-1.5 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X size={13} />
            Reset ({activeCount})
          </button>
        )}
      </div>
    </div>
  );
}
