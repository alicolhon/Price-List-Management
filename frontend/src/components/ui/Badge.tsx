import { cn } from '../../lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'red' | 'amber' | 'blue' | 'green' | 'purple' | 'gray';
}

const variantMap = {
  default: 'bg-gray-100 text-gray-700',
  red: 'bg-red-100 text-red-700 border border-red-200',
  amber: 'bg-amber-100 text-amber-800 border border-amber-200',
  blue: 'bg-blue-100 text-blue-700 border border-blue-200',
  green: 'bg-green-100 text-green-700 border border-green-200',
  purple: 'bg-purple-100 text-purple-700 border border-purple-200',
  gray: 'bg-gray-100 text-gray-500',
};

export function Badge({ children, className, variant = 'default' }: BadgeProps) {
  return (
    <span className={cn('inline-flex items-center px-2 py-0.5 rounded text-xs font-medium', variantMap[variant], className)}>
      {children}
    </span>
  );
}
