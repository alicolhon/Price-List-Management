import { useQuery } from '@tanstack/react-query';
import { TrendingUp, AlertTriangle, Package, DollarSign } from 'lucide-react';
import { api } from '../api/client';
import { fmtKeur, fmtPct, cn } from '../lib/utils';

export function SummaryBar() {
  const { data } = useQuery({
    queryKey: ['summary'],
    queryFn: api.getSummary,
    refetchInterval: 30_000,
  });

  if (!data) return (
    <div className="bg-white border-b border-gray-200 px-6 py-3 flex gap-6 text-sm animate-pulse">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="h-8 w-24 bg-gray-100 rounded" />
      ))}
    </div>
  );

  const volChange = data.weighted_ipp_change_pct;

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-3 flex flex-wrap gap-x-8 gap-y-2 items-center text-sm">
      <Stat
        icon={<Package size={14} className="text-gray-500" />}
        label="Products"
        value={`${data.active_products.toLocaleString()} / ${data.total_products.toLocaleString()}`}
        sub="active / total"
      />
      <Stat
        icon={<DollarSign size={14} className="text-blue-500" />}
        label="IPP Volume"
        value={fmtKeur(data.total_ipp_volume_current)}
        sub={`→ ${fmtKeur(data.total_ipp_volume_future)}`}
      />
      <Stat
        icon={<TrendingUp size={14} className={cn(volChange != null && volChange >= 0 ? 'text-green-500' : 'text-red-500')} />}
        label="Wtd IPP Chg"
        value={fmtPct(data.weighted_ipp_change_pct)}
        sub={`RRP: ${fmtPct(data.weighted_rrp_change_pct)}`}
        valueClass={cn(volChange != null && volChange >= 0 ? 'text-green-700' : 'text-red-600')}
      />
      <Stat
        icon={<AlertTriangle size={14} className="text-red-500" />}
        label="Violations"
        value={String(data.total_violations)}
        sub="future violations"
        valueClass={data.total_violations > 0 ? 'text-red-700' : 'text-green-700'}
      />
      {data.rotten_apples > 0 && (
        <Stat
          label="🔴 Rotten Apples"
          value={String(data.rotten_apples)}
          sub="negative margin"
          valueClass="text-red-700 font-bold"
        />
      )}
      <Stat
        label="MIN Violations"
        value={String(data.min_violations)}
        sub="below corridor"
        valueClass={data.min_violations > 0 ? 'text-amber-700' : 'text-gray-500'}
      />
    </div>
  );
}

function Stat({ icon, label, value, sub, valueClass }: {
  icon?: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
  valueClass?: string;
}) {
  return (
    <div className="flex items-center gap-2">
      {icon}
      <div>
        <div className="text-xs text-gray-400">{label}</div>
        <div className={cn('font-semibold text-gray-900', valueClass)}>{value}</div>
        {sub && <div className="text-xs text-gray-400">{sub}</div>}
      </div>
    </div>
  );
}
