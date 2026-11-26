import { api } from '../api/client.js';
import { useActor } from '../context/ActorContext.jsx';
import { useFetch } from '../hooks/useFetch.js';
import RequirePermission from './RequirePermission.jsx';

export default function AuditLog({ refreshKey }) {
  return (
    <RequirePermission permission="audit:read">
      <AuditTable refreshKey={refreshKey} />
    </RequirePermission>
  );
}

// Only mounted when the user may read the log, so it never triggers a pointless denial.

function AuditTable({ refreshKey }) {
  const { actorId } = useActor();
  const { data, error, loading, reload } = useFetch(() => api.getAuditLog(actorId), [actorId, refreshKey]);

  return (
    <div>
      <div className="card-toolbar">
        <button type="button" className="button-secondary" onClick={reload}>
          Refresh
        </button>
      </div>

      {loading && <p className="muted">Loading audit log…</p>}
      {error && (
        <p className="notice notice-denied" role="alert">
          <strong>{error.status}</strong> {error.message}
        </p>
      )}
      {data && data.length === 0 && <p className="muted">No attempts recorded yet. Try an action above.</p>}
      {data && data.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>User</th>
                <th>Action</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry, index) => (
                <tr key={`${entry.timestamp}-${index}`}>
                  <td>{new Date(entry.timestamp).toLocaleString()}</td>
                  <td>{entry.user_name}</td>
                  <td>{entry.action}</td>
                  <td>
                    <span className={`badge ${entry.outcome === 'Allowed' ? 'badge-allowed' : 'badge-denied'}`}>
                      {entry.outcome}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}