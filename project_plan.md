# Project Plan: RBAC Management System

## 1. Approach and tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.10 + Flask | Small and readable, and the language I'm strongest in. |
| Tests | pytest | Plain `assert`s, fixtures and parametrisation keep tests short. |
| Storage | In-memory Python structures | Allowed by the brief, needs no setup, and every test gets a fresh store. |
| Frontend | React + Vite | Required by the brief. Vite gives a fast dev server and a dev proxy. |

### Architecture

Permissions are enforced on the server. The UI only reflects what the server allows.

```
React UI  --HTTP + X-User-Id header-->  Flask routes (app/api)
                                           |  @require_permission(...)
                                           v
                                     Services (app/services)
                                     access, roles, users, audit log
                                           |
                                 Validation (app/validation)
                                           |
                                 In-memory store (app/domain)
```

Separation of concerns:

- `app/domain`: permission catalogue and seeded data. No logic.
- `app/validation`: input checking and cleaning. No HTTP and no storage.
- `app/services`: the RBAC rules (authorize, assign roles, last-Admin protection, audit log).
- `app/api`: a thin Flask layer. Routes authorize, call a service and return JSON.
- All expected failures raise one `AppError` and become one JSON error shape in a single place.
- Frontend: `src/api/client.js` is the only file that talks to the server. Pages and forms are in `src/components`.

### Key design decisions

- **One enforcement point.** Every protected route goes through `AccessService.authorize()`, via the
  `@require_permission` decorator. Authorization runs before validation, so an unauthorised caller
  learns nothing about the input rules.
- **Effective permissions are the union of the user's roles' permissions**, read live on every
  request, so editing a role takes effect immediately.
- **Every denial is audited.** Allowed list and read calls are not logged, to keep the log meaningful.
- **Safe errors.** Unexpected exceptions return a generic 500. Details go to the server log only.
- **The UI never hides buttons by permission.** The simulator shows every action so the server's
  refusal is visible. A `/api/me` endpoint lets pages avoid *requesting* data the user is not allowed
  to read, which stops the audit log filling with automatic denials. This is a courtesy, not security.
- **A Vite dev proxy instead of CORS.** `/api` is forwarded to Flask, so the backend needs no extra
  dependency and no cross-origin configuration.
- **Acceptance tests labelled with the brief's wording** live in one file, so the three required
  scenarios are easy to find (`backend/tests/test_brief_scenarios.py`).



## 2. Task Breakdown

Demo users are seeded, and the **Acting as** dropdown (top right) switches between them. There are
no passwords: this is a simulator.

| User | Role | Can do |
|---|---|---|
| Alice Admin | Admin | Everything |
| Bob Editor | Editor | `users:read`, `users:write`, `reports:export` |
| Carol Viewer | Viewer | `users:read` |
| Dave Auditor | Auditor | `users:read`, `audit:read`, `reports:export` |

1. **Test Access tab, as Carol:** click **Delete User**. The server answers `403 Forbidden` and the
   denial appears in the audit log. (Carol cannot see the log herself, so switch to Dave or Alice.)
2. **As Bob:** click **Export Report**. It is allowed and logged.
3. **Roles tab, as Alice:** create a role. Try an empty form, a duplicate name such as `editor`, and
   a valid one. Edit it. The built-in Admin role is locked.
4. **Users tab, as Alice:** change a user's roles. Try removing Admin from Alice (she is the only
   Admin, so it is refused).
5. **As Carol, Roles tab:** try to create a role. The server refuses, because the button being
   visible does not mean it is allowed.





## 3. Trade-offs and known limitations

- **In-memory storage.** All data resets when the server restarts.
- **Identity is a plain `X-User-Id` header.** Anyone can claim to be any user. This is acceptable only
  because the app is a simulator. A real system would use signed sessions or JWTs.
- **Two endpoints are public on purpose** (`/api/meta`, `/api/demo/users`) to power the permission
  checkboxes and the Switch User dropdown. They expose only ids and names.
- **The built-in Admin role is locked**, so the system cannot lose its only way back in.
- **Only an Admin can grant or remove the Admin role.** Found during security review: without this,
  any user with `roles:manage` could promote themselves (see `AI_USAGE.md`).
- **Known limitation: `roles:manage` is admin-equivalent.** A non-admin holding it can still edit
  their own role to add more permissions. It should only be given to trusted users.
- **The audit log records authorization decisions, not business outcomes.** A change that is allowed
  and then refused by a business rule (for example, removing the last Admin) appears as `Allowed`;
  the refusal is shown in the UI. Denials by the Admin-only rule appear as a second, `Denied` row.
- **The audit log is capped at 500 entries** and lives in memory.
- **No frontend automated tests.** The UI was verified by hand and in a real browser. The brief's
  required unit tests are on the backend.
- **No linter or formatter is configured.** A few lines are long (mostly seed data).
- Development servers only: no production build, HTTPS, rate limiting or pagination.

