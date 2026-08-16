# School Management Software — Module Specifications

## Tier legend
🟢 Basic · 🔵 Pro (includes Basic) · 🟣 Ultra (includes Pro)

---

## 1. Students 🟢

**Purpose:** Single source of truth for every student's identity and academic placement.

**Fields**
- Full name, DOB, gender, photo, student ID (auto-generated)
- Class, section, roll number, enrollment date, status (active/inactive/graduated/transferred)
- Guardian(s): name, relationship, phone, email, emergency contact flag
- Address, blood group, previous school (optional)

**Licensing note:** a student consumes one Student license slot while `status = active`. Marking a student inactive or transitioning to alumni frees that license slot automatically (see PRD Section 4.2).

**Actions**
- Add/edit/deactivate student — Class/Section dropdowns support inline "+ Create new…" (PRD Section 1) so an admin never has to abandon the Add Student form to set up a missing class/section elsewhere
- **Guardian consent capture** (PRD Section 8, India DPDP Act) — when linking a guardian to a student during enrollment, the enrolling staff member records that guardian's consent to data processing (`student_guardian.consent_recorded_at`)
- Bulk import (CSV)
- **Promote to next class** (end-of-year batch action) — see full workflow in PRD Section 3 "Student Lifecycle & Promotion Workflow": checks Grades (pass/fail) and Fees (dues) before promoting, updates class/section, re-attaches to new Academics timetable, preserves prior-year Attendance/Grades history, and routes final-year students to Alumni instead of a new class.
- Transfer certificate generation
- Search/filter by class, section, status

**Screens**
- Student list (table, filterable)
- Student profile (tabs: Info, Attendance, Grades, Fees)
- Add/Edit form

---

## 2. Attendance 🟢

**Purpose:** Fast daily/period tracking with minimal taps.

**Fields**
- Date, class, section, period (if period-wise)
- Status per student: Present / Absent / Late / Excused
- Marked by (teacher), timestamp
- Reason/note (optional, for absences)

**Actions**
- Mark attendance (default: today, pre-filled "Present" — tap only exceptions)
- Edit past attendance (with audit log)
- Auto-notify parent on absence (Pro+, ties into Messages)
- Export attendance report (daily/monthly/term)

**Screens**
- Mark attendance (roster view, swipe/tap to toggle status)
- Attendance schedule (per student, color-coded)
- Class attendance summary

---

## 3. Academics 🟢

**Purpose:** Timetable, subjects, and homework in one place.

**Fields**
- Subjects (name, code, assigned teacher, class)
- Timetable: day, period, time slot, subject, teacher, room
- Homework/assignment: title, description, subject, class, due date, attachment
- Submission status per student (submitted/pending/late)

**Actions**
- Build/edit timetable (drag-and-drop grid)
- Post homework/assignment
- Mark submissions received
- View today's schedule (role-based: teacher sees their periods, student sees their day)

**Screens**
- Timetable grid (weekly view)
- Homework feed (chronological, filterable by subject)
- Assignment detail + submission tracker

---

## 4. Grades 🟢

**Purpose:** Exam scores, gradebook, and report card generation.

**Fields**
- Exam/term name, subject, max marks, marks obtained
- Grading scale (A-F, percentage, GPA — configurable per school)
- Report card template (school logo, remarks, attendance summary, grade summary)
- Teacher remarks per subject

**Actions**
- Enter marks (bulk grid entry per class/subject)
- Auto-calculate grade/GPA from marks
- Generate report card (PDF, per student or batch)
- Publish grades (toggle visibility to parents/students)

**Screens**
- Gradebook (spreadsheet-style entry)
- Report card preview/generator
- Student performance trend (simple chart)

---

## 5. Fees 🔵

**Purpose:** Fee structure, invoicing, and payment tracking.

**Fields**
- Fee structure: class-wise, term-wise, fee heads (tuition, transport, lab, etc.)
- Invoice: student, amount, due date, status (paid/unpaid/partial/overdue)
- Payment record: amount, date, method (cash/card/bank/online), receipt number
- Discounts/scholarships (flat or %)

**Actions**
- Generate invoices (bulk, per class or individually)
- Record payment / mark paid
- Send payment reminders (auto, ties into Messages)
- Generate receipt (PDF)
- Apply discount/waiver

**Screens**
- Fee dashboard (collected vs. pending, by class)
- Student fee ledger
- Invoice/receipt generator
- Payment history

---

## 6. Messages 🔵

**Purpose:** Announcements and direct parent-teacher communication.

**Fields**
- Announcement: title, body, audience (school-wide/class/section), attachment
- Direct message: sender, recipient, thread, timestamp, read status
- Notification preferences (push/email/SMS)

**Actions**
- Post announcement (targeted by audience)
- Start/reply to conversation
- Mark as read
- Push notification trigger (attendance alert, fee due, homework posted — auto-generated)

**Screens**
- Announcement feed
- Inbox/chat thread view
- Compose screen

---

## 7. Staff 🔵

**Purpose:** Teacher and employee records, roles, and basic HR.

**Fields**
- Name, photo, role (predefined template or admin-customized clone — see PRD Section 2.1: Accountant, Librarian, Registrar, Transport Coordinator, Nurse, Teacher, or custom), subjects/classes assigned (for Teacher-category roles, defines data scope)
- Contact info, joining date, employment status
- Leave requests: type, dates, status (pending/approved/rejected)
- Basic payroll: salary, payment history (optional, may be Ultra depending on scope)

**Licensing note:** a staff member consumes one license slot while employment status is active — from the **Admin, Faculty, or Staff** license pool depending on their assigned role's category (see PRD Section 4.2): Admin-flagged roles draw from the Admin pool, the Teacher role draws from the Faculty pool, and all other operational roles (Accountant, Librarian, Registrar, Transport Coordinator, Nurse, and custom clones of these) draw from the Staff pool. Marking staff inactive frees the license slot in whichever category it occupied. Reassigning a staff member to a different role category frees a slot in the old category and consumes one in the new category.

**Roles & Permissions actions (see PRD Section 2.1)**
- Assign a predefined role template to a staff member (Accountant, Librarian, Registrar, Transport Coordinator, Nurse, Teacher) — these are auto-seeded for every school at tenant creation (PRD Section 6), so they're always present in the Add Staff role dropdown without setup
- Clone a template into a custom role and toggle module + action (view/create/edit/delete) permissions — the Add Staff role dropdown supports inline "+ Create new custom role…" (PRD Section 1) if the needed custom role doesn't exist yet, without abandoning the in-progress Add Staff form
- Admin role is fixed — cannot be edited, restricted, or deleted, by anyone
- Assign classes/subjects to Teacher-category roles (drives data scope, separate from module permission)

**Actions**
- Add/edit staff profile
- Assign classes/subjects
- Approve/reject leave requests
- Role & permission management (who can access what modules)

**Screens**
- Staff directory
- Staff profile (tabs: Info, Classes, Leave, Payroll)
- Leave request form + approval queue

---

## 8. Schedule 🔵

**Purpose:** School-wide events, holidays, and exam schedules in one view.

**Fields**
- Event: title, date/time, type (holiday/exam/event/meeting), audience
- Recurring event support (annual holidays)

**Actions**
- Create/edit event
- RSVP (for meetings/events, optional)
- Sync exam dates with Grades module

**Screens**
- Schedule view (month/week)
- Event detail
- Upcoming events widget (dashboard)

---

## 9. Library 🟣

**Purpose:** Book inventory and lending.

**Fields**
- Book: title, author, ISBN, category, copies available
- Lending record: student/staff, book, issue date, due date, return date, fine (if overdue)

**Actions**
- Add/edit book catalog
- Issue/return book
- Auto-calculate overdue fines
- Search catalog

**Screens**
- Catalog (searchable list)
- Issue/return desk view
- Overdue report

---

## 10. Transport 🟣

**Purpose:** Bus routes and student transport assignment.

**Fields**
- Route: name, stops, driver, vehicle number
- Student assignment: route, stop, pickup/drop time
- Live location (optional, requires GPS hardware integration)

**Actions**
- Create/edit route
- Assign student to route/stop
- Track bus status (if GPS integrated)

**Screens**
- Route list/map view
- Student transport assignment
- Live tracking map (if applicable)

---

## 11. Admissions 🟣

**Purpose:** Prospective student pipeline from inquiry to enrollment.

**Fields**
- Applicant: name, DOB, applying for class, guardian contact
- Application status: inquiry → applied → interview → accepted/rejected → enrolled
- Documents uploaded (birth certificate, previous marksheets)
- Entrance test score (if applicable)

**Actions**
- Add applicant / online application form (public-facing)
- Move applicant through pipeline stages
- Convert accepted applicant to Student record (auto-link to Students module)

**Screens**
- Pipeline board (kanban-style by stage)
- Applicant profile
- Public application form (external-facing)

---

## 12. Documents 🟣

**Purpose:** Centralized storage for certificates, IDs, and official files.

**Fields**
- Document: type (ID card, certificate, transfer letter), linked to student/staff, file, issue date

**Actions**
- Generate ID card (template-based, with photo/QR code)
- Generate certificate (bonafide, transfer, character)
- Upload/store external documents
- Bulk print (e.g., all ID cards for a class)

**Screens**
- Document library (filterable by type/person)
- Template editor (basic)
- Bulk generation tool

---

## 13. Cafeteria 🟣

**Purpose:** Meal planning and optional meal-fee tracking.

**Fields**
- Menu: day, meal items, dietary tags (veg/vegan/allergen)
- Student meal plan enrollment (if paid meal program)

**Actions**
- Publish weekly menu
- Enroll/unenroll student in meal plan
- Track meal fee (links to Fees module)

**Screens**
- Weekly menu view
- Meal plan enrollment list

---

## 14. Health 🟣

**Purpose:** Basic medical records and nurse visit logs.

**Fields**
- Student health profile: allergies, conditions, blood group, emergency contact
- Visit log: date, reason, action taken, follow-up needed

**Actions**
- Log nurse/clinic visit
- Flag critical conditions (visible badge on student profile)
- Notify parent on visit (ties into Messages)

**Screens**
- Health profile (per student)
- Visit log (chronological)

---

## 15. Alumni 🟣

**Purpose:** Track graduated students for engagement/networking.

**Licensing note:** transitioning a student to Alumni frees their Student license slot (see PRD Section 4.2) — this is the standard path for final-year students, as opposed to marking them simply "inactive."

**Fields**
- Alumni profile: graduation year, current occupation, contact, linked original student record
- Events/reunions

**Actions**
- Auto-move graduated students to Alumni (from Students module)
- Post alumni-only announcements/events

**Screens**
- Alumni directory
- Alumni event feed

---

## Cross-module notes
- **Students** is the anchor entity — Attendance, Grades, Fees, Health, Documents, and Alumni all reference it.
- **Messages** and **Schedule** function as shared services — most modules can trigger a notification or event through them rather than duplicating logic.
- **Fees** and **Cafeteria/Transport** share the invoicing engine — don't build separate billing logic per module.
