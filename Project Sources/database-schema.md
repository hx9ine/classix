# Database Schema — ClassiX
**Companion document to:** `PRD-school-management-software.md` and `module-specifications.md`
**Status:** Living document — reflects Section 6 (Multi-Tenancy) and Section 4.2 (Licensing) of the PRD. Any conflict with the PRD → PRD wins; update this doc to match.

**Instruction to AI coding agents:** This is the schema to implement against. Do not invent tables, fields, or relationships not listed here. If something needed isn't defined, flag it and propose an addition rather than improvising — then this document should be updated (see Document History).

---

## Conventions (apply to every table unless noted)

- **Primary key:** `id` — UUID, not auto-increment integer (safer across tenants, no sequential-ID leakage between schools)
- **Tenant scoping:** every tenant-owned table has a `tenant_id` (FK → `tenant.id`), enforced at the ORM manager level per PRD Section 6. Tables without `tenant_id` are explicitly marked "global" below.
- **Timestamps:** `created_at`, `updated_at` on every table (auto-managed)
- **Soft delete:** prefer a `status`/`is_active` field over hard deletes for anything with history value (Students, Staff, Invoices, etc.) — hard deletes only for true junk data
- **Naming:** snake_case table and column names, singular table names (`student`, not `students`)

---

## 1. Tenancy & Auth (Phase 0)

### platform_user (global)

Represents Juspire employees who manage the SaaS platform.

These users are not associated with any tenant.

Responsibilities include:

- tenant management
- billing
- platform administration
- customer support

Platform users do not automatically receive access to tenant-owned records.
Tenant data may only be accessed through an approved Support Session.

### support_session (global)

Temporary authorised support access.

| Field | Type | Notes |
|--------|------|------|
| id | UUID |
| platform_user_id | FK |
| tenant_id | FK |
| approved_by_user_id | FK → user |
| ticket_reference | string |
| reason | text |
| started_at | datetime |
| expires_at | datetime |
| ended_at | datetime nullable |
| status | active / expired / revoked |

Every support session must be fully auditable.

Support sessions never permanently bypass tenant isolation.
They temporarily establish an audited context through which platform users may access a tenant's environment.

### `tenant` *(global — not tenant-scoped, this IS the tenant table)*
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| school_name | string | |
| subdomain_slug | string, unique | e.g. `springfield` → `springfield.classix.com` |
| custom_domain | string, nullable | future scope (PRD 6) |
| subscription_tier | enum: basic/pro/ultra | |
| admin_license_limit | integer | base + add-ons combined (PRD 4.2) |
| faculty_license_limit | integer | base + add-ons combined |
| staff_license_limit | integer | base + add-ons combined (non-teaching operational roles) |
| student_license_limit | integer | base + add-ons combined |
| status | enum: active/suspended/cancelled | |
| stripe_customer_id | string, nullable | |
| created_at, updated_at | datetime | |

### `user` *(tenant-scoped)*
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| email | string, unique per tenant | |
| password_hash | string | Django auth-managed |
| account_category | enum: staff/parent/student | Broad account category — determines which portal UI loads. Fine-grained permissions for staff live in `role` + `role_permission` (Section 2.1, Section 8 below) via `staff.role_id`, not here. |
| first_name, last_name | string | |
| phone | string, nullable | |
| is_active | boolean | account-level, distinct from Student/Staff license status |
| last_login | datetime, nullable | |
| created_at, updated_at | datetime | |

*Note: `user` is the login/auth identity. `student` and `staff` (below) are profile/business records — a Student may or may not have a linked `user` (portal login is optional for younger students, guardian may log in on their behalf instead).*

### `academic_session` *(tenant-scoped)*
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| name | string | e.g. "2026-2027" |
| start_date, end_date | date | |
| is_current | boolean | only one session should be current at a time |

---

## 2. Academic Structure (Phase 1)

### `class_level`
| Field     | Type        | Notes                                |
| --------- | ----------- | ------------------------------------ |
| id        | UUID (PK)   |                                      |
| tenant_id | FK → tenant | Tenant-scoped                        |
| name      | string      | Examples: Grade 1, Grade 2, Class 10 |
| sort_order | integer | determines promotion sequence |

#### Constraints:
Unique: (tenant_id, name)

### `section`
| Field          | Type             | Notes             |
| -------------- | ---------------- | ----------------- |
| id             | UUID (PK)        |                   |
| tenant_id      | FK → tenant      | Tenant-scoped     |
| class_level_id | FK → class_level | Parent class      |
| name           | string           | Examples: A, B, C |
|academic_session_id | FK → academic_session | sections are scoped per session |

#### Constraints:
(tenant_id, academic_session_id, class_level_id, name)

---

## 3. Students Module (Phase 1 — anchor entity)

### `student`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| user_id | FK → user, nullable | optional portal login |
| student_code | string | school-facing ID, auto-generated |
| first_name, last_name | string | |
| dob | date | |
| gender | string | |
| photo_url | string, nullable | |
| section_id | FK → section | current class/section |
| roll_number | string, nullable | |
| status | enum: active/inactive/alumni/transferred | **drives license consumption — PRD 4.2** |
| enrollment_date | date | |
| blood_group | string, nullable | |
| address | text, nullable | |
| previous_school | string, nullable | |
| academic_session_id | FK → academic_session | session the current record applies to |

### `guardian`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| user_id | FK → user, nullable | optional parent portal login |
| first_name, last_name | string | |
| phone, email | string | |
| relationship | string | e.g. "Mother" |

### `student_guardian` *(join table)*
| Field | Type | Notes |
|---|---|---|
| student_id | FK → student | |
| guardian_id | FK → guardian | |
| is_emergency_contact | boolean | |
| consent_recorded_at | datetime, nullable | **DPDP Act compliance (PRD Section 8)** — timestamp this guardian consented to processing this student's personal data. Captured during enrollment; null means consent not yet obtained. |
| consent_recorded_by_id | FK → user, nullable | which staff member captured the consent (audit trail) |

*Supports a guardian linked to multiple students (siblings) and a student having multiple guardians.*

---

## 4. Attendance Module (Phase 2)

### `attendance_record`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| student_id | FK → student | |
| section_id | FK → section | |
| date | date | |
| period_id | FK → timetable_period, nullable | null = daily attendance, not period-wise |
| status | enum: present/absent/late/excused | |
| marked_by_id | FK → staff | |
| note | text, nullable | |
| academic_session_id | FK → academic_session | |

**Unique constraint:** (student_id, date, period_id) — prevents duplicate marks.

---

## 5. Academics Module (Phase 2)

### `subject`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| name, code | string | |

### `timetable_period`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| section_id | FK → section | |
| subject_id | FK → subject | |
| staff_id | FK → staff | |
| day_of_week | integer (0-6) | |
| start_time, end_time | time | |
| room | string, nullable | |

### `assignment` *(homework)*
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| section_id | FK → section | |
| subject_id | FK → subject | |
| staff_id | FK → staff | |
| title, description | string/text | |
| due_date | date | |
| attachment_url | string, nullable | |

### `submission`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| assignment_id | FK → assignment | |
| student_id | FK → student | |
| status | enum: pending/submitted/late | |
| submitted_at | datetime, nullable | |
| file_url | string, nullable | |

---

## 6. Grades Module (Phase 2)

### `exam`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| academic_session_id | FK → academic_session | |
| name | string | e.g. "Term 1 Final" |
| start_date, end_date | date | |

### `grade_entry`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| student_id | FK → student | |
| exam_id | FK → exam | |
| subject_id | FK → subject | |
| marks_obtained | decimal | |
| max_marks | decimal | |
| grade_letter | string, nullable | derived or manually entered |
| remarks | text, nullable | |

**Unique constraint:** (student_id, exam_id, subject_id)

*Report cards are a generated PDF artifact (Phase 6), not a stored table — computed on demand from `grade_entry` + `attendance_record` summaries.*

---

## 7. Fees Module (Phase 4)

### `fee_structure`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| class_level_id | FK → class_level | |
| academic_session_id | FK → academic_session | |
| fee_head | string | e.g. "Tuition", "Lab" |
| amount | decimal | |

### `invoice`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| student_id | FK → student | |
| academic_session_id | FK → academic_session | |
| total_amount | decimal | |
| due_date | date | |
| status | enum: unpaid/partial/paid/overdue | |

### `invoice_line_item`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| invoice_id | FK → invoice | |
| fee_head | string | |
| amount | decimal | |

### `payment`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| invoice_id | FK → invoice | |
| amount | decimal | |
| payment_date | date | |
| method | enum: cash/card/bank/online | |
| receipt_number | string | |

### `discount`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| student_id | FK → student | |
| type | enum: flat/percent | |
| value | decimal | |
| reason | string, nullable | |

---

## 8. Messages Module (Phase 4)

### `announcement`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| title, body | string/text | |
| audience_type | enum: school/class/section | |
| audience_ref_id | UUID, nullable | class_level_id or section_id depending on audience_type |
| attachment_url | string, nullable | |
| created_by_id | FK → user | |

### `message_thread`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |

### `message_thread_participant` *(join table)*
| Field | Type | Notes |
|---|---|---|
| thread_id | FK → message_thread | |
| user_id | FK → user | |

### `message`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| thread_id | FK → message_thread | |
| sender_id | FK → user | |
| body | text | |
| sent_at | datetime | |
| read_at | datetime, nullable | |

---

## 9. Staff Module (Phase 1 basic / Phase 4 full)

### `staff`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| user_id | FK → user | |
| first_name, last_name | string | |
| photo_url | string, nullable | |
| staff_role_label | string, denormalized | display convenience only (e.g. "Accountant") — source of truth is `role_id` below |
| role_id | FK → role | drives module + action permissions, Section 2.1 |
| employment_status | enum: active/inactive | **drives license consumption — PRD 4.2** |
| joining_date | date | |
| phone | string, nullable | |

### `leave_request`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| staff_id | FK → staff | |
| leave_type | string | |
| start_date, end_date | date | |
| status | enum: pending/approved/rejected | |
| reason | text, nullable | |

### `payroll_record` *(basic, per PRD 6 "kept basic")*
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| staff_id | FK → staff | |
| salary_amount | decimal | |
| payment_date | date | |

---

## 9a. Roles & Permissions (RBAC) — supports Section 2.1

### `role`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant, nullable | **null = system template** (Accountant, Librarian, Registrar, Transport Coordinator, Nurse, Teacher, Admin), shared across all tenants, read-only. **non-null = a tenant's cloned/custom role.** |
| name | string | |
| is_admin_role | boolean | true only for the one hardcoded Admin role — enforced full access regardless of `role_permission` rows; this flag, not the permission rows, is what grants Admin's access, so it can never be stripped by editing permissions |
| license_category | enum: admin/faculty/staff | which license pool (PRD Section 4.2) a staff member in this role draws from. `admin` for the Admin role, `faculty` for the Teacher role, `staff` for all other operational templates (Accountant, Librarian, Registrar, Transport Coordinator, Nurse) and their custom clones. Inherited from the template on clone — not independently editable, since it's a billing-relevant field. |
| is_editable | boolean | false for system templates and the Admin role; true for tenant-cloned custom roles |
| cloned_from_role_id | FK → role, nullable | traceability — which template a custom role was cloned from |

### `role_permission`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| role_id | FK → role | |
| module | string | matches module names: students, attendance, academics, grades, fees, messages, staff, schedule, library, transport, admissions, documents, cafeteria, health, alumni |
| action | enum: view/create/edit/delete | |
| allowed | boolean | |

**Unique constraint:** (role_id, module, action)

*Seed data: baseline `role_permission` rows for all seven predefined system templates (Admin, Teacher, Accountant, Librarian, Registrar/Front Desk, Transport Coordinator, Nurse/Health Officer) are defined in the companion doc `permission-matrix.md` — implement seeding directly from that matrix, don't re-derive it. Default posture is deny-by-default: absence of a row for a given (role, module, action) means denied.*

*Note: rows here are irrelevant for any role where `role.is_admin_role = true` — Admin's access is enforced by that flag directly in code, bypassing the permission table entirely, so there is no data path by which Admin's access can be misconfigured or revoked.*

*Teacher class/subject scoping (which sections a Teacher-category staff member can see within Academics/Attendance/Grades) is **not** stored here — it's derived from the existing `timetable_period.staff_id` / `section.class_teacher_id` assignments. Don't model "assigned classes" as a permission row; it's a data-scope join, not an access-control toggle.*

---

## 10. Schedule Module (Phase 4)

### `schedule_event`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| title | string | |
| event_type | enum: holiday/exam/event/meeting | |
| start_datetime, end_datetime | datetime | |
| audience_type | enum: school/class/section | |
| audience_ref_id | UUID, nullable | |
| recurrence_rule | string, nullable | iCal RRULE format if recurring |

---

## 11. Library Module (Phase 5)

### `book`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| title, author, isbn, category | string | |
| total_copies, available_copies | integer | |

### `book_lending`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| book_id | FK → book | |
| borrower_type | enum: student/staff | |
| borrower_id | UUID | polymorphic — references student.id or staff.id based on borrower_type |
| issue_date, due_date | date | |
| return_date | date, nullable | |
| fine_amount | decimal, default 0 | |

---

## 12. Transport Module (Phase 5)

### `transport_route`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| name, driver_name, vehicle_number | string | |

### `transport_stop`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| route_id | FK → transport_route | |
| name | string | |
| sequence_order | integer | |
| pickup_time, drop_time | time | |

### `student_transport_assignment`
| Field | Type | Notes |
|---|---|---|
| student_id | FK → student | |
| route_id | FK → transport_route | |
| stop_id | FK → transport_stop | |

---

## 13. Admissions Module (Phase 5)

### `applicant`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| first_name, last_name | string | |
| dob | date | |
| applying_for_class_level_id | FK → class_level | |
| guardian_name, guardian_phone, guardian_email | string | |
| status | enum: inquiry/applied/interview/accepted/rejected/enrolled | pipeline stage |
| entrance_score | decimal, nullable | |
| linked_student_id | FK → student, nullable | set when converted to enrolled Student (PRD Admissions explanation) |

### `applicant_document`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| applicant_id | FK → applicant | |
| doc_type | string | |
| file_url | string | |

---

## 14. Documents Module (Phase 5)

### `document`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| owner_type | enum: student/staff | |
| owner_id | UUID | polymorphic reference |
| doc_type | enum: id_card/certificate/transfer_letter/other | |
| file_url | string | |
| issue_date | date | |

---

## 15. Cafeteria Module (Phase 5)

### `meal_menu`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| date | date | |
| meal_items | JSON | list of items + dietary tags |

### `meal_plan_enrollment`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| student_id | FK → student | |
| start_date, end_date | date | |
| linked_invoice_id | FK → invoice, nullable | shared billing engine (PRD Section 3) |

---

## 16. Health Module (Phase 5)

### `health_profile` *(1:1 with student)*
| Field | Type | Notes |
|---|---|---|
| student_id | FK → student, PK | |
| allergies | text, nullable | |
| conditions | text, nullable | |
| blood_group | string, nullable | |
| emergency_contact_note | text, nullable | |

### `health_visit_log`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| student_id | FK → student | |
| visit_date | datetime | |
| reason | text | |
| action_taken | text | |
| follow_up_needed | boolean | |
| logged_by_id | FK → staff | |

---

## 17. Alumni Module (Phase 5)

### `alumni`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| student_id | FK → student | original record — status becomes "alumni" (frees license, PRD 4.2) |
| graduation_year | integer | |
| current_occupation | string, nullable | |
| contact_email | string, nullable | |

---

## 18. Billing & Licensing (Phase 3)

### `subscription`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| tier | enum: basic/pro/ultra | mirrors tenant.subscription_tier — source of truth is here, tenant table caches it |
| stripe_subscription_id | string | |
| status | enum: active/past_due/cancelled | |
| current_period_end | datetime | |

### `license_addon`
| Field | Type | Notes |
|---|---|---|
| id | UUID (PK) | |
| tenant_id | FK → tenant | |
| license_type | enum: admin/faculty/staff/student | matches the four categories in PRD Section 4.2 |
| quantity | integer | e.g. +25 |
| stripe_line_item_id | string | |
| purchased_at | datetime | |

*Active license usage per category (`X / Y Faculty used`, etc., PRD 4.2) is **computed live**: Student count via `COUNT(student) WHERE tenant_id = X AND status = 'active'`; Admin/Faculty/Staff counts via `COUNT(staff) JOIN role WHERE tenant_id = X AND employment_status = 'active' AND role.license_category = <category>`. Not stored as a separate table, to avoid sync bugs. Cache/denormalize only if performance requires it later.*

---

## Entity Relationship Summary (high-level)

```
tenant (1) ──< user, student, staff, [all tenant-scoped tables]

academic_session (1) ──< section, exam, fee_structure

class_level (1) ──< section
section (1) ──< student, timetable_period, assignment, attendance_record

student (1) ──< attendance_record, grade_entry, invoice, submission,
                book_lending, health_profile, document, alumni,
                student_transport_assignment, meal_plan_enrollment
student (M) ──< >(M) guardian   [via student_guardian]

staff (1) ──< timetable_period, leave_request, payroll_record,
              attendance_record (marked_by), assignment
staff (M) ──> (1) role   [role_id]
role (1) ──< role_permission

invoice (1) ──< invoice_line_item, payment

applicant (1) ──> student   [linked_student_id, set on enrollment]

subscription (1) ── tenant (1)
license_addon (M) ── tenant (1)
```

---

## Notes for implementation

- **Polymorphic references** (`borrower_id` in `book_lending`, `owner_id` in `document`) — implement via Django's `ContentType` framework or two nullable FKs, whichever the dev team prefers; not prescribing the mechanism, just the intent (one record can belong to either a student or staff member).
- **Row-level tenant isolation** (PRD Section 6): every query against a tenant-scoped table must filter by `tenant_id`. Recommend a custom Django manager/base model class that all tenant-scoped models inherit from, auto-injecting the filter — don't rely on every view remembering to add it manually.
- **This schema assumes row-level multi-tenancy** (current PRD default). If the project later escalates to schema-per-tenant (PRD Section 6 escalation path), `tenant_id` columns become unnecessary within each schema, but the table structures themselves stay the same.

---

## Document History

- **v1:** Initial schema derived from PRD Section 3 (Modules), Section 4.2 (Licensing), Section 6 (Multi-Tenancy), and `module-specifications.md`. Covers all 15 modules + tenancy/auth/billing infrastructure.
- **v2:** Added `role` and `role_permission` tables (Section 8a) to support PRD Section 2.1 RBAC — hardcoded Admin via `is_admin_role` flag (not permission rows), system templates vs. tenant-cloned custom roles, module+action permission granularity. Updated `account_category` to a broad account category (staff/parent/student) and `staff` to reference `role_id` instead of a flat enum. Clarified that Teacher class-scoping is a data-scope join, not a permission row.
- **v3:** Restructured licensing from two categories (student/staff) to four (PRD Section 4.2 v6): added `admin_license_limit` and `faculty_license_limit` to `tenant` alongside `staff_license_limit`/`student_license_limit`; added `license_category` (admin/faculty/staff) to `role`, inherited on clone, driving which pool a staff member's license draws from; updated `license_addon.license_type` enum to admin/faculty/staff/student.
- **v4:** Linked `role_permission` seed data to the new companion doc `permission-matrix.md`, which defines the full module × action grid for all seven predefined templates and confirms deny-by-default as the default posture.
- **v5:** Added `consent_recorded_at` / `consent_recorded_by_id` to `student_guardian` (PRD Section 8) — supports India's DPDP Act verifiable-guardian-consent requirement for processing a minor's personal data, captured at enrollment.
- **v6:** Added global `platform_user` and `support_session` tables. Clarified separation between platform authentication and tenant authentication. Renamed `user.role` to `account_category` to avoid conflict with RBAC roles.
