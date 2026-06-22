import { useState, useRef, useCallback } from 'react';
import { Portal } from './Portal';
import { cn } from '../../lib/utils';

interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export function Tooltip({ content, children, className }: TooltipProps) {
  const [show, setShow] = useState(false);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const ref = useRef<HTMLDivElement>(null);

  const handleMouseEnter = useCallback(() => {
    if (ref.current) {
      const rect = ref.current.getBoundingClientRect();
      setPos({ x: rect.left + rect.width / 2, y: rect.top });
    }
    setShow(true);
  }, []);

  return (
    <div
      ref={ref}
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={() => setShow(false)}
    >
      {children}
      {show && content && (
        <Portal>
          <div
            className={cn(
              'fixed pointer-events-none z-[9999]',
              'bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-xl',
              'whitespace-nowrap max-w-xs fade-in',
              className,
            )}
            style={{
              left: pos.x,
              top: pos.y - 8,
              transform: 'translateX(-50%) translateY(-100%)',
            }}
          >
            {content}
            <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
          </div>
        </Portal>
      )}
    </div>
  );
}
