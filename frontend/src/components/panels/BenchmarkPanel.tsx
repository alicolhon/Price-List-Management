import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { fmtEur, fmtPct, cn } from '../../lib/utils';
import type { Product, CalculationResult } from '../../api/types';

interface Props {
  product: Product;
  calc: CalculationResult;
}

export function BenchmarkPanel({ product, calc }: Props) {
  const [expanded, setExpanded] = useState(false);

  const benchmarks = [
    {
      label: 'PL Intercars',
      npp: product.npp_pl_intercars,
      dev: calc.deviation_intercars,
      color: 'blue',
    },
    {
      label: 'Autonet',
      npp: product.npp_autonet,
      dev: calc.deviation_autonet,
      color: 'indigo',
    },
    {
      label: 'Truck (HCV)',
      npp: product.npp_truck,
      dev: calc.deviation_truck,
      color: 'teal',
    },
    {
      label: 'LKQ Tender/PEP',
      npp: product.npp_lkq,
      dev: calc.deviation_lkq,
      color: 'violet',
    },
  ].filter(b => b.npp != null);

  if (benchmarks.length === 0) return null;

  const devColor = (dev: number | null) => {
    if (dev == null) return 'text-gray-400';
    if (Math.abs(dev) <= 0.10) return 'text-green-600';
    if (Math.abs(dev) <= 0.20) return 'text-amber-600';
    return 'text-red-600';
  };

  return (
    <div className="border border-gray-100 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(e => !e)}
        className="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
      >
        <span className="text-xs font-semibold text-gray-600">
          Benchmarks ({benchmarks.length})
        </span>
        <span className="flex items-center gap-1">
          {/* Quick inline preview */}
          {!expanded && benchmarks.slice(0, 2).map(b => (
            <span key={b.label} className={cn('text-xs font-medium', devColor(b.dev))}>
              {b.label.split(' ')[0]}: {fmtPct(b.dev)}
            </span>
          ))}
          {expanded ? <ChevronUp size={14} className="text-gray-400 ml-1" /> : <ChevronDown size={14} className="text-gray-400 ml-1" />}
        </span>
      </button>

      {expanded && (
        <div className="divide-y divide-gray-50">
          {benchmarks.map(b => (
            <div key={b.label} className="flex items-center justify-between px-3 py-2">
              <span className="text-xs text-gray-600 font-medium w-28">{b.label}</span>
              <span className="text-sm font-mono text-gray-900">{fmtEur(b.npp)}</span>
              <span className={cn('text-xs font-semibold w-16 text-right', devColor(b.dev))}>
                {b.dev != null ? fmtPct(b.dev) : '—'}
              </span>
              {/* Visual deviation bar */}
              <div className="w-16 h-2 bg-gray-100 rounded-full overflow-hidden">
                {b.dev != null && (
                  <div
                    className={cn(
                      'h-full rounded-full transition-all',
                      Math.abs(b.dev) <= 0.10 ? 'bg-green-400' : Math.abs(b.dev) <= 0.20 ? 'bg-amber-400' : 'bg-red-400',
                    )}
                    style={{
                      width: `${Math.min(100, Math.abs(b.dev) * 500)}%`,
                      marginLeft: b.dev < 0 ? 'auto' : '0',
                    }}
                  />
                )}
              </div>
            </div>
          ))}

          {/* AT/CH Alignment */}
          {(calc.rrp_at_alignment || calc.rrp_ch_alignment) && (
            <div className="px-3 py-2 bg-gray-50">
              <div className="text-xs font-semibold text-gray-500 mb-1">AT/CH Alignment</div>
              <div className="flex gap-4">
                {calc.rrp_at_alignment != null && (
                  <span className="text-xs text-gray-600">AT: <strong>{fmtEur(calc.rrp_at_alignment)}</strong></span>
                )}
                {calc.rrp_ch_alignment != null && (
                  <span className="text-xs text-gray-600">CH: <strong>{fmtEur(calc.rrp_ch_alignment)}</strong></span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
