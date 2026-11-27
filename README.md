# RBAC Management System

A small web app for managing **roles, permissions and user access**, with **live permission
enforcement**. Admins create and edit roles, assign roles to users, and then act as any user to
attempt protected actions. Every attempt is allowed or denied by the server and written to an
access audit log.

- **Frontend:** React (Vite)
- **Backend:** Python 3 + Flask
- **Storage:** in-memory (resets when the backend restarts)
- **Tests:** pytest (80 tests)

Related documents: [project_plan.md](project_plan.md) (approach, milestones, trade-offs) and
[AI_USAGE.md](AI_USAGE.md) (how AI was used and verified).

## Quick start

You need **Python 3.10+** and **Node 20+**. Use two terminals.

**1. Backend** (http://127.0.0.1:5000)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        
pip install -r requirements.txt
flask --app app run --port 5000
```

**2. Frontend** (http://localhost:5173)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server forwards `/api` calls to the backend, so no CORS
setup is needed. Start the backend first.

## Run the tests

```bash
cd backend
source .venv/bin/activate
pytest
```

Expected: `80 passed`. The tests for the brief's three required scenarios are described below.

## Tests mapped to the brief

Run everything with `pytest` (from `backend/`). The three scenarios the brief requires are in
[`tests/test_brief_scenarios.py`](backend/tests/test_brief_scenarios.py); run just those with
`pytest tests/test_brief_scenarios.py -v`.

| Brief scenario | Acceptance test (HTTP) | Deeper unit tests |
|---|---|---|
| 1. A user with the required permission succeeds | `test_scenario_1_user_with_the_required_permission_succeeds` | `test_access.py::test_user_with_permission_can_perform_action_and_it_is_logged_as_allowed` |
| 2. An unauthorized user is blocked (403) | `test_scenario_2_unauthorized_user_is_blocked_with_403_and_logged`, `test_scenario_2_restriction_is_enforced_by_the_server_not_just_the_ui` | `test_access.py::test_user_without_permission_is_blocked_with_403_and_logged_as_denied`, `test_api.py::test_viewer_calling_create_role_directly_gets_403`, `test_api.py::test_a_role_manager_who_is_not_admin_cannot_promote_themselves_to_admin` |
| 3. Invalid or malformed input is handled gracefully | `test_scenario_3_duplicate_role_name_is_handled_gracefully`, `test_scenario_3_invalid_permission_is_handled_gracefully`, `test_scenario_3_malformed_json_is_handled_gracefully` | `test_role_validation.py::test_duplicate_role_name_is_rejected_case_insensitively_with_409`, `test_role_validation.py::test_unknown_permission_is_rejected`, `test_role_service.py::test_duplicate_name_fails_with_409_and_stores_nothing` |
| Other edge cases named in the brief | | `test_user_service.py::test_the_last_admin_cannot_lose_the_admin_role`, `test_user_service.py::test_assigning_a_non_existent_role_is_rejected_and_leaves_the_user_unchanged` |

Each scenario test also asserts that a rejected request leaves no data behind.

## Try it (2-minute walkthrough)

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




