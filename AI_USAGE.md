# AI Usage

## 1. Which AI tools I used, and for what

I used **Claude (Anthropic)** as a pair-programming assistant throughout.

| Area | How AI was used | What I did myself |
|---|---|---|
| Architecture | Proposed the layered structure (domain, validation, services, API) and discussed trade-offs. | Chose Python and Flask over the Node option, and decided which limitations to accept or fix. |
| Backend code and tests | Drafted each module and its tests, with a line-by-line explanation. | Typed each file myself, read the explanation, and ran `pytest` after every step. |
| Frontend | Drafted the React components and explained each one. | Ran the app, clicked through every flow and reported what I saw. |


The AI first drafted a Node prototype in its own scratch workspace. I preferred Python, so it was
discarded and none of it is in this repository.

### How I verified AI output

- Every step ended with `pytest` on my own machine (Python 3.10) before I committed.
- I exercised the running server with `curl` and the UI by hand, switching between users.
- The AI ran the frontend in a real headless browser against the real backend and reported the results.
- The AI also ran mutation spot-checks: it deliberately broke the code six ways (for example,
  "authorization always allows") and confirmed the matching scenario test failed each time.
- I committed in small steps so each change can be reviewed on its own.

## 2. One example of AI code that was unsafe, and how it was caught

**The bug.** The first version of the "assign roles to a user" endpoint let *anyone holding
`roles:manage`* promote themselves to **Admin**. The code only checked "does the caller have
`roles:manage`?" and never asked "may the caller grant *this particular role*?"


**How it was caught.** Before starting the frontend we did a deliberate security review. Instead of
reading the code, we wrote a short attack script: an Admin gives Bob (an Editor) a custom role
containing `roles:manage`, then Bob calls the API to make himself Admin. It returned `200 OK` and Bob
became Admin.

**The fix.**
- `assign_roles` now takes the acting user and refuses with `403 ADMIN_ROLE_RESTRICTED` unless the
  actor is an Admin, whenever a change would grant or remove the Admin role. The denial is written to
  the audit log.
- The attack script became a permanent regression test over real HTTP, plus unit tests for both sides
  of the rule (non-admins blocked, ordinary role changes and Admin actions still work).
- The suite went from 62 to 70 tests.

**What I learned.** Test the actor with *partial* privileges, not only the one with none. A second probe
also showed a non-admin role manager can still widen their own role's permissions. I chose to document
that as a known limitation in `project_plan.md` rather than rush a larger fix, and listed the proper
solution under future work.



