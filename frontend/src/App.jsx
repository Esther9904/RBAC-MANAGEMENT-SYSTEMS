import { useCallback, useState } from 'react';
import AuditLog from './components/AuditLog.jsx';
import RolesPage from './components/RolesPage.jsx';
import TestAccess from './components/TestAccess.jsx';
import UserSwitcher from './components/UserSwitcher.jsx';
import UsersPage from './components/UsersPage.jsx';
import { useActor } from './context/ActorContext.jsx';

const TABS = [
  { id: 'roles', label: 'Roles' },
  { id: 'users', label: 'Users' },
  { id: 'access', label: 'Test Access' },
];

export default function App() {
  const { actorId, error } = useActor();
  const [tab, setTab] = useState(TABS[0].id);
  const [auditVersion, setAuditVersion] = useState(0);
  const refreshAudit = useCallback(() => setAuditVersion((version) => version + 1), []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>RBAC Management</h1>
        <UserSwitcher />
      </header>

      <nav className="tabs" aria-label="Sections">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            className={item.id === tab ? 'tab tab-active' : 'tab'}
            aria-current={item.id === tab ? 'page' : undefined}
            onClick={() => setTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <main>
        {error && <p className="notice notice-denied" role="alert">{error}</p>}
        {!error && !actorId && <p className="muted">Loading…</p>}

        {actorId && tab === 'roles' && <RolesPage key={actorId} />}
        {actorId && tab === 'users' && <UsersPage key={actorId} />}

        {actorId && tab === 'access' && (
          <>
            <section className="card">
              <h2>Attempt a protected action</h2>
              <p className="muted">
                The server decides. Buttons are never hidden, so you can see exactly what each user is denied.
              </p>
              <TestAccess key={actorId} onAttempt={refreshAudit} />
            </section>
            <section className="card">
              <h2>Access audit log</h2>
              <AuditLog refreshKey={auditVersion} />
            </section>
          </>
        )}
      </main>
    </div>
  );
}