const BASE_URL = '/api';

// Every failed request becomes one of these, so components handle a single error shape.
export class ApiError extends Error {
  constructor(status, code, message, details) {
    super(message);
    this.name = 'ApiError';
    this.status = status; // HTTP status, or 0 when the server could not be reached
    this.code = code;
    this.details = details; // optional per-field errors, used by forms
  }
}

async function request(path, { method = 'GET', body, actorId } = {}) {
  const headers = {};
  if (actorId) headers['X-User-Id'] = actorId; // tells the server who is acting
  if (body !== undefined) headers['Content-Type'] = 'application/json';

  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, 'NETWORK_ERROR', 'Cannot reach the server. Is the backend running?');
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    // Empty or non-JSON body: leave data as null.
  }

  if (!response.ok) {
    const error = data?.error;
    throw new ApiError(
      response.status,
      error?.code ?? 'UNKNOWN_ERROR',
      error?.message ?? 'Request failed.',
      error?.details,
    );
  }
  return data;
}

export const api = {
  getMeta: () => request('/meta'),
  getDemoUsers: () => request('/demo/users'),
  getMe: (actorId) => request('/me', { actorId }),
  performAction: (actorId, actionKey) =>
    request(`/actions/${encodeURIComponent(actionKey)}`, { method: 'POST', actorId }),
  getAuditLog: (actorId) => request('/audit-log', { actorId }),
  getUsers: (actorId) => request('/users', { actorId }),
  getRoles: (actorId) => request('/roles', { actorId }),
  createRole: (actorId, body) => request('/roles', { method: 'POST', body, actorId }),
  updateRole: (actorId, roleId, body) =>
    request(`/roles/${encodeURIComponent(roleId)}`, { method: 'PUT', body, actorId }),
  assignRoles: (actorId, userId, roleIds) =>
    request(`/users/${encodeURIComponent(userId)}/roles`, {
      method: 'PUT',
      body: { role_ids: roleIds },
      actorId,
    }),
};