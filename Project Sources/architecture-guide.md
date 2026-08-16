# ClassiX Architecture Guide

**Version:** v1  
**Status:** Active  
**Purpose:** Defines the engineering architecture, project structure, and coding conventions for ClassiX.

---

# 1. Purpose

This document is the engineering source of truth for ClassiX.

- The **PRD** defines **what** to build.
- This document defines **how** it must be built.

If an engineering decision conflicts with the PRD, the PRD takes precedence.

---

# 2. Architecture Principles

- One Django app per business module.
- Thin views, fat services.
- Business logic belongs in services.
- Complex queries belong in selectors.
- Reusable UI components over duplicate markup.
- Server-rendered UI first (Django + HTMX).
- Multi-tenant safety by default.
- Permission checks on every action.
- No duplicated CSS or JavaScript.
- Consistent project structure across all apps.

---

# 3. Project Structure

```
classix/
│
├── apps/
│   ├── core/
│   ├── tenants/
│   ├── accounts/
│   ├── rbac/
│   ├── billing/
│   ├── audit/
│
│   ├── students/
│   ├── attendance/
│   ├── academics/
│   ├── grades/
│   ├── fees/
│   ├── staff/
│   ├── messages/
│   ├── schedule/
│   ├── library/
│   ├── transport/
│   ├── admissions/
│   ├── documents/
│   ├── cafeteria/
│   ├── health/
│   └── alumni/
│
├── config/
├── templates/
├── static/
├── media/
├── docs/
├── requirements/
├── scripts/
└── manage.py
```

---

The system contains two completely separate authentication domains.

### Tenant Authentication

Tenant users authenticate against the tenant-scoped User model.

Every User belongs to exactly one tenant.

Authentication is performed within the resolved tenant context.

---

### Platform Authentication

Platform users authenticate separately.

Platform users never belong to a tenant.

Platform functionality exists outside the tenant request lifecycle.

---

### Support Sessions

Support access is implemented through temporary Support Sessions.

Middleware establishes both:

- current platform actor
- current tenant

during an approved support session.

Normal tenant requests continue to operate with tenant isolation unchanged.

---

# 4. Infrastructure Apps

## core

Shared functionality.

Contains:

- Base models
- Mixins
- Constants
- Validators
- Utilities
- Common middleware
- Shared helpers

---

## tenants

Owns:

- Tenant model
- Tenant middleware
- Tenant managers
- Tenant services

Nothing else.

---

## accounts

Owns:

- User model
- Authentication
- Login
- Logout
- Password reset
- Profile

Does NOT own Staff or Student data.

---

## rbac

Owns:

- Roles
- Permissions
- Permission decorators
- Permission mixins
- Permission services

---

## billing

Owns:

- Subscription
- Licensing
- Stripe
- Module feature gating

Does NOT own school fee collection.

---

## audit

Owns:

- Activity logs
- Audit logs
- Security logs

---

# 5. Business Module Structure

Every business module follows the same layout.

```
students/

    migrations/

    templates/

    tests/

    admin.py
    apps.py
    forms.py
    models.py
    permissions.py
    selectors.py
    services.py
    signals.py
    tables.py
    filters.py
    urls.py
    views.py
```

No exceptions.

---

# 6. App Responsibilities

Each app owns only its own domain.

Example:

Students

Owns:

- Student
- Guardian
- Enrollment
- Promotion

Does NOT own:

- Attendance
- Grades
- Fees

---

# 7. Dependency Rules

Infrastructure apps may be used by every module.

Foundation modules may be used by dependent modules.

Lower-level apps must never import higher-level apps.

Example:

✔ Attendance → Students

✔ Grades → Academics

✘ Students → Attendance

Avoid circular dependencies.

---

# 8. Services

Business logic belongs in services.

Example:

```
create_student()

promote_student()

graduate_student()

archive_student()
```

Views should never contain business logic.

---

# 9. Selectors

Complex queries belong in selectors.

Example:

```
active_students()

students_by_section()

teacher_dashboard()

overdue_invoices()
```

Views should call selectors instead of writing ORM queries.

---

# 10. Permissions

Every action must pass through permission checking.

Flow:

```
Request

↓

Permission Check

↓

View

↓

Service

↓

Selector

↓

Model
```

Never bypass permissions.

---

# 11. Multi-Tenant Rules

Every tenant-owned model must inherit the shared tenant base model.

Never trust tenant_id from requests.

Never query tenant-owned models without tenant filtering.

Tenant context must come from middleware.

---

# 12. URL Structure

Each app owns its own URLs.

Example

```
students/

urls.py
```

Root project includes module URLs.

---

# 13. Templates

Each app owns its templates.

```
students/

templates/

    students/

        pages/

        partials/

        modals/
```

---

# 14. Shared Templates

Reusable templates live globally.

```
templates/

    base.html

    components/

    includes/
```

Examples:

- button
- modal
- card
- table
- badge
- form_field
- pagination

---

# 15. Static Assets

Global only.

```
static/

    css/

    js/

    icons/

    images/

    fonts/
```

Do NOT create:

```
students.css

attendance.css

fees.css
```

Use shared design system files.

---

# 16. HTMX

Rules:

- Full page → full template
- HTMX → partial template
- Forms submit through HTMX where appropriate
- Nested modal uses Out-of-Band Swap
- Avoid custom JavaScript when HTMX can solve it

---

# 17. Forms

Validation belongs inside forms.

Business logic belongs inside services.

---

# 18. Naming Conventions

Apps

```
students
attendance
grades
fees
```

Models

```
Student
Guardian
Invoice
Section
```

Services

```
create_student()

promote_student()
```

Selectors

```
active_students()

teacher_sections()
```

---

# 19. Testing

Every app contains

```
tests/

    test_models.py

    test_forms.py

    test_views.py

    test_services.py

    test_permissions.py
```

---

# 20. Security Rules

- Never bypass tenant filtering.
- Never bypass permission checks.
- Never hard delete protected records.
- Validate all user input.
- Keep business rules inside services.

---

# 21. Adding a New Module

Every new module must:

1. Create Django app.
2. Register URLs.
3. Create models.
4. Create services.
5. Create selectors.
6. Create permissions.
7. Create templates.
8. Add navigation.
9. Add tests.
10. Update documentation.

---

# 22. AI Agent Rules

When generating code:

- Follow this architecture.
- Do not invent folder structures.
- Do not invent coding patterns.
- Reuse existing components.
- Keep module boundaries clean.
- Respect tenant isolation.
- Respect RBAC.
- Keep views thin.
- Keep services reusable.

---

# 23. Architecture Decision Log

## v1

- Added Architecture Guide.
- Standardised project folder structure.
- One Django app per module.
- Introduced Infrastructure Apps.
- Standardised app layout.
- Standardised services/selectors pattern.
- Standardised template structure.
- Standardised static asset organisation.
- Defined dependency rules.
- Defined engineering conventions for future development.

## v2
- Added dual authentication architecture (Platform and Tenant), support-session model, and request lifecycle for approved support access.