import { useState } from 'react';
import { api } from '../api/client.js';
import { useActor } from '../context/ActorContext.jsx';
import { useFetch } from '../hooks/useFetch.js';
import RequirePermission from './RequirePermission.jsx';
import RoleForm from './RoleForm.jsx';

export default function RolesPage() {
  return (
    <RequirePermission permission="users:read">
      <RolesContent />
    </RequirePermission>
  );
}

function RolesContent() {
  const { actorId, refreshPermissions } = useActor();
  const meta = useFetch(() => api.getMeta(), []);
  const roles = useFetch(() => api.getRoles(actorId), [actorId]);
  const [editingId, setEditingId] = useState(null);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [status, setStatus] = useState(null); // { kind: 'created' | 'updated', roleId, text }

  async function createRole(payload) {
    setStatus(null);
    const role = await api.createRole(actorId, payload);
    setStatus({ kind: 'created', roleId: role.id, text: `Role "${role.name}" created.` });
    setCreateFormKey((key) => key + 1); // new key = brand-new empty form
    roles.reload();
    refreshPermissions();
  }

  async function updateRole(roleId, payload) {
    setStatus(null);
    const role = await api.updateRole(actorId, roleId, payload);
    setStatus({ kind: 'updated', roleId, text: `Role "${role.name}" updated.` });
    setEditingId(null);
    roles.reload();
    refreshPermissions();
  }

  function startEditing(roleId) {
    setStatus(null);
    setEditingId(roleId);
  }

  const failure = meta.error || roles.error;
  if (failure) {
    return (
      <p className="notice notice-denied" role="alert">
        <strong>{failure.status}</strong> {failure.message}
      </p>
    );
  }
  if (!meta.data || !roles.data) return <p className="muted">Loading roles…</p>;

  const catalogue = meta.data.permissions;

  return (
    <>
      <section className="card">
        <h2>Create a role</h2>
        <RoleForm
          key={createFormKey}
          permissionCatalogue={catalogue}
          initial={{ name: '', permissions: [] }}
          submitLabel="Create role"
          onSubmit={createRole}
        />
        {status?.kind === 'created' && (
          <p className="notice notice-allowed" role="status">
            {status.text}
          </p>
        )}
      </section>

      <section className="card">
        <h2>Roles</h2>
        <ul className="item-list">
          {roles.data.map((role) => (
            <li key={role.id} className="item">
              {editingId === role.id ? (
                <RoleForm
                  permissionCatalogue={catalogue}
                  initial={{ name: role.name, permissions: role.permissions }}
                  submitLabel="Save changes"
                  onSubmit={(payload) => updateRole(role.id, payload)}
                  onCancel={() => setEditingId(null)}
                />
              ) : (
                <>
                  <div className="item-head">
                    <strong>{role.name}</strong>
                    {role.is_system && <span className="badge badge-neutral">Built-in, locked</span>}
                    <button
                      type="button"
                      className="button-secondary item-action"
                      disabled={role.is_system}
                      onClick={() => startEditing(role.id)}
                    >
                      Edit
                    </button>
                  </div>
                  <div className="chips">
                    {role.permissions.map((permission) => (
                      <code key={permission} className="chip">
                        {permission}
                      </code>
                    ))}
                  </div>
                  {status?.kind === 'updated' && status.roleId === role.id && (
                    <p className="notice notice-allowed" role="status">
                      {status.text}
                    </p>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}