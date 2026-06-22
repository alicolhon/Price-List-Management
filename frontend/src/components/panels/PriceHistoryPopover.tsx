import { useState, useRef, useCallback } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { Portal } from '../ui/Portal';
import { RRP_HISTORY_LABELS, fmtEur, fmtPct, cn } from '../../lib/utils';
import type { Product } from '../../api/types';

const RRP_KEYS = [
  'rrp_01_2023', 'rrp_04_2023', 'rrp_07_2023', 'rrp_10_2023',
  'rrp_01_2024', 'rrp_04_2024', 'rrp_07_2024', 'rrp_10_2024',
  'rrp_01_2025', 'rrp_04_2025', 'rrp_07_2025', 'rrp_10_2025',
  'rrp_current_01_2026',
] as const;

interface Props {
  product: Product;
  children: React.ReactNode;
}

export function PriceHistoryPopover({ product, children }: Props) {
  const [show, setShow] = useState(false);
  const [pos, setPos] = useState({ x: 0, y: 0, alignRight: false });
  const triggerRef = useRef<HTMLDivElement>(null);

  const values: (number | null)[] = RRP_KEYS.map(
    k => (product as unknown as Record<string, unknown>)[k] as number | null,
  );
  const validValues = values.filter((v): v is number => v != null);
  const minVal = validValues.length ? Math.min(...validValues) : 0;
  const maxVal = validValues.length ? Math.max(...validValues) : 1;

  const getHeight = (v: number | null) => {
    if (v == null || maxVal === minVal) return 50;
    return 10 + ((v - minVal) / (maxVal - minVal)) * 40;
  };

  const firstVal = validValues[0];
  const lastVal = validValues[validValues.length - 1];
  const trend = lastVal != null && firstVal != null ? lastVal / firstVal - 1 : null;

  const POPOVER_WIDTH = 320;

  const handleMouseEnter = useCallback(() => {
    if (triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      const spaceRight = window.innerWidth - rect.left;
      const alignRight = spaceRight < POPOVER_WIDTH + 16;
      setPos({
        x: alignRight ? rect.right : rect.left,
        y: rect.top,
        alignRight,
      });
    }
    setShow(true);
  }, []);

  return (
    <div
      ref={triggerRef}
      className="inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={() => setShow(false)}
    >
      {children}
      {show && (
        <Portal>
          <div
            className="fixed z-[9999] bg-white border border-gray-200 rounded-xl shadow-2xl p-4 fade-in"
            style={{
              width: POPOVER_WIDTH,
              top: pos.y - 8,
              transform: 'translateY(-100%)',
              ...(pos.alignRight
                ? { right: window.innerWidth - pos.x }
                : { left: pos.x }),
            }}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-gray-700">RRP History</span>
              {trend != null && (
                <span className={cn('text-xs font-medium flex items-center gap-1', trend >= 0 ? 'text-green-700' : 'text-red-600')}>
                  {trend >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                  {fmtPct(trend)} (2023→2026)
                </span>
              )}
            </div>

            {/* Mini bar chart */}
            <div className="flex items-end gap-1 h-16 mb-3">
              {values.map((v, i) => (
                <div
                  key={i}
                  className="flex-1 flex flex-col items-center gap-0.5"
                  title={`${RRP_HISTORY_LABELS[i]}: ${fmtEur(v)}`}
                >
                  <div
                    className={cn('w-full rounded-t transition-all', v == null ? 'bg-gray-100' : 'bg-blue-400')}
                    style={{ height: `${getHeight(v)}px` }}
                  />
                </div>
              ))}
            </div>

            {/* Table */}
            <div className="grid grid-cols-2 gap-1 max-h-48 overflow-y-auto">
              {values.map((v, i) => (
                <div key={i} className="flex justify-between items-center text-xs py-0.5 px-1 hover:bg-gray-50 rounded">
                  <span className="text-gray-500">{RRP_HISTORY_LABELS[i]}</span>
                  <span className={cn('font-medium', v == null ? 'text-gray-300' : 'text-gray-900')}>
                    {fmtEur(v)}
                  </span>
                </div>
              ))}
              {product.rrp_future_04_2026 != null && (
                <div className="flex justify-between items-center text-xs py-0.5 px-1 bg-blue-50 rounded col-span-2">
                  <span className="text-blue-600 font-medium">04-2026 (Future)</span>
                  <span className="font-bold text-blue-700">{fmtEur(product.rrp_future_04_2026)}</span>
                </div>
              )}
            </div>
          </div>
        </Portal>
      )}
    </div>
  );
}
