# Permission Matrix — ClassiX
**Companion document to:** `PRD-school-management-software.md` (Section 2.1 — Roles & Permissions) and `database-schema.md` (Section 8a — `role`/`role_permission`)
**Status:** Living document — the baseline `role_permission` seed data for every predefined system template. When admin clones a template into a custom role, this matrix is the starting point they tweak from.

**Default posture (decided in this doc): deny-by-default.** Any module/action combination not explicitly marked "Yes" below is denied. This is the safer, standard convention for a system exposing sensitive student/financial data across many custom-configurable roles — it means a newly cloned or misconfigured role can never accidentally over-expose data; the failure mode is "can't see something they should," which is a support ticket, not a privacy incident.

---

## Legend

- **V** = View · **C** = Create · **E** = Edit · **D** = Delete
- **—** = no access to this module at all
- **Own classes only** = access is further restricted to the staff member's assigned sections/subjects (Staff module data, not a permission row — see PRD Section 2.1)
- **Delete convention:** hard Delete is reserved for Admin by default across most modules — other roles manage removal via status changes (an Edit action, e.g. "mark inactive") rather than permanently deleting records with history value. Exceptions are modules where deleting a record has no downstream history implication (e.g. a Library catalog entry, a Transport route) — those templates may get Delete directly.

---

## Matrix: Module × Role Template

| Module | Admin | Teacher | Accountant | Librarian | Registrar / Front Desk | Transport Coordinator | Nurse / Health Officer |
|---|---|---|---|---|---|---|---|
| **Students** | V/C/E/D | V (own classes only) | V | V | V/C/E | V | V |
| **Attendance** | V/C/E/D | V/C/E (own classes only) | — | — | V | — | — |
| **Academics** | V/C/E/D | V/C/E (own classes only) | — | — | V | — | — |
| **Grades** | V/C/E/D | V/C/E (own classes only) | — | — | V | — | — |
| **Fees** | V/C/E/D | — | V/C/E/D | — | V | — | — |
| **Messages** | V/C/E/D | V/C (own classes only) | V/C | V/C | V/C | V/C | V/C |
| **Staff** | V/C/E/D | — | V *(payroll-relevant view)* | V | V | V | V |
| **Schedule** | V/C/E/D | V | V | V | V/C | V | V |
| **Library** | V/C/E/D | V | — | V/C/E/D | — | — | — |
| **Transport** | V/C/E/D | — | — | — | — | V/C/E/D | — |
| **Admissions** | V/C/E/D | — | — | — | V/C/E/D | — | — |
| **Documents** | V/C/E/D | — | — | — | V/C/E | — | — |
| **Cafeteria** | V/C/E/D | — | — *(gap, see note)* | — | — | — | — |
| **Health** | V/C/E/D | — | — | — | — | — | V/C/E/D |
| **Alumni** | V/C/E/D | — | — *(gap, see note)* | — | — | — | — |

---

## Per-role rationale

**Teacher** — needs to run their own classroom: mark attendance, post homework/grades, message parents of their students, see the school schedule. Deliberately excluded from Fees, Staff, Admissions, and other operational modules — a Teacher role that could see the whole school's fee ledger would be an over-grant. Student and academic-module access is data-scoped to their assigned sections/subjects, not the whole school roster.

**Accountant** — owns Fees end-to-end (including Delete, since correcting billing errors is routine). Needs View on Students (to attribute invoices) and Staff (payroll reference data). Can message for payment reminders. Does **not** get access to Grades, Attendance, Health, or Library — financial role, not an academic or welfare one.

**Librarian** — owns the Library catalog and lending end-to-end. Needs View on Students and Staff purely to look up borrowers. No financial, academic, or admissions access.

**Registrar / Front Desk** — the closest template to a "generalist admin support" role: manages Student records (short of hard delete — that stays Admin-only, since deleting a student record has real history implications), owns the Admissions pipeline end-to-end, and generates Documents (ID cards, certificates). Broader View access across Academics/Grades/Schedule reflects a front-desk role fielding parent questions, without edit rights into academic content itself.

**Transport Coordinator** — owns Transport end-to-end, needs View on Students to assign routes/stops, can message about route changes.

**Nurse / Health Officer** — owns Health end-to-end, View on Students, can message parents about a clinic visit.

---

## Known gaps (flagged, not silently assumed)

- **Cafeteria** and **Alumni** have no owning predefined template today — only Admin has access by default. If a school needs a non-Admin role to manage either (e.g., an Accountant handling meal billing, since Cafeteria shares the Fees billing engine — PRD Section 3), the admin would clone Accountant and manually add Cafeteria permissions via the clone-and-tweak flow. This is intentionally left as a customization case rather than a new predefined template, since usage is likely to vary a lot by school. Worth revisiting if this pattern turns out to be common enough to warrant its own template later.

---

## How clone-and-tweak interacts with this matrix

1. Admin selects a template (e.g., Accountant) to clone.
2. A new `role` row is created with `tenant_id` set (making it tenant-owned, not a shared system template), `is_editable = true`, and `role_permission` rows copied from the template's baseline above.
3. Admin toggles individual module/action cells for the new role — e.g., add Cafeteria View/Create to a cloned Accountant role to cover meal billing.
4. The Admin role itself can never be cloned into something with reduced access, and can never be the *target* of a permission edit — its access is enforced via the `is_admin_role` flag in code, not these permission rows (per `database-schema.md` Section 8a).

---

## Document History

- **v1:** Initial permission matrix for all seven predefined role templates (Admin, Teacher, Accountant, Librarian, Registrar/Front Desk, Transport Coordinator, Nurse/Health Officer) across all 15 modules. Deny-by-default posture decided and documented. Cafeteria/Alumni gap flagged as an open customization case rather than a new template.
