import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Settings } from 'lucide-react';

import { SummaryBar } from './components/SummaryBar';
import { FilterBar } from './components/FilterBar';
import { ProductList } from './components/ProductList';
import { ImportPanel } from './components/ImportPanel';
import type { Filters } from './api/types';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 20_000 },
  },
});

const DEFAULT_FILTERS: Filters = {
  search: '',
  pg1: '',
  pg2: '',
  status: '',
  abc_sales: '',
  violation: '',
  discount_group: '',
};

function PriceApp() {
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [showImport, setShowImport] = useState(false);

  const updateFilter = (partial: Partial<Filters>) =>
    setFilters(f => ({ ...f, ...partial }));

  const resetFilters = () => setFilters(DEFAULT_FILTERS);

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* ── Header ── */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-red-600 rounded-md flex items-center justify-center">
            <span className="text-white font-bold text-xs">B</span>
          </div>
          <div>
            <h1 className="font-bold text-gray-900 text-sm leading-none">Price List Management</h1>
            <p className="text-xs text-gray-400 mt-0.5">MA-SMS · DE21 · 04-2026</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {showImport && <ImportPanel />}
          <button
            onClick={() => setShowImport(s => !s)}
            className="p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Import settings"
          >
            <Settings size={16} />
          </button>
        </div>
      </header>

      {/* ── Summary Bar ── */}
      <SummaryBar />

      {/* ── Filters ── */}
      <FilterBar filters={filters} onChange={updateFilter} onReset={resetFilters} />

      {/* ── Product List ── */}
      <main className="flex-1 min-h-0 flex flex-col">
        <ProductList filters={filters} />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <PriceApp />
    </QueryClientProvider>
  );
}
