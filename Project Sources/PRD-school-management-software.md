# Product Requirements Document (PRD)
## ClassiX by Juspire — School Management Software

**Product name:** ClassiX (by Juspire) — *not yet trademark/domain verified, treat as provisional until confirmed.*
**Status:** Living document — source of truth for all product decisions.
**Instruction to AI assistants (including Claude):** If a future response drifts from what's documented here, contradicts an earlier decision, or seems to be guessing/hallucinating details, the user will say "refer to the PRD" — re-read this document in full before continuing, and correct course based on it, not on assumptions.

---

## 1. Product Vision

A web-based, subscription-priced school management platform. The single guiding principle for every design and technical decision:

> **Simple enough to understand in one glance. Powerful enough to run the whole school.**

Design philosophy (non-negotiable, applies to every screen and feature):
- **Minimal screens** — don't create a new page/screen when a modal, drawer, or inline edit will do.
- **Minimal clicks/actions** — the most common task on any screen should take 1-2 taps/clicks, not a multi-step wizard.
- **Modal-based workflows wherever possible** — actions like adding a student, marking attendance exceptions, recording a payment should happen in a modal over the current screen, not a full page navigation, so the user never loses context.
- **Smart defaults** — pre-fill today's date, current class, logged-in user's context, etc. Reduce data entry, don't add it.
- **Role-based views** — a teacher, parent, admin, and student should each see only what's relevant to them, styled consistently but scoped differently.
- **Progressive disclosure** — advanced options are tucked away (behind "More" or settings), not shown by default.
- **Consistent visual language** — same icon set, same interaction patterns (e.g., swipe/tap to mark attendance, same modal pattern everywhere) across all modules.
- **Aesthetic direction** — clean, elegant, modern. Apple-like: generous whitespace, clear typography hierarchy, no unnecessary chrome or decoration.
- **Inline "create new" within dependent dropdowns — never force a workflow restart.** Any form with a dropdown that depends on setup data the admin configures elsewhere (Class/Section, Role, Subject, Route, etc.) must offer a "+ Create new…" option at the bottom of that dropdown. Selecting it opens a small nested modal on top of the current one — the original form's already-entered data is preserved, not lost — for a minimal, single-purpose creation (e.g., just a class name). On save, the nested modal closes and the new value is auto-selected in the original form, which the admin then continues uninterrupted. The admin must never be forced to cancel an in-progress workflow, go create a missing dependency elsewhere, and restart from scratch.

**Any feature or screen that violates these principles should be flagged and reconsidered before being built.**

---

## 2. Target Users / Roles

| Role | Primary needs |
|---|---|
| **Admin** | Full control — manage students, staff, fees, settings, subscription |
| **Teacher** | Attendance, grades, homework, messaging — for their assigned classes only |
| **Parent** | View child's attendance, grades, fees, messages — read-mostly, mobile-first |
| **Student** | View timetable, homework, grades — read-mostly |

Three user-facing surfaces (not one bloated app):
1. **Admin/Teacher web dashboard** — data-dense but organized, desktop-first
2. **Parent view** — minimal, mobile-first (web now, native app possibly later)
3. **Student view** — minimal, mobile-first (web now, native app possibly later)

### 2.1 Platform vs Tenant Users

ClassiX operates with two distinct categories of users:

#### 2.1.1 Platform Users (Juspire)

Platform users are employees of Juspire who manage and operate the SaaS platform itself.

Examples include:

- Founder
- Support Engineer
- Billing Team
- DevOps
- Customer Success

Platform users are **not members of any tenant (school)**.

Their responsibilities include:

- Managing tenants
- Subscription and billing administration
- Platform monitoring
- Tenant provisioning
- Support operations

Platform users never automatically gain unrestricted access to tenant-owned data.

---

#### 2.1.2 Tenant Users (School)

Tenant users belong to exactly one school.

These include:

- Admin
- Staff
- Parent
- Student

Every tenant has at least one Admin.

Admin is the highest authority within that tenant and always has unrestricted visibility across every module within that school's data.

Tenant Admin authority never extends outside their own tenant.

### 2.2 Roles & Permissions (RBAC) — Hybrid Model

The simple four-role model above (Admin/Teacher/Parent/Student) is a **broad account category**, used to decide which portal UI a user lands in. Within the **staff category**, schools need finer-grained division of labor — e.g., an Accountant who only handles Fees/Payroll, a Librarian who only handles Library, without either being made a full Admin or blocked entirely.

**Decided model: hybrid — predefined templates + clone-and-customize.**

- **Admin** is always a full-access role across every module. This is hardcoded, not just a default permission set — it cannot be edited, restricted, or deleted by anyone, including another Admin. Admin visibility into everything is a permanent guarantee, not a configurable default.
The Admin role described here is a **tenant administrator**, not a platform administrator.

Platform administration is handled separately by Juspire employees and is intentionally outside the tenant RBAC system.
- **Predefined role templates** ship out of the box, each pre-mapped to sensible module + action permissions: **Accountant** (Fees, Payroll), **Librarian** (Library), **Registrar/Front Desk** (Students, Admissions), **Transport Coordinator** (Transport), **Nurse/Health Officer** (Health), **Teacher** (Academics, Attendance, Grades — scoped to their assigned classes only).
- **Admin can clone any template into a custom role** for their school and toggle permissions — granularity is **module + action** (view / create / edit / delete), not just "has access to module." E.g., clone Accountant, add view-only on Students, remove delete on Fees.
- **Teacher's class-scoping is separate from module permissions.** A Teacher's *module* access (Attendance, Grades, Academics) is granted the same way as any role, but *which students/classes* they see within that module is determined by their class/subject assignment (Staff module), not by the permission system. This distinction matters for implementation: don't try to model "my assigned classes" as a permission — it's a data-scope rule.
- **Parents and Students** are not part of the role/permission system — they get a fixed, minimal read-mostly view (per Section 1 design philosophy), not configurable per school.

**Default permission posture: deny-by-default.** Any module/action not explicitly granted to a role is denied. This is the safer convention for a system where schools can create custom roles — it means a misconfigured or newly cloned role can never accidentally over-expose sensitive student or financial data; the failure mode is a support request for missing access, not a privacy incident.

**Detailed permission matrix:** the specific module × action grid for every predefined template lives in the companion doc `permission-matrix.md` — that document is the baseline seed data for `role_permission` (see `database-schema.md` Section 8a) and what admin sees when cloning/tweaking a role.

**Why hybrid, not fully custom from day one:** a full permission-builder (any role, any module/action combination, freely defined) is more flexible but meaningfully more complex to build and to test for permission-leak bugs. Predefined templates cover the vast majority of real school divisions-of-labor immediately; the clone-and-customize layer gives schools with unusual needs an escape hatch without needing a fully generic builder from day one.

---

## 3. Modules

Legend: 🟢 Basic tier · 🔵 Pro tier (includes Basic) · 🟣 Ultra tier (includes Pro)

| # | Module | Tier | Purpose |
|---|---|---|---|
| 1 | **Students** | 🟢 | Student profiles, enrollment, guardians — the anchor entity |
| 2 | **Attendance** | 🟢 | Daily/period-wise tracking |
| 3 | **Academics** | 🟢 | Timetable, subjects, homework |
| 4 | **Grades** | 🟢 | Gradebook, exams, report cards |
| 5 | **Fees** | 🔵 | Invoicing, payments, receipts |
| 6 | **Messages** | 🔵 | Announcements, parent-teacher chat, notifications |
| 7 | **Staff** | 🔵 | Teacher/employee profiles, roles, leave |
| 8 | **Schedule** | 🔵 | School-wide events, holidays, exam schedule |
| 9 | **Library** | 🟣 | Book inventory and lending |
| 10 | **Transport** | 🟣 | Bus routes, student assignment |
| 11 | **Admissions** | 🟣 | Prospective student pipeline |
| 12 | **Documents** | 🟣 | ID cards, certificates, file storage |
| 13 | **Cafeteria** | 🟣 | Meal planning, meal-fee tracking |
| 14 | **Health** | 🟣 | Medical records, nurse visit logs |
| 15 | **Alumni** | 🟣 | Graduated student tracking |

**Detailed field/action/screen specs for each module** live in the companion doc: `module-specifications.md`. That document is the detailed reference; this PRD holds the decisions and priorities.

**Cross-module rules:**
- **Students** is the anchor — Attendance, Grades, Fees, Health, Documents, Alumni all reference it.
- **Messages** and **Schedule** are shared services — other modules trigger notifications/events through them rather than duplicating logic.
- **Fees**, **Cafeteria**, and **Transport** share one billing/invoicing engine — no duplicate billing logic per module.

**Student Lifecycle & Promotion Workflow** (owned by: Students module)

At the end of an academic session, students move to the next class. This is a defined workflow, not just a field edit:

1. **Trigger:** Admin runs "Promote to Next Class" as a bulk, end-of-year action, scoped by current class/section.
2. **Pre-checks** (Students module reads from, but does not modify, other modules):
   - **Grades module** — flags students who failed/didn't meet promotion criteria; admin can override to promote anyway or hold back individually. Never auto-blocks silently — always surfaces the list for admin decision.
   - **Fees module** — flags students with pending dues; admin can override or block promotion pending payment, per school policy (school-configurable, not hardcoded).
3. **Execution:** For promoted students, `class`/`section` field updates to the next grade level; students held back stay in their current class.
4. **Side effects triggered automatically:**
   - **Academics** — student is re-attached to the new class's timetable/subjects.
   - **Historical data preserved** — Attendance and Grades records stay tied to the student but scoped by academic session/year, so last year's records remain queryable and are never overwritten.
5. **Final-year exception:** Students completing their last grade are not promoted to a new class — instead they're transitioned to **Alumni** status (Alumni module), moved out of the active Students roster.
6. **Inactive/withdrawn students:** When an admin marks a student inactive (left school) or transitions them to Alumni, that student stops counting toward the school's active Student license count (see Section 4.2 — Licensing Model).

---

## 4. Subscription Model

Three tiers, feature-gated by module bundle (see table above), each with a base **license allowance** and the flexibility to purchase additional licenses without upgrading tiers.

### 4.1 Tiers (feature/module access)

- **Basic** — Students, Attendance, Academics, Grades. Core operations, small schools/tight budgets.
- **Pro** — Basic + Fees, Messages, Staff, Schedule. Main revenue tier — money and communication features live here.
- **Ultra** — Pro + Library, Transport, Admissions, Documents, Cafeteria, Health, Alumni. Large schools/districts, full suite, multi-campus, priority support, API access.

**Tier controls which modules a school can access. It does not by itself control how many users they can have — that's the licensing model below.**

### 4.2 Licensing Model (seats, decoupled from tier)

Each subscription tier includes a base license allocation across **four independent license categories**, and schools can purchase additional licenses in any category as an add-on, without being forced to upgrade to a tier whose extra modules they may not need.

**The four license categories:**

| Category | Who it covers | Consumed by |
|---|---|---|
| **Admin license** | Full-access administrator accounts | Active staff whose assigned role has `is_admin_role = true` (PRD Section 2.1) |
| **Faculty license** | Teaching staff | Active staff whose assigned role is the Teacher template (or a custom role cloned from it) |
| **Staff license** | Non-teaching operational roles — Accountant, Librarian, Registrar, Transport Coordinator, Nurse, and any custom roles cloned from these templates | Active staff in any non-teaching, non-admin role |
| **Student license** | Enrolled students | Active students |

Each license category is its own independent pool — a school can be well within its Student limit but need to buy extra Faculty licenses, or vice versa. They are not fungible with each other (a spare Staff license can't cover a Faculty overage).

**How it works:**
- Each tenant has a **license quota per category** — `admin_license_limit`, `faculty_license_limit`, `staff_license_limit`, `student_license_limit` — starting values set by tier, increased independently by add-on purchases.
- Each tenant has a **live active count per category**, computed from actual data (not a manually maintained number), based on each staff member's role category and each student's status.
- **A license is "consumed"** by a Student or Staff record only while that record is **active**, in the category its role/type maps to.
- **A license is "freed"** automatically the moment a record's status changes away from active, or its role category changes:
  - Student marked **Inactive** or transitioned to **Alumni** → frees a Student license
  - Staff marked **Inactive** (resigned/terminated) → frees a license in whichever category (Admin/Faculty/Staff) their role belonged to
  - Staff **reassigned to a different role category** (e.g., Teacher promoted to Admin) → frees one license in the old category, consumes one in the new category — checked against the new category's limit at the moment of reassignment
- **Enforcement:** Creating, reactivating, or reassigning a Student/Staff record checks the current active count in the relevant category against that category's limit. If at capacity, the action is blocked with a clear message naming the specific category ("You've reached your 20 Faculty license limit — free one up or add more") — never a silent failure or vague error, in line with the product's simplicity principle.
- **Add-on purchase:** Admin can buy additional licenses in any single category (e.g., +5 Faculty, +25 Students) independently, directly from a billing/settings screen — self-serve, no upgrade conversation required, billed as a recurring add-on alongside the base subscription.
- **Usage visibility:** Admin dashboard shows a simple usage indicator per category (e.g., "18 / 20 Faculty used," "87 / 100 Students used") so schools see when they're approaching a limit before hitting a hard block.

**Example (matches the scenario that prompted this decision):** A Basic-tier school with a 100-Student / 20-Faculty / 10-Staff / 2-Admin base allocation grows to 130 students but Faculty/Staff/Admin stay flat. Rather than upgrading to Pro (which they don't need for Fees/Messages/Schedule), they buy a "+50 Student" license add-on only, and stay on Basic — paying for the exact capacity they need, in the category they need it.

**Pricing model:** per-seat/month, priced independently per category (e.g., Student licenses priced lower per seat than Faculty/Staff/Admin, since student counts are much larger) — exact numbers TBD, not yet finalized.
**Other considerations:** free/trial tier possible (Attendance + Students, capped at a small Student license count e.g. 50, with 1 Admin and no Faculty/Staff add-ons); add-ons like SMS or extra storage may also be pay-as-you-go, following the same "buy more without upgrading tier" philosophy as licenses.

---

## 5. Tech Stack (Decided)

| Layer | Choice | Notes |
|---|---|---|
| **Frontend** | HTML, custom CSS (hand-written, no framework) + vanilla JS + **htmx** | Server-rendered via Django templates; htmx adds dynamic/partial-page interactivity (live search, inline edit, modals) without a full SPA framework; CSS is a hand-authored design system (see `component-library.md`), not a utility framework |
| **Backend** | **Django** | Also use Django REST Framework later if/when a mobile app needs an API |
| **Database** | **PostgreSQL** | Multi-tenancy: start with row-level (tenant_id column); consider schema-per-tenant if data isolation needs grow |
| **Auth** | Django's built-in auth, extended with custom roles (admin/teacher/parent/student) | No third-party auth service needed initially |
| **Payments** | **Stripe**, via `dj-stripe` package | Handles tiered subscription billing |
| **File storage** | AWS S3 or Cloudflare R2 | Photos, documents, generated PDFs |
| **Notifications** | Twilio (SMS), SendGrid/Resend (email), Firebase Cloud Messaging (push, if/when mobile apps exist) | |
| **PDF generation** | Puppeteer or `react-pdf`-equivalent / Django-compatible HTML-to-PDF tool | Report cards, ID cards, certificates |
| **Hosting** | Railway, Render, or DigitalOcean App Platform — **India region** (Mumbai/Bengaluru, per Section 8 compliance posture) | Move to AWS/GCP only at real scale (100+ schools) |

**Visual design tokens (decided):**

| Token | Value | Use |
|---|---|---|
| `--color-ink` | `#1C1F26` | Text, dark UI chrome |
| `--color-canvas` | `#FAFAF8` | Background |
| `--color-slate` | `#6B7280` | Secondary text, borders, muted labels |
| `--color-accent` | `#2F5FDB` | Primary actions, active states, links |
| `--color-moss` | `#2F7D5E` | Success/positive (Present, Paid) |
| `--color-rust` | `#C4432B` | Alert/negative (Absent, Overdue) |

- **UI/body typeface:** native system font stack (`-apple-system, "Segoe UI", sans-serif`) — fast-loading, legible at dense dashboard sizes, genuinely Apple-like since it's literally what Apple's own OS uses.
- **Display typeface (used sparingly):** a humanist serif, reserved for report cards, certificates, ID cards, and the login wordmark — the "official document" moments, not the dense dashboard UI.
- **Layout:** 8px spacing scale, 8px border radius, one subtle shadow level (never stacked/heavy shadows).
- Full component-level application of these tokens lives in `component-library.md`.

**Why this stack:** faster to build with one core language (Python) and no separate frontend build pipeline; Django Admin gives a free internal tool for managing tenants/subscriptions/debugging; htmx bridges the gap so key interactive screens (attendance grid, timetable builder) still feel modern without adopting full SPA complexity.

**Known tradeoff (accepted):** vanilla JS/htmx has a lower interactivity ceiling than React, and doesn't directly reuse for a future native mobile app. Accepted for now in favor of build speed and simplicity; can revisit if/when a dedicated mobile app or highly complex interactive screens become necessary.

**Implementation pattern: nested-modal "create new" sync (supports Section 1's inline-create rule)**

When a nested modal creates a dependency (e.g. a new Class from inside the Add Student modal), the underlying form must reflect it live, without a page reload. Mechanism:
1. The nested modal's "Create" button is an `hx-post` to the relevant endpoint (e.g. `/api/class-levels/`) — the new row is written to the database synchronously within that request.
2. The server's response does two things in one payload: (a) a fragment that closes the nested modal, and (b) an **htmx out-of-band swap** (`hx-swap-oob="true"`) targeting the dependent dropdown's element ID in the underlying form, returning the updated option list with the new value pre-selected server-side.
3. No custom JS state management is needed — htmx's OOB swap natively supports "one response updates two unrelated parts of the page." The rest of the underlying form (already-entered fields) is untouched, since only the targeted elements are swapped.
4. On validation failure (e.g. duplicate name), the server re-renders the nested modal with an inline error instead of the close+swap response; the underlying form is unaffected either way.

This pattern generalizes to every dependent-dropdown case in Section 1 (Class/Section, Role, Subject, Route, etc.) — implement it once as a reusable convention, not bespoke per module.

---

## 6. Multi-Tenant Architecture (Decided)

ClassiX is built **multi-tenant from day one**. One codebase, one deployment, serving many schools — each school is a "tenant."

**URL structure**
- Root domain: `classix.com` — marketing site, login, sign-up
- Each school gets a subdomain on signup: `school-name.classix.com`
- Subdomain slug is chosen by the school during onboarding (validated: unique, lowercase, alphanumeric + hyphen, no reserved words)
- Reserved subdomains that can never be assigned to a school: `www`, `app`, `api`, `admin`, `staging`, `mail`, `support`, `blog`, `status`, `docs`

**Tenant resolution (how the app knows which school is being viewed)**
- Every incoming request's subdomain is resolved to a tenant **before** any view logic runs — implemented as Django middleware that runs early in the request cycle.
- Middleware looks up the subdomain against a `Tenant`/`School` table, attaches the resolved tenant to the request, and all subsequent queries are scoped to that tenant automatically.
- Unknown/unregistered subdomain → redirect to marketing site or a "school not found" page, never a raw error.

**Data isolation strategy**
- **Starting approach: row-level multi-tenancy** — every tenant-owned table has a `tenant_id` (or `school_id`) foreign key; all queries are automatically filtered by the current tenant (enforced at the ORM/manager level, not left to each view to remember).
- **Escalation path:** if data isolation, compliance, or per-tenant backup/restore needs grow, migrate to **schema-per-tenant** (separate Postgres schema per school) — noted as an open decision (Section 7), not yet finalized as final architecture.
- Regardless of which strategy is used: **no query should ever be able to leak data across tenants.** This is a hard security requirement, not a nice-to-have.

**Custom domain support (future, not v1):** schools may eventually want to map their own domain (e.g., `portal.springfieldacademy.edu`) to their ClassiX subdomain — noted as future scope, not required for launch.

**Tenant provisioning flow (high-level)**
1. School signs up on `classix.com` → chooses subdomain slug → picks subscription tier
2. Tenant record created, initial admin user created, tenant-scoped database rows initialized (empty Students/Staff/etc. tables ready to populate)
3. **All seven predefined role templates (Admin, Teacher, Accountant, Librarian, Registrar/Front Desk, Transport Coordinator, Nurse/Health Officer) are auto-seeded for the new tenant** — these exist immediately, before the admin configures anything, so role dropdowns are never empty on day one (see `permission-matrix.md` for the seeded baseline). Only custom clones need to be created manually later.
4. Onboarding prompts the admin to set up **Class Levels and Sections** before inviting staff or adding students — this is foundational setup data every later Student/Staff/Academics screen depends on, so it's front-loaded rather than discovered as a mid-workflow gap.
5. School redirected to `school-name.classix.com` to start using the app

### Support Access Model

Support access follows an explicit customer-consent model.

Juspire employees do not automatically have access to tenant data.

When customer support is required:

1. A support request is raised.
2. A tenant administrator may approve temporary support access.
3. A time-limited support session is created.
4. Every support action is recorded in the audit log.
5. Access automatically expires when the session ends or reaches its expiry time.

Future versions may support configurable durations, read-only support sessions, and emergency access policies.

---

## 7. Development Phases / Build Order

Dependency-ordered build plan. Each phase assumes the previous phase is functional — don't start a phase's core work until its dependencies exist. This is the order to build in, not necessarily the order of user-facing launch (some phases can run in parallel where noted).

### Phase 0 — Foundation (nothing works without this)
- Django project setup, environment/config, hosting pipeline (Railway/Render)
- **Multi-tenant infrastructure** (Section 6): Tenant/School model, subdomain resolution middleware, reserved-subdomain handling
- Auth system + broad account category (Admin/Staff/Parent/Student) — tenant-scoped
- **Permission-check scaffolding** (Section 2.1): build every view/action behind a permission check from day one — even while only Admin and Teacher exist as roles. This avoids retrofitting permission checks into every module later when custom roles (Phase 4) are introduced.
- Base UI shell: layout, navigation, design system (custom CSS design tokens — colors, spacing, type scale — shared modal component, htmx conventions) — this is what every later screen builds on top of. **Build the reusable component set defined in the companion doc `component-library.md`** (Modal, Button, Form Field incl. dependent dropdown, Table, Sidebar Nav Item, License Chip, Card, Toggle Group, Tag/Badge, Mobile Tab Bar) here, once — every module afterward composes from these rather than writing new one-off markup.
- Django Admin configured for internal tenant/debug management

*Nothing in Phase 1+ should start until tenant resolution + auth + base UI shell exist — every module depends on "who is logged in, at which school, seeing what."*

### Phase 1 — Anchor data models
- **Students module** (full CRUD, profile, guardians) — the anchor entity almost everything else references
- **Staff module (basic profile only)** — needed because Academics/Attendance require assigning a teacher to a class
- Class/Section/Subject setup (foundational data admins configure before anything else is usable)

### Phase 2 — Basic tier core workflows
*(Depends on Phase 1: Students + Staff + Class/Section must exist first)*
- **Attendance module** — depends on Students + Class/Section + Staff (who marks it)
- **Academics module** — timetable, subjects, homework — depends on Staff (teacher assignment) + Class/Section
- **Grades module** — gradebook, report cards — depends on Students + Academics (subjects/exams)

→ At the end of Phase 2, the **Basic subscription tier is functionally complete.**

### Phase 3 — Billing & subscription infrastructure
*(Can run in parallel with Phase 2, but must be done before any tier is sold live)*
- Stripe integration (`dj-stripe`), subscription tier model, module feature-gating logic
- **Licensing/quota system** (Section 4.2): per-tenant Admin/Faculty/Staff/Student license limits (four independent pools), live active-count tracking per category (driven by role category for staff, status for students), enforcement on create/reactivate/reassign, self-serve per-category add-on purchase, usage indicator UI per category
- Tenant onboarding/signup flow (school signs up → picks tier → subdomain provisioned)
- This phase is infrastructure, not a "module" — required before real customers can be onboarded, regardless of which modules exist yet.

### Phase 4 — Pro tier modules
*(Depends on Phase 2 + Phase 3: needs Students/Staff/Academics data, and tier-gating to control access)*
- **Fees module** — depends on Students + billing infrastructure (shares invoicing logic, Section 3 cross-module rule)
- **Messages module** — depends on Staff + Students/Parents (recipients) — becomes the shared notification service other modules plug into
- **Staff module (full)** — extend basic profile with leave management. Also where the **full RBAC system** (Section 2.1) is built: predefined role templates (Accountant, Librarian, Registrar, Transport Coordinator, Nurse), clone-and-customize UI, module+action permission storage and enforcement, Teacher class-scoping logic.
- **Schedule module** — mostly standalone, but ties into Academics (exam dates) and Messages (event notifications)

→ At the end of Phase 4, the **Pro subscription tier is functionally complete.**

### Phase 5 — Ultra tier modules
*(Each depends on Phase 1 anchor models; largely independent of each other — can be built in any order or parallelized across a team)*
- **Documents** — depends on Students/Staff (who a document belongs to)
- **Library** — depends on Students/Staff (borrowers)
- **Transport** — depends on Students (route assignment)
- **Admissions** — depends on ability to create a Student record from an accepted applicant (Phase 1 model reused)
- **Cafeteria** — depends on Fees (meal billing, Phase 4)
- **Health** — depends on Students, ties into Messages for parent notification
- **Alumni** — depends on Students (graduated status transition)

→ At the end of Phase 5, the **Ultra subscription tier is functionally complete.**

### Phase 6 — Cross-cutting polish (ongoing, not a single point in time)
- PDF generation (report cards, ID cards, certificates) — needed as soon as Grades/Documents exist, refined over time
- Notifications (SMS/email/push) — layered onto Messages once core modules generate events worth notifying about
- Performance, security review (especially tenant-isolation audit — see Section 6), accessibility pass
- UI/UX refinement pass against Section 1 principles — revisit every screen once real workflows exist, trim clicks, convert flows to modals where a full page crept in during initial build

### Phase 7 — Launch readiness
- End-to-end testing across roles and tenants
- Onboarding documentation/UI for new schools
- Marketing site (`classix.com` root)
- Production hardening, backups, monitoring

**Rule of thumb for any agent or developer picking up work:** if a task touches a module, check what that module depends on in this list before starting — build the dependency first, even if it feels like a detour.

---

## 8. Compliance, Privacy & Data Retention (Target Market: India)

**Not legal advice.** This section documents ClassiX's technical posture toward India's data protection law so it's built in from day one, not retrofitted. Confirm consent flow wording, data processing agreement terms, and exact retention rules with an Indian data-protection lawyer before launch — the items below are the engineering-relevant defaults to build against in the meantime.

**Applicable law:** India's **Digital Personal Data Protection Act, 2023 (DPDP Act)**, with the **DPDP Rules, 2025** notified 13 November 2025. The Act is legally in force; enforcement is rolling out in phases, with full penalty enforcement expected around May 2027. This means: not yet a "day-one drop-dead" compliance deadline, but the obligations are real and active now, not hypothetical — build to them from the start rather than treating this as later work.

**Likely data-fiduciary structure (confirm with counsel):** each **School (tenant) is the Data Fiduciary** — they collect and are responsible for consent from parents/guardians and students. **ClassiX operates as the Data Processor**, processing data on the school's behalf under a Data Processing Agreement (DPA) with each tenant. This is the standard structure for B2B SaaS under DPDP and mirrors how most GDPR-style regimes treat a software vendor vs. its customers — but should be confirmed contractually before onboarding real schools.

**Children's data — the most consequential requirement for ClassiX specifically:** the DPDP Act requires **verifiable parental/guardian consent** before processing a minor's personal data, and restricts behavioral tracking/targeted advertising directed at children (not relevant to ClassiX's ad-free model, but the consent requirement is). Practical implication for the schema and Student enrollment workflow:
- The `student_guardian` relationship (see `database-schema.md`) needs a **consent capture field** — recorded at the point a guardian is linked to a student during enrollment (Registrar/Admin workflow), not left implicit.
- ClassiX's job is to give schools the **technical means** to capture and record this consent — the school (as Data Fiduciary) is responsible for actually obtaining it.

**Hosting:** given an India-only launch, default to hosting in an **India-region data center** (both for straightforward data-residency posture and for latency) rather than a US/EU default region, even though DPDP doesn't yet mandate hard localization for most data categories as of this writing — cross-border transfer restrictions are still pending separate notification, so this is a "safe default," not yet a hard legal requirement.

**Backup & retention (decided default, pending legal confirmation):**
- Daily automated backups, 30-day point-in-time recovery window.
- **No automatic hard deletes on Student, Staff, Grade, or Fee records.** "Delete" in the UI means a status change (Inactive/Archived), not permanent removal — consistent with the Delete-button convention flagged in `component-library.md`.
- **Right-to-erasure requests** (a DPDP Data Principal right) are routed to a **manual admin/legal review process**, not an automatic hard-delete action — schools generally have a legitimate educational record-keeping basis to retain academic records for a period even after an erasure request, but the exact balance needs legal confirmation before this is finalized as a hard rule.
- Breach notification tooling (audit logs, incident detection) is covered under Phase 6's security review in the build order (Section 7) — flagging the DPDP breach-notification obligation as a reason that phase isn't optional polish.

---

## 9. Explicitly Out of Scope (for now)

- Native mobile apps (web-based only for v1; DRF API groundwork may be laid but no app built yet)
- Full payroll/tax processing under Staff (kept basic — salary + payment history only)
- AI-based features (not discussed/decided yet)
- Multi-language support (not discussed/decided yet)
- Kubernetes/advanced infra (not needed until real scale)

*(This section should be updated as more scope decisions are made — anything not yet decided should be added here rather than assumed.)*

---

## 10. Open Decisions / Not Yet Finalized

- Exact pricing numbers per tier
- Exact base license counts per category per tier (e.g., Basic = 100 Students/20 Faculty/10 Staff/2 Admin — placeholder numbers used as example, not finalized)
- Per-category add-on pack sizes and pricing (e.g., "+25 Students" vs "+5 Faculty" pack pricing may differ)
- Whether Staff payroll goes deeper or stays basic
- Schema-per-tenant vs row-level multi-tenancy — final call (currently: start row-level, escalate later)
- Custom domain mapping for schools — timing (post-v1 confirmed, exact mechanism TBD)
- Whether free trial tier ships in v1
- Database schema design (next step)
- Screen-by-screen wireframes (next step)
- Detailed timeline/estimates per phase (Section 7 defines order, not duration)

---

## 11. AI Agent Instructions (Anti-Hallucination Protocol)

This section is written specifically for AI coding agents (Claude, Claude Code, or any other AI assistant/agent used to build this software). Read this section in full before generating code, architecture, or answering questions about the product.

**Rules for any AI agent working on this project:**

1. **This PRD is the single source of truth.** If your own memory, assumption, or a prior response in a session conflicts with this document, this document wins. Do not silently favor your own prior output over what's written here.
2. **Do not invent modules, fields, tiers, tech choices, or naming that aren't in this document.** If something is needed but not specified here, say so explicitly and ask, or propose it as a new decision to be added — don't quietly assume and proceed.
3. **Check Section 1 (Design Philosophy) before building any screen or flow.** If what you're about to build requires more than 1-2 clicks for a common action, adds a new full-page screen where a modal would work, or breaks role-based scoping — stop and flag it instead of building it.
4. **Respect the multi-tenant boundary at all times (Section 6).** Every piece of code that touches tenant-owned data must be scoped to the current tenant. If you're generating a query, model, or view and you're not sure it's tenant-safe, flag it rather than guessing.
5. **Respect the RBAC model at all times (Section 2.1).** Admin's full access is hardcoded and must never be made editable/removable in any code path. Every module action must sit behind a permission check from Phase 0 onward — never add a screen or endpoint without one, even before custom roles exist.
6. **Follow the build order in Section 7 — don't build out of dependency order.** If asked to build a module before its dependencies exist (e.g., Attendance before Students), flag the missing dependency rather than stubbing around it silently.
7. **Check Section 9 (Out of Scope) before adding functionality.** If a request seems to require something listed as out-of-scope, point that out rather than building it silently.
8. **Check Section 10 (Open Decisions) before treating something as final.** If it's listed as not-yet-finalized, don't present your output as if it were a settled decision — flag the assumption you're making.
9. **When corrected with "refer to the PRD"** (or similar), re-read this entire document before responding again, and explicitly acknowledge what was inconsistent before proceeding.
10. **Update Section 12 (Document History)** whenever a material decision changes during a session, so the document stays accurate for the next session/agent.
11. **If uncertain, say so.** A flagged uncertainty is always better than a confident, incorrect assumption — especially for architecture, tenant isolation, permissions, and billing logic where mistakes are costly to unwind.
12. **Respect Section 8 (Compliance/Privacy) on anything touching consent, retention, or deletion.** Never implement a hard delete on Student/Staff/Grade/Fee records as a shortcut, even if asked casually — route it through the status-change/archival pattern instead, and flag if a request seems to bypass this.

---

## 12. Document History

- **v1:** Initial PRD compiled from module definitions, subscription tiers, and tech stack decisions.
- **v2:** Product name set to ClassiX (by Juspire, provisional). Added Multi-Tenant Architecture section (Section 6): subdomain-based tenancy (`school-name.classix.com`), row-level isolation as starting strategy, tenant provisioning flow. Added AI Agent Instructions (Section 9).
- **v3:** Added Development Phases / Build Order (Section 7) — dependency-ordered plan from Phase 0 (foundation/multi-tenancy/auth) through Phase 7 (launch readiness). Renumbered subsequent sections accordingly.
- **v4:** Added Student Lifecycle & Promotion Workflow (Section 3) — defines end-of-year promotion, Grades/Fees pre-checks, Academics side-effects, and Alumni transition for final-year students. Reworked Subscription Model (Section 4) to add a Licensing Model (4.2) decoupled from tier: base license allocation per tier, self-serve add-on license purchases, active-count-based consumption/freeing for Students and Staff. Added license/quota system to Phase 3 of the build order.
- **v5:** Added Roles & Permissions / RBAC (Section 2.1) — hybrid model: hardcoded full-access Admin, predefined role templates (Accountant, Librarian, Registrar, Transport Coordinator, Nurse), admin clone-and-customize with module+action permission granularity, Teacher class-scoping handled separately from module permissions. Updated Phase 0 (permission-check scaffolding from day one) and Phase 4 (full RBAC build-out) in the build order accordingly.
- **v6:** Restructured Licensing Model (Section 4.2) from two categories (Student/Staff) to four independent license pools: **Admin, Faculty (Teachers), Staff (non-teaching operational roles), Student** — each priced, purchased, tracked, and enforced independently. Staff license consumption is now driven by role category (tied to the RBAC role from Section 2.1), not a flat staff count.
- **v7:** Decided deny-by-default as the RBAC default permission posture (Section 2.1). Added companion doc `permission-matrix.md` — the full module × action grid for all seven predefined role templates, which serves as `role_permission` seed data and the baseline for clone-and-tweak. Flagged Cafeteria and Alumni as modules with no owning template today (Admin-only by default, customizable via clone-and-tweak).
- **v8:** Added the inline "+ Create new…" dependent-dropdown pattern to Section 1 design philosophy — forms with dropdowns tied to setup data (Class/Section, Role, etc.) must offer nested-modal creation without losing in-progress form data. Clarified tenant provisioning flow: all 7 role templates auto-seed at tenant creation; Class/Section setup is front-loaded into onboarding rather than discovered as a mid-workflow gap.
- **v9:** Added the concrete technical implementation pattern (Section 5) for how a nested-modal creation writes to the database and syncs live into the underlying form's dropdown without a page reload — htmx out-of-band swap, server-rendered pre-selected option, no custom JS state management.
- **v10:** Added companion doc `component-library.md` — a reusable-component approach for the vanilla JS/htmx stack (Django template includes for structure/behavior, hand-written CSS classes for shared styling), with a 10-component inventory derived from `wireframes.html` and explicit gaps (danger button, toasts, empty states, loading states) flagged for design before Phase 0 build. Linked into Phase 0 of the build order.
- **v11:** Dropped Tailwind CSS from the stack — frontend styling is now purely hand-written custom CSS, no utility framework. Updated Section 5 (Tech Stack) and `component-library.md` accordingly.
- **v12:** Locked three pre-build decisions: (1) **Visual design tokens** — final color palette (ink/canvas/slate/accent/moss/rust), system-font UI typeface + sparingly-used serif display face, 8px spacing/radius scale, added to Section 5. (2) **New Section 8 — Compliance, Privacy & Data Retention**, targeting India's DPDP Act 2023 / DPDP Rules 2025: school-as-Data-Fiduciary / ClassiX-as-Data-Processor structure (pending legal confirmation), verifiable guardian consent capture requirement for minors' data, India-region hosting, backup/retention policy (30-day recovery, no hard deletes on core records, erasure requests routed to manual review). Renumbered subsequent sections (Out of Scope → 9, Open Decisions → 10, AI Agent Instructions → 11, Document History → 12) and added an AI-agent rule against implementing shortcut hard-deletes. (3) Backup/retention policy folded into the new Section 8 rather than standing alone.
- **v13:** Added companion document architecture-guide.md to formally define the project's engineering architecture. This document becomes the implementation reference for project structure, Django app organization, dependency rules, service/selector patterns, template organization, static asset strategy, and coding conventions. The PRD remains the product source of truth, while the Architecture Guide becomes the engineering source of truth.
- **v14:** Introduced Platform vs Tenant user architecture. Added customer-approved support sessions, clarified Tenant Admin scope, and documented the separation between platform administration and tenant RBAC.

*(Update this log each time a material decision changes, so the document stays trustworthy as the single reference point.)*
