# Project Plan: RBAC Management System

## 1. Approach and tech stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python 3.10 + Flask | Small, readable, and the language I'm strongest in. |
| Tests | pytest | Plain `assert`s, fixtures and parametrisation keep tests short. |
| Storage | In-memory Python structures | Allowed by the brief; zero setup; each test gets a fresh store. |
| Frontend | React + Vite | Required by the brief; Vite gives a fast dev server. |

### Architecture

Permissions are enforced on the server. The UI only reflects what the server allows.

    React UI  ──HTTP + X-User-Id header──▶  Flask routes (app/api)
                                               │  @require_permission(...)
                                               ▼
                                         Services (app/services)
                                         access · roles · users · audit
                                               │
                                     Validation (app/validation)
                                               │
                                         In-memory store (app/domain)

Separation of concerns:

- `app/domain`: permission catalogue and seeded data. No logic.
- `app/validation`: input checking and cleaning. No HTTP, no storage.
- `app/services`: the RBAC rules (authorize, assign roles, last-admin protection, audit log).
- `app/api`: thin Flask layer. Routes only authorize, call a service and return JSON.
- All failures raise one `AppError` type and are converted to one JSON error shape in a single place.

### Key design decisions

- **One enforcement point.** Every protected route goes through `AccessService.authorize()`, via the `@require_permission` decorator. Authorization runs *before* validation, so an unauthorised caller learns nothing about the input rules.
- **Effective permissions are the union of the user's roles' permissions**, read live on every request, so editing a role takes effect immediately.
- **Every denial is audited.** Allowed list/read calls are not logged, to keep the audit log meaningful.
- **Safe errors.** Unexpected exceptions return a generic 500; details go to the server log only.

## 2. Milestones and scoping (4-6 hour window)

| # | Milestone | Planned time | Status |
|---|---|---|---|
| 1 | Repo, tooling, domain layer | 30 min | Done |
| 2 | Role validation + tests | 30 min | Done |
| 3 | Access service, audit log + tests | 45 min | Done |
| 4 | Role and user services + tests | 45 min | Done |
| 5 | Flask API + HTTP tests | 45 min | Done |
| 6 | Security review pass and fix | 30 min | Done |
| 7 | React UI: Switch User, Roles, Users, Test Access, Audit Log | 90 min | TODO |
| 8 | README, final docs, manual end-to-end check | 30 min | TODO |

Scoping rule: enforcement correctness and tests come before UI polish, because the rubric weights
functionality, security and testing above visuals. Anything beyond the brief is listed under "Future work".

## 3. Assumptions

- A "user" is a seeded demo account; there is no registration or password login. The "Switch User" dropdown stands in for login, as the brief allows.
- A user can hold several roles; their permissions are combined.
- Assigning a user an empty role list is allowed and means "no access".
- Role names are 2-30 characters, start with a letter, and are unique case-insensitively.
- The brief asks to create, view and update roles, so roles cannot be deleted.

## 4. Trade-offs and known limitations

- **In-memory storage.** All data resets when the server restarts. Chosen for speed and simplicity.
- **Identity is a plain `X-User-Id` header.** Anyone can claim to be any user. This is acceptable only
  because the app is a simulator. A real system would use signed sessions or JWTs.
- **Two endpoints are public on purpose** (`/api/meta`, `/api/demo/users`) to power the permission
  checkboxes and the Switch User dropdown. They expose only ids and names.
- **The built-in Admin role is locked**, so nobody can remove their own way back into the system.
- **Only an Admin can grant or remove the Admin role.** Found during security review: without this,
  any user with `roles:manage` could promote themselves (see `AI_USAGE.md`).
- **Known limitation: `roles:manage` is admin-equivalent.** A non-admin holding it can still edit their
  own role to add more permissions. It should only be given to trusted users.
- **Audit log is capped at 500 entries** and lives in memory.
- No pagination, no rate limiting, no HTTPS or CORS hardening (single-machine demo).

## 5. Future work

- Rule: "you can only grant permissions you hold yourself". This would close the `roles:manage` limitation.
- Real authentication (hashed passwords, signed tokens) and a persistent database (SQLite).
- Role deletion with a safe reassignment flow.
- Pagination and filtering for the audit log.