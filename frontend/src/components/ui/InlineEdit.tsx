import { useState, useRef, useEffect } from 'react';
import { Check, X, Pencil } from 'lucide-react';
import { cn } from '../../lib/utils';

interface InlineEditProps {
  value: number | null;
  onSave: (val: number | null) => Promise<void>;
  label?: string;
  unit?: string;
  decimals?: number;
  className?: string;
  readOnly?: boolean;
  highlight?: boolean;
}

export function InlineEdit({ value, onSave, label, unit = '€', decimals = 2, className, readOnly, highlight }: InlineEditProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState('');
  const [saving, setSaving] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editing]);

  const displayVal = value != null
    ? value.toLocaleString('de-DE', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
    : '—';

  const startEdit = () => {
    if (readOnly) return;
    setDraft(value != null ? String(value) : '');
    setEditing(true);
  };

  const cancel = () => setEditing(false);

  const save = async () => {
    const parsed = draft.trim() === '' ? null : parseFloat(draft.replace(',', '.'));
    if (draft.trim() !== '' && isNaN(parsed!)) return;
    setSaving(true);
    try {
      await onSave(parsed);
      setEditing(false);
    } finally {
      setSaving(false);
    }
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') save();
    if (e.key === 'Escape') cancel();
  };

  if (editing) {
    return (
      <div className={cn('flex items-center gap-1', className)}>
        {label && <span className="text-xs text-gray-500 shrink-0">{label}</span>}
        <div className="flex items-center gap-1 bg-white border-2 border-blue-400 rounded-md px-2 py-0.5">
          <input
            ref={inputRef}
            type="number"
            step="0.01"
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onKeyDown={onKey}
            className="w-24 text-sm outline-none bg-transparent"
          />
          {unit && <span className="text-xs text-gray-400">{unit}</span>}
        </div>
        <button onClick={save} disabled={saving} className="text-green-600 hover:text-green-700">
          <Check size={14} />
        </button>
        <button onClick={cancel} className="text-gray-400 hover:text-gray-600">
          <X size={14} />
        </button>
      </div>
    );
  }

  return (
    <div className={cn('flex items-center gap-1 group', className)}>
      {label && <span className="text-xs text-gray-500 shrink-0">{label}</span>}
      <button
        onClick={startEdit}
        disabled={readOnly}
        className={cn(
          'flex items-center gap-1 px-2 py-0.5 rounded-md text-sm font-medium transition-colors',
          readOnly ? 'cursor-default' : 'hover:bg-gray-100 cursor-pointer',
          highlight ? 'text-blue-700 font-semibold' : 'text-gray-900',
        )}
        title={readOnly ? undefined : 'Click to edit'}
      >
        {unit && <span className="text-xs text-gray-400">{unit}</span>}
        <span>{displayVal}</span>
        {!readOnly && (
          <Pencil size={11} className="text-gray-300 group-hover:text-gray-500 transition-colors ml-0.5" />
        )}
      </button>
    </div>
  );
}


interface TextEditProps {
  value: string | null;
  onSave: (val: string | null) => Promise<void>;
  placeholder?: string;
  className?: string;
  multiline?: boolean;
}

export function TextEdit({ value, onSave, placeholder = 'Add comment...', className, multiline }: TextEditProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState('');
  const [saving, setSaving] = useState(false);

  const startEdit = () => {
    setDraft(value || '');
    setEditing(true);
  };

  const save = async () => {
    setSaving(true);
    try {
      await onSave(draft.trim() || null);
      setEditing(false);
    } finally {
      setSaving(false);
    }
  };

  if (editing) {
    return (
      <div className={cn('space-y-1', className)}>
        {multiline ? (
          <textarea
            autoFocus
            rows={3}
            value={draft}
            onChange={e => setDraft(e.target.value)}
            className="w-full border-2 border-blue-400 rounded-md p-2 text-sm outline-none resize-none"
          />
        ) : (
          <input
            autoFocus
            type="text"
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') save(); if (e.key === 'Escape') setEditing(false); }}
            className="w-full border-2 border-blue-400 rounded-md px-2 py-1 text-sm outline-none"
          />
        )}
        <div className="flex gap-2">
          <button onClick={save} disabled={saving} className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
            Save
          </button>
          <button onClick={() => setEditing(false)} className="text-xs text-gray-500 hover:text-gray-700">
            Cancel
          </button>
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={startEdit}
      className={cn(
        'text-left text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded px-1 py-0.5 w-full transition-colors',
        !value && 'italic text-gray-400',
        className,
      )}
      title="Click to edit"
    >
      {value || placeholder}
    </button>
  );
}
