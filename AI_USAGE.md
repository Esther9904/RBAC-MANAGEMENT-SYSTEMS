# AI Usage

## 1. Which AI tools I used, and for what

I used **Claude (Anthropic)** as a pair-programming assistant throughout.

| Area | How AI was used | What I did myself |
|---|---|---|
| Architecture | Proposed the layered structure (domain / validation / services / API) and discussed trade-offs with me. | Chose Python/Flask over the Node option, and decided which limitations to accept. |
| Backend code and tests | Drafted each module and its tests, with a line-by-line explanation. | Typed each file myself, read the explanation, and ran `pytest` after every step. |
| Documentation | Drafted `project_plan.md` and this file. | Reviewed and edited them so they match what actually happened. |

How I verified AI output: every step ended with `pytest` on my own machine (Python 3.10), I exercised the
running server with `curl`, and I committed in small steps so each change can be reviewed on its own.

## 2. One example of AI code that was unsafe, and how it was caught

**The bug.** The first version of the "assign roles to a user" endpoint let *anyone holding `roles:manage`*
promote themselves to **Admin**. The code only checked "does the caller have `roles:manage`?" and never
asked "may the caller grant *this particular role*?"

**Why the tests missed it.** My escalation test used a Viewer, who has no `roles:manage`, so they were
(correctly) blocked. No test covered a user who *has* `roles:manage` but is not an Admin. All 62 tests passed
while the hole existed. Passing tests only prove the cases someone thought to write.

**How it was caught.** Before starting the frontend we did a deliberate security review. Instead of reading
the code, we wrote a short attack script: an Admin gives Bob (an Editor) a custom role containing
`roles:manage`, then Bob calls the API to make himself Admin. It returned `200 OK` and Bob became Admin.

**The fix.**
- `assign_roles` now takes the acting user and refuses with `403 ADMIN_ROLE_RESTRICTED` unless the actor
  is an Admin whenever a change would grant or remove the Admin role. The denial is written to the audit log.
- The attack script became a permanent regression test over real HTTP, plus unit tests for both sides
  of the rule (non-admins blocked, ordinary role changes and Admin actions still work).

**What I learned.** Test the actor with *partial* privileges, not only the one with none. A second probe
also showed a non-admin role manager can still widen their own role's permissions. I chose to document that
as a known limitation in `project_plan.md` rather than rush a larger fix, and listed the proper
solution under future work.