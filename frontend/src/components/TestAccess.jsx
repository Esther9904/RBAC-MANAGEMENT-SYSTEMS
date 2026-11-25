import { useState } from 'react';
import { api } from '../api/client.js';
import { useActor } from '../context/ActorContext.jsx';
import { useFetch } from '../hooks/useFetch.js';

export default function TestAccess({ onAttempt }) {
  const { actorId } = useActor();
  const meta = useFetch(() => api.getMeta(), []);
  const [result, setResult] = useState(null);
  const [busyKey, setBusyKey] = useState('');

  async function attempt(actionKey) {
    setBusyKey(actionKey);
    try {
      const data = await api.performAction(actorId, actionKey);
      setResult({ ok: true, status: 200, text: data.message });
    } catch (error) {
      setResult({ ok: false, status: error.status, text: error.message });
    } finally {
      setBusyKey('');
      onAttempt(); // tell the page to refresh the audit log
    }
  }

  if (meta.loading) return <p className="muted">Loading actions…</p>;
  if (meta.error) return <p className="notice notice-denied" role="alert">{meta.error.message}</p>;

  return (
    <div>
      <div className="action-grid">
        {Object.entries(meta.data.actions).map(([key, action]) => (
          <button
            key={key}
            type="button"
            className="action-button"
            disabled={busyKey !== ''}
            onClick={() => attempt(key)}
          >
            <span className="action-label">{action.label}</span>
            <span className="action-permission">needs {action.permission}</span>
          </button>
        ))}
      </div>

      {result && (
        <p
          className={`notice ${result.ok ? 'notice-allowed' : 'notice-denied'}`}
          role={result.ok ? 'status' : 'alert'}
        >
          <strong>{result.status}</strong> {result.text}
        </p>
      )}
    </div>
  );
}