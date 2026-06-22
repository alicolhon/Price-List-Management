import { useState, useRef } from 'react';
import { Upload, RefreshCw, CheckCircle, XCircle } from 'lucide-react';
import { api } from '../api/client';
import { useQueryClient } from '@tanstack/react-query';

export function ImportPanel() {
  const [status, setStatus] = useState<'idle' | 'uploading' | 'done' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);
  const qc = useQueryClient();

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setStatus('uploading');
    setMessage('Uploading and converting...');
    try {
      const result = await api.uploadFile(file, true);
      setMessage(JSON.stringify(result));
      setStatus('done');
      qc.invalidateQueries();
    } catch (err) {
      setStatus('error');
      setMessage(String(err));
    }
  };

  const runImport = async () => {
    setStatus('uploading');
    setMessage('Running import from ./data/price_list.xlsb...');
    try {
      const result = await api.triggerImport(true);
      setMessage(JSON.stringify(result));
      setStatus('done');
      qc.invalidateQueries();
    } catch (err) {
      setStatus('error');
      setMessage(String(err));
    }
  };

  return (
    <div className="flex items-center gap-3 text-sm">
      <input ref={fileRef} type="file" accept=".xlsb,.xlsx,.ods" className="hidden" onChange={handleFile} />

      <button
        onClick={() => fileRef.current?.click()}
        disabled={status === 'uploading'}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        <Upload size={13} />
        Upload Excel
      </button>

      <button
        onClick={runImport}
        disabled={status === 'uploading'}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
      >
        <RefreshCw size={13} className={status === 'uploading' ? 'animate-spin' : ''} />
        Re-import
      </button>

      {message && (
        <div className="flex items-center gap-1 text-xs text-gray-600">
          {status === 'done' && <CheckCircle size={13} className="text-green-500" />}
          {status === 'error' && <XCircle size={13} className="text-red-500" />}
          <span className="max-w-xs truncate">{message}</span>
        </div>
      )}
    </div>
  );
}
