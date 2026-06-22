import { useState } from 'react';
import { MessageSquare, ChevronDown, ChevronUp, AlertTriangle, Info } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { api } from '../api/client';
import type { Product, ProductUpdate } from '../api/types';
import { fmt, fmtEur, fmtPct, cn, violationLabel, abcColor } from '../lib/utils';
import { Badge } from './ui/Badge';
import { Tooltip } from './ui/Tooltip';
import { InlineEdit, TextEdit } from './ui/InlineEdit';
import { CommentHistoryModal } from './panels/CommentHistoryModal';
import { PriceHistoryPopover } from './panels/PriceHistoryPopover';
import { BenchmarkPanel } from './panels/BenchmarkPanel';

interface Props {
  product: Product;
}

export function ProductCard({ product }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const qc = useQueryClient();
  const calc = product.calc;

  const mutation = useMutation({
    mutationFn: (data: ProductUpdate) => api.updateProduct(product.id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['products'] }),
  });

  const save = async (data: ProductUpdate) => {
    await mutation.mutateAsync(data);
  };

  const violationStatus = calc?.future_violation ?? 'OK';

  const cardBorder = {
    ROTTEN_APPLE: 'border-l-4 border-l-red-500 bg-red-50',
    MIN: 'border-l-4 border-l-amber-500 bg-amber-50',
    MAX: 'border-l-4 border-l-blue-500 bg-blue-50',
    OK: 'border-l-4 border-l-transparent bg-white',
  }[violationStatus];

  return (
    <div className={cn('rounded-lg shadow-sm border border-gray-200', cardBorder)}>
      {/* ── Top bar ─────────────────────────────────────────────── */}
      <div className="px-4 py-3 flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono font-bold text-sm text-gray-900">{product.material_10}</span>
            {product.status && (
              <Badge variant={product.status.toLowerCase().includes('active') ? 'green' : 'gray'}>
                {product.status}
              </Badge>
            )}
            {violationStatus !== 'OK' && (
              <Badge variant={violationStatus === 'ROTTEN_APPLE' ? 'red' : violationStatus === 'MIN' ? 'amber' : 'blue'}>
                {violationLabel(violationStatus)}
              </Badge>
            )}
            {calc?.flag_ipp_change_above_10 && (
              <Badge variant="red">IPP Δ&gt;10%</Badge>
            )}
            {calc?.flag_minderrabatt && (
              <Badge variant="amber">Minderrabatt</Badge>
            )}
          </div>
          <div className="text-xs text-gray-500 mt-0.5 truncate">
            {product.description_en || product.description_de || '—'}
          </div>
          {product.description_de && product.description_en && (
            <div className="text-xs text-gray-400 truncate">{product.description_de}</div>
          )}
        </div>

        {/* Right: PG + ABC badges */}
        <div className="flex flex-col items-end gap-1 shrink-0">
          <div className="flex gap-1 flex-wrap justify-end">
            {product.pg1_description && (
              <Tooltip content={`${product.pg1_current} › ${product.pg2_description}`}>
                <Badge variant="gray">{product.pg1_description?.split(' ').slice(1).join(' ') || product.pg1_current}</Badge>
              </Tooltip>
            )}
            {product.pg3_description && (
              <Badge variant="gray" className="text-xs">{product.pg3_description}</Badge>
            )}
          </div>
          <div className="flex gap-1">
            {(['abc_sales', 'abc_qty', 'abc_vehicle_population'] as const).map(k => {
              const val = product[k] as string | null;
              return val ? (
                <Tooltip key={k} content={k.replace('abc_', 'ABC ').replace('_', ' ')}>
                  <span className={cn('text-xs font-bold px-1.5 py-0.5 rounded', abcColor(val))}>{val}</span>
                </Tooltip>
              ) : null;
            })}
          </div>
        </div>
      </div>

      {/* ── Core Price Row ───────────────────────────────────────── */}
      <div className="px-4 pb-3 grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-gray-100 pt-3">

        {/* RRP */}
        <div className="space-y-1">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">RRP</div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Current:</span>
            <PriceHistoryPopover product={product}>
              <span className="text-sm font-medium text-gray-700 underline decoration-dotted cursor-help">
                {fmtEur(product.rrp_current_01_2026)}
              </span>
            </PriceHistoryPopover>
          </div>
          <InlineEdit
            label="Future:"
            value={product.rrp_future_04_2026}
            onSave={v => save({ rrp_future_04_2026: v })}
            highlight
          />
          {calc?.rrp_change_pct != null && (
            <span className={cn('text-xs font-medium', calc.rrp_change_pct >= 0 ? 'text-green-600' : 'text-red-600')}>
              {fmtPct(calc.rrp_change_pct)}
            </span>
          )}
        </div>

        {/* IPP */}
        <div className="space-y-1">
          <Tooltip content="Invoice Price Point — worst-case customer payment (MAX of RRP-discount or NP)">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide flex items-center gap-1">
              IPP <Info size={10} className="text-gray-300" />
            </div>
          </Tooltip>
          <div className="text-xs text-gray-500">
            Current: <strong className="text-gray-800">{fmtEur(calc?.ipp_final_current)}</strong>
          </div>
          <div className="text-xs text-gray-500">
            Future: <strong className="text-gray-800">{fmtEur(calc?.ipp_final_future)}</strong>
          </div>
          {calc?.ipp_change_pct != null && (
            <span className={cn('text-xs font-medium', calc.ipp_change_pct >= 0 ? 'text-green-600' : 'text-red-600')}>
              {fmtPct(calc.ipp_change_pct)}
            </span>
          )}
        </div>

        {/* NPP */}
        <div className="space-y-1">
          <Tooltip content="Net Price Point DE21 — actual price level for German market">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide flex items-center gap-1">
              NPP DE21 <Info size={10} className="text-gray-300" />
            </div>
          </Tooltip>
          <div className="text-xs text-gray-500">
            Current: <strong className="text-gray-800">{fmtEur(calc?.npp_current_de21)}</strong>
          </div>
          <div className="text-xs text-gray-500">
            Future: <strong className={cn(violationStatus !== 'OK' ? 'text-red-700' : 'text-gray-800')}>
              {fmtEur(calc?.npp_future_de21)}
            </strong>
          </div>
          {product.minimum_npp_eur != null && (
            <div className="text-xs text-gray-400">
              Min: {fmtEur(product.minimum_npp_eur)} / Max: {fmtEur(product.maximum_npp_eur)}
            </div>
          )}
        </div>

        {/* NP Platinum */}
        <div className="space-y-1">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">NP Platinum</div>
          <InlineEdit
            label="Current:"
            value={product.np_platinum_lc}
            onSave={v => save({ np_platinum_lc: v })}
            highlight={product.np_platinum_manual_override || false}
          />
          <div className="text-xs text-gray-500">
            Future: <strong className="text-gray-800">{fmtEur(calc?.np_platinum_lc_future)}</strong>
          </div>
          {product.np_platinum_manual_override && (
            <Tooltip content={product.reason_manual_override || 'Manual override active'}>
              <Badge variant="amber" className="cursor-help">Override ⚠</Badge>
            </Tooltip>
          )}
        </div>
      </div>

      {/* ── Margin + Discount Row ────────────────────────────────── */}
      <div className="px-4 pb-2 flex flex-wrap items-center gap-3 text-xs border-t border-gray-100 pt-2">
        <div className="flex items-center gap-1">
          <span className="text-gray-400">Margin:</span>
          <span className={cn('font-semibold', (calc?.new_margin ?? 0) < 0 ? 'text-red-600' : 'text-gray-700')}>
            {calc?.new_margin != null ? `${(calc.new_margin * 100).toFixed(1)}%` : '—'}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-gray-400">DG:</span>
          <span className="font-medium text-gray-700">{product.discount_group_future || product.discount_group_current || '—'}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-gray-400">Disc:</span>
          <span className="text-gray-700">{product.future_basic_discount}% + {product.future_add_discount}%</span>
        </div>
        {product.predecessor && (
          <Tooltip content={`Predecessor: ${product.predecessor}`}>
            <span className="text-gray-400 cursor-help">⬅ {product.predecessor}</span>
          </Tooltip>
        )}
        {product.successor && product.successor !== '9999999999' && (
          <Tooltip content={`Successor: ${product.successor}`}>
            <span className="text-gray-400 cursor-help">➡ {product.successor}</span>
          </Tooltip>
        )}
        {/* NP Tier pills */}
        {calc?.np_gold_lc_future != null && (
          <div className="flex gap-1 ml-auto">
            {[
              { label: 'Plat', val: calc.np_platinum_lc_future, color: 'bg-gray-100 text-gray-700' },
              { label: 'Gold', val: calc.np_gold_lc_future, color: 'bg-yellow-50 text-yellow-700' },
              { label: 'Silv', val: calc.np_silver_lc_future, color: 'bg-gray-50 text-gray-600' },
              { label: 'Brnz', val: calc.np_bronze_lc_future, color: 'bg-orange-50 text-orange-700' },
            ].map(t => (
              <Tooltip key={t.label} content={`NP ${t.label}: ${fmtEur(t.val)}`}>
                <span className={cn('px-1.5 py-0.5 rounded text-xs font-medium cursor-help', t.color)}>
                  {t.label} {fmtEur(t.val)}
                </span>
              </Tooltip>
            ))}
          </div>
        )}
      </div>

      {/* ── Comments Row ────────────────────────────────────────── */}
      <div className="px-4 pb-2 flex items-center gap-2 border-t border-gray-100 pt-2">
        <button
          onClick={() => setShowComments(true)}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-800 transition-colors"
        >
          <MessageSquare size={13} />
          <span>Comments</span>
        </button>
        {product.comment_04_2026 && (
          <span className="text-xs text-gray-600 italic truncate flex-1">
            "{product.comment_04_2026}"
          </span>
        )}
        {!product.comment_04_2026 && (
          <TextEdit
            value={null}
            onSave={v => save({ comment_04_2026: v })}
            placeholder="Add comment for 04-2026..."
            className="flex-1"
          />
        )}
      </div>

      {/* ── Price Proposals (if violation) ──────────────────────── */}
      {calc && violationStatus !== 'OK' && (
        <div className="px-4 pb-2 border-t border-gray-100 pt-2">
          <div className="flex items-center gap-2">
            <AlertTriangle size={13} className="text-amber-600 shrink-0" />
            <span className="text-xs text-gray-600">
              Suggested RRP to fix: {' '}
              {calc.price_proposal_min_rrp != null && (
                <button
                  onClick={() => save({ rrp_future_04_2026: calc.price_proposal_min_rrp })}
                  className="font-semibold text-blue-700 hover:underline"
                  title="Apply this suggestion"
                >
                  {fmtEur(calc.price_proposal_min_rrp)} (min)
                </button>
              )}
              {calc.price_proposal_max_rrp != null && (
                <>
                  {' / '}
                  <button
                    onClick={() => save({ rrp_future_04_2026: calc.price_proposal_max_rrp })}
                    className="font-semibold text-blue-700 hover:underline"
                  >
                    {fmtEur(calc.price_proposal_max_rrp)} (max)
                  </button>
                </>
              )}
            </span>
          </div>
        </div>
      )}

      {/* ── Expand for Benchmarks + Details ─────────────────────── */}
      <div className="px-4 pb-2 border-t border-gray-100 pt-2">
        <button
          onClick={() => setExpanded(e => !e)}
          className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 transition-colors"
        >
          {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          {expanded ? 'Less' : 'Benchmarks & Details'}
        </button>
      </div>

      {expanded && calc && (
        <div className="px-4 pb-4 space-y-3 border-t border-gray-100 pt-3 fade-in">
          {/* Benchmarks */}
          <BenchmarkPanel product={product} calc={calc} />

          {/* Volume */}
          {(calc.ipp_volume_current != null || calc.ipp_volume_future != null) && (
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-gray-400 mb-1 font-semibold">IPP Volume</div>
                <div>Cur: <strong>{fmtEur(calc.ipp_volume_current)}</strong></div>
                <div>Fut: <strong>{fmtEur(calc.ipp_volume_future)}</strong></div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-gray-400 mb-1 font-semibold">Sales</div>
                <div>Qty 12M: <strong>{fmt(product.qty_12m, 0)}</strong></div>
                <div>IPP 12M: <strong>{fmtEur(product.ipp_12m)}</strong></div>
              </div>
            </div>
          )}

          {/* Editable extra fields */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="text-xs text-gray-400 mb-1 font-semibold">Min/Max NPP Corridor</div>
              <div className="flex gap-2">
                <InlineEdit label="Min:" value={product.minimum_npp_eur} onSave={v => save({ minimum_npp_eur: v })} />
                <InlineEdit label="Max:" value={product.maximum_npp_eur} onSave={v => save({ maximum_npp_eur: v })} />
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-400 mb-1 font-semibold">PS Action</div>
              <select
                value={product.ps_action || ''}
                onChange={e => save({ ps_action: e.target.value || null })}
                className="text-xs border border-gray-200 rounded px-2 py-1 w-full"
              >
                <option value="">—</option>
                <option value="APPROVE">Approve</option>
                <option value="REVIEW">Review</option>
                <option value="ESCALATE">Escalate</option>
                <option value="PHASE_OUT">Phase Out</option>
              </select>
            </div>
          </div>

          {/* Manual Override */}
          <div className="flex items-start gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={product.np_platinum_manual_override || false}
                onChange={e => save({ np_platinum_manual_override: e.target.checked })}
                className="rounded"
              />
              <span className="text-xs text-gray-600">NP Manual Override</span>
            </label>
            {product.np_platinum_manual_override && (
              <TextEdit
                value={product.reason_manual_override}
                onSave={v => save({ reason_manual_override: v })}
                placeholder="Reason for override..."
                className="flex-1"
              />
            )}
          </div>

          {/* Flags row */}
          <div className="flex flex-wrap gap-2 text-xs">
            {product.fg_pkw && <Badge variant="gray">PKW</Badge>}
            {product.fg_nkw && <Badge variant="gray">NKW</Badge>}
            {product.fg_krad && <Badge variant="gray">KRAD</Badge>}
            {product.fg_motor && <Badge variant="gray">MOTOR</Badge>}
            {product.eznrart && <Badge variant="gray">EZNR: {product.eznrart}</Badge>}
            {product.fepaa != null && <Badge variant="gray">FEPAA: {fmt(product.fepaa, 0)}</Badge>}
            {product.material_13 && <span className="text-gray-400">Mat13: {product.material_13}</span>}
          </div>
        </div>
      )}

      {/* Comment History Modal */}
      <CommentHistoryModal
        product={product}
        open={showComments}
        onClose={() => setShowComments(false)}
        onSave={async (field, value) => {
          await save({ [field]: value } as ProductUpdate);
        }}
      />
    </div>
  );
}
