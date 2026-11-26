import { useState } from 'react';
import { api } from '../api/client.js';
import { useActor } from '../context/ActorContext.jsx';
import { useFetch } from '../hooks/useFetch.js';
import RequirePermission from './RequirePermission.jsx';

export default function UsersPage() {
  return (
    <RequirePermission permission="users:read">
      <UsersContent />
    </RequirePermission>
  );
}

function UsersContent() {
  const { actorId, refreshPermissions } = useActor();
  const users = useFetch(() => api.getUsers(actorId), [actorId]);
  const roles = useFetch(() => api.getRoles(actorId), [actorId]);
  const [savedUserId, setSavedUserId] = useState(null); // whose roles were saved most recently

  async function saveRoles(userId, roleIds) {
    setSavedUserId(null); // a new attempt hides the previous success message
    await api.assignRoles(actorId, userId, roleIds);
    setSavedUserId(userId);
    users.reload();
    refreshPermissions(); // the acting user's own roles may just have changed
  }

  const failure = users.error || roles.error;
  if (failure) {
    return (
      <p className="notice notice-denied" role="alert">
        <strong>{failure.status}</strong> {failure.message}
      </p>
    );
  }
  if (!users.data || !roles.data) return <p className="muted">Loading users…</p>;

  return (
    <section className="card">
      <h2>Users and their roles</h2>
      <p className="muted">Tick the roles a user should have, then save. A user's permissions are the combination of all their roles.</p>
      <ul className="item-list">
        {users.data.map((user) => (
          // The key includes the saved roles, so after a save the row restarts from the server's data.
          <UserRow
            key={`${user.id}:${user.role_ids.join(',')}`}
            user={user}
            roles={roles.data}
            justSaved={savedUserId === user.id}
            onSave={saveRoles}
          />
        ))}
      </ul>
    </section>
  );
}

function UserRow({ user, roles, justSaved, onSave }) {
  const [selected, setSelected] = useState(user.role_ids);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [touched, setTouched] = useState(false); // true once the user edits again, hiding the success message

  const changed =
    selected.length !== user.role_ids.length || selected.some((roleId) => !user.role_ids.includes(roleId));

  // The built-in Admin role is the one flagged is_system. Warn before granting it.
  const adminRole = roles.find((role) => role.is_system);
  const grantingAdmin =
    adminRole && selected.includes(adminRole.id) && !user.role_ids.includes(adminRole.id);

  function toggle(roleId) {
    setError('');
    setTouched(true);
    setSelected((current) =>
      current.includes(roleId) ? current.filter((id) => id !== roleId) : [...current, roleId],
    );
  }

  async function handleSave() {
    setSaving(true);
    setError('');
    try {
      await onSave(user.id, selected);
    } catch (err) {
      setError(err.message); // e.g. "Cannot remove the Admin role from the last Admin."
    } finally {
      setSaving(false);
    }
  }

  return (
    <li className="item">
      <div className="item-head">
        <strong>{user.name}</strong>
        <button
          type="button"
          className="button-primary item-action"
          disabled={!changed || saving}
          onClick={handleSave}
        >
          {saving ? 'Saving…' : 'Save roles'}
        </button>
      </div>
      <fieldset className="role-checks">
        <legend className="sr-only">Roles for {user.name}</legend>
        {roles.map((role) => (
          <label key={role.id} className="check">
            <input type="checkbox" checked={selected.includes(role.id)} onChange={() => toggle(role.id)} />
            {role.name}
          </label>
        ))}
      </fieldset>
      {grantingAdmin && (
        <p className="notice notice-warning" role="note">
          Admin gives {user.name} every permission, including managing roles and users. Only grant it to people you
          fully trust.
        </p>
      )}
      {justSaved && !touched && (
        <p className="notice notice-allowed" role="status">
          Roles updated for {user.name}.
        </p>
      )}
      {error && (
        <p className="notice notice-denied" role="alert">
          {error}
        </p>
      )}
    </li>
  );
}