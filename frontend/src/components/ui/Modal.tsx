import { useEffect } from 'react';
import { X } from 'lucide-react';
import { Portal } from './Portal';
import { cn } from '../../lib/utils';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

const sizeMap = {
  sm: 'max-w-md',
  md: 'max-w-xl',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
};

export function Modal({ open, onClose, title, children, size = 'md' }: ModalProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <Portal>
      <div
        className="fixed inset-0 z-[9998] flex items-center justify-center p-4 bg-black/50 fade-in"
        onClick={e => { if (e.target === e.currentTarget) onClose(); }}
      >
        <div className={cn('bg-white rounded-xl shadow-2xl w-full flex flex-col max-h-[90vh]', sizeMap[size])}>
          <div className="flex items-center justify-between px-5 py-4 border-b shrink-0">
            <h3 className="font-semibold text-gray-900 text-sm">{title}</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
              <X size={18} />
            </button>
          </div>
          <div className="overflow-y-auto flex-1 p-5">{children}</div>
        </div>
      </div>
    </Portal>
  );
}
