import type { Filters, Product, ProductListResponse, ProductUpdate, SummaryStats } from './types';

const BASE = 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  listProducts: (filters: Partial<Filters>, page = 1, pageSize = 50) => {
    const params = new URLSearchParams();
    params.set('page', String(page));
    params.set('page_size', String(pageSize));
    if (filters.search) params.set('search', filters.search);
    if (filters.pg1) params.set('pg1', filters.pg1);
    if (filters.pg2) params.set('pg2', filters.pg2);
    if (filters.status) params.set('status', filters.status);
    if (filters.abc_sales) params.set('abc_sales', filters.abc_sales);
    if (filters.violation) params.set('violation', filters.violation);
    if (filters.discount_group) params.set('discount_group', filters.discount_group);
    return request<ProductListResponse>(`/api/products?${params}`);
  },

  getProduct: (id: number) => request<Product>(`/api/products/${id}`),

  updateProduct: (id: number, data: ProductUpdate) =>
    request<Product>(`/api/products/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  simulate: (id: number, data: ProductUpdate) =>
    request(`/api/products/${id}/simulate`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getSummary: () => request<SummaryStats>('/api/products/summary'),

  getPg1: () => request<{ code: string; description: string }[]>('/api/reference/pg1'),
  getPg2: (pg1?: string) => {
    const q = pg1 ? `?pg1=${encodeURIComponent(pg1)}` : '';
    return request<{ code: string; description: string }[]>(`/api/reference/pg2${q}`);
  },
  getDiscountGroups: () => request<string[]>('/api/reference/discount-groups'),

  triggerImport: (force = false) =>
    request('/api/import/run', { method: 'POST', body: JSON.stringify({ force }) }),
  getImportStatus: () => request<{ status: string; message: string }>('/api/import/status'),

  uploadFile: (file: File, force = false) => {
    const form = new FormData();
    form.append('file', file);
    return fetch(`${BASE}/api/import/upload?force=${force}`, { method: 'POST', body: form })
      .then(r => r.json());
  },
};
