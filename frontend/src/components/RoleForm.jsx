import { useId, useState } from 'react';
import { ApiError } from '../api/client.js';

// One form for both creating and editing a role.
export default function RoleForm({ permissionCatalogue, initial, submitLabel, onSubmit, onCancel }) {
  const uid = useId(); // unique per form, so two forms on one page never share ids
  const nameId = `${uid}-name`;
  const nameErrorId = `${uid}-name-error`;
  const [name, setName] = useState(initial.name);
  const [selected, setSelected] = useState(initial.permissions);
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState('');
  const [saving, setSaving] = useState(false);

  function togglePermission(permission) {
    setSelected((current) =>
      current.includes(permission) ? current.filter((item) => item !== permission) : [...current, permission],
    );
  }

  async function handleSubmit(event) {
    event.preventDefault(); // stop the browser reloading the page
    setFormError('');

    // Quick client-side checks for instant feedback. The server repeats and extends them.
    const errors = {};
    if (!name.trim()) errors.name = 'Role name is required.';
    if (selected.length === 0) errors.permissions = 'Select at least one permission.';
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) return;

    setSaving(true);
    try {
      await onSubmit({ name, permissions: permissionCatalogue.filter((item) => selected.includes(item)) });
    } catch (error) {
      if (error instanceof ApiError && error.details) {
        // Server field errors look like [{ field, message }]; turn them into { field: message }.
        setFieldErrors(Object.fromEntries(error.details.map((detail) => [detail.field, detail.message])));
      } else {
        setFormError(error.message); // e.g. the 403 "Forbidden: requires roles:manage"
      }
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit} noValidate>
      <div className="field">
        <label htmlFor={nameId}>Role name</label>
        <input
          id={nameId}
          type="text"
          value={name}
          maxLength={30}
          onChange={(event) => setName(event.target.value)}
          aria-invalid={Boolean(fieldErrors.name)}
          aria-describedby={fieldErrors.name ? nameErrorId : undefined}
        />
        {fieldErrors.name && (
          <p id={nameErrorId} className="field-error">
            {fieldErrors.name}
          </p>
        )}
      </div>

      <fieldset className="field">
        <legend>Permissions</legend>
        <div className="perm-grid">
          {permissionCatalogue.map((permission) => (
            <label key={permission} className="check">
              <input
                type="checkbox"
                checked={selected.includes(permission)}
                onChange={() => togglePermission(permission)}
              />
              <code>{permission}</code>
            </label>
          ))}
        </div>
        {fieldErrors.permissions && <p className="field-error">{fieldErrors.permissions}</p>}
      </fieldset>

      {formError && (
        <p className="notice notice-denied" role="alert">
          {formError}
        </p>
      )}

      <div className="form-actions">
        <button type="submit" className="button-primary" disabled={saving}>
          {saving ? 'Saving…' : submitLabel}
        </button>
        {onCancel && (
          <button type="button" className="button-secondary" onClick={onCancel} disabled={saving}>
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}