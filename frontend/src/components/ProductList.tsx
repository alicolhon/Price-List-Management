import { useEffect, useRef, useCallback } from 'react';
import { useInfiniteQuery } from '@tanstack/react-query';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Loader2, PackageSearch } from 'lucide-react';

import { api } from '../api/client';
import type { Filters, Product } from '../api/types';
import { ProductCard } from './ProductCard';

interface Props {
  filters: Filters;
}

const PAGE_SIZE = 30;

export function ProductList({ filters }: Props) {
  const parentRef = useRef<HTMLDivElement>(null);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
  } = useInfiniteQuery({
    queryKey: ['products', filters],
    queryFn: ({ pageParam = 1 }) => api.listProducts(filters, pageParam as number, PAGE_SIZE),
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce((acc, p) => acc + p.items.length, 0);
      return loaded < lastPage.total ? allPages.length + 1 : undefined;
    },
    initialPageParam: 1,
    staleTime: 30_000,
  });

  const allItems: Product[] = data?.pages.flatMap(p => p.items) ?? [];
  const totalCount = data?.pages[0]?.total ?? 0;

  const virtualizer = useVirtualizer({
    count: allItems.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 220,
    overscan: 5,
  });

  // Infinite scroll: load next page when reaching ~80% of list
  const onScroll = useCallback(() => {
    const el = parentRef.current;
    if (!el || isFetchingNextPage || !hasNextPage) return;
    if (el.scrollTop + el.clientHeight >= el.scrollHeight * 0.8) {
      fetchNextPage();
    }
  }, [fetchNextPage, isFetchingNextPage, hasNextPage]);

  useEffect(() => {
    const el = parentRef.current;
    if (!el) return;
    el.addEventListener('scroll', onScroll);
    return () => el.removeEventListener('scroll', onScroll);
  }, [onScroll]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3 text-gray-400">
        <Loader2 size={32} className="animate-spin" />
        <span className="text-sm">Loading products...</span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-2 text-red-500">
        <span className="font-medium">Failed to load products</span>
        <span className="text-xs text-gray-500">Is the backend running on http://localhost:8000?</span>
      </div>
    );
  }

  if (allItems.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3 text-gray-400">
        <PackageSearch size={40} className="text-gray-300" />
        <span className="text-sm">No products found for these filters</span>
      </div>
    );
  }

  const virtualItems = virtualizer.getVirtualItems();

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <div className="px-4 py-2 text-xs text-gray-500 bg-gray-50 border-b border-gray-200">
        Showing {allItems.length} of {totalCount.toLocaleString()} products
      </div>

      <div
        ref={parentRef}
        className="flex-1 overflow-y-auto px-4 py-3"
      >
        <div
          style={{ height: virtualizer.getTotalSize(), position: 'relative' }}
        >
          {virtualItems.map(vItem => {
            const product = allItems[vItem.index];
            return (
              <div
                key={product.id}
                data-index={vItem.index}
                ref={virtualizer.measureElement}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  transform: `translateY(${vItem.start}px)`,
                  paddingBottom: '12px',
                }}
              >
                <ProductCard product={product} />
              </div>
            );
          })}
        </div>

        {isFetchingNextPage && (
          <div className="flex justify-center py-4">
            <Loader2 size={20} className="animate-spin text-gray-400" />
          </div>
        )}
      </div>
    </div>
  );
}
