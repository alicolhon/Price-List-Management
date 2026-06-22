import { Modal } from '../ui/Modal';
import { TextEdit } from '../ui/InlineEdit';
import { COMMENT_FIELDS } from '../../lib/utils';
import type { Product } from '../../api/types';

interface Props {
  product: Product;
  open: boolean;
  onClose: () => void;
  onSave: (field: string, value: string | null) => Promise<void>;
}

export function CommentHistoryModal({ product, open, onClose, onSave }: Props) {
  return (
    <Modal open={open} onClose={onClose} title={`Comment History — ${product.material_10}`} size="lg">
      <div className="space-y-3">
        {COMMENT_FIELDS.map(({ key, label }) => {
          const value = (product as unknown as Record<string, unknown>)[key] as string | null;
          const isCurrent = key === 'comment_04_2026';
          return (
            <div key={key} className={`rounded-lg p-3 ${isCurrent ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50'}`}>
              <div className="flex items-center justify-between mb-1">
                <span className={`text-xs font-semibold ${isCurrent ? 'text-blue-700' : 'text-gray-500'}`}>
                  {label} {isCurrent && '✏️'}
                </span>
              </div>
              {isCurrent ? (
                <TextEdit
                  value={value}
                  onSave={v => onSave(key, v)}
                  placeholder="Add comment for this price round..."
                  multiline
                />
              ) : (
                <p className="text-sm text-gray-700 whitespace-pre-wrap min-h-[1.5rem]">
                  {value || <span className="italic text-gray-400">No comment</span>}
                </p>
              )}
            </div>
          );
        })}

        {product.hinweise_sms41 && (
          <div className="rounded-lg p-3 bg-yellow-50 border border-yellow-200">
            <div className="text-xs font-semibold text-yellow-700 mb-1">SMS41-EU Notes</div>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{product.hinweise_sms41}</p>
          </div>
        )}
      </div>
    </Modal>
  );
}
