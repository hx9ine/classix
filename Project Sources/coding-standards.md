# ClassiX Coding Standards

**Version:** v1  
**Status:** Active  
**Purpose:** Defines the coding conventions and development standards for all ClassiX contributors.

---

# 1. Purpose

This document defines **how code should be written**.

- **PRD** = Product decisions
- **Architecture Guide** = Project structure
- **Coding Standards** = Code quality and consistency

All contributors should follow these standards.

---

# 2. General Principles

- Keep code simple.
- Prefer readability over cleverness.
- Avoid duplication.
- Write code for future maintainers.
- Keep functions small and focused.
- Prefer composition over inheritance.
- Explicit is better than implicit.

---

# 3. Python Standards

- Follow PEP 8.
- Use 4 spaces for indentation.
- Maximum line length: 100 characters.
- Use type hints where practical.
- Use f-strings instead of string concatenation.
- Avoid wildcard imports.

Example

```python
def create_student(name: str) -> Student:
    ...
```

---

# 4. Django Standards

- One Django app per business module.
- Business logic belongs in services.
- Queries belong in selectors.
- Forms contain validation only.
- Views coordinate requests and responses only.
- Keep models focused on data and simple model behaviour.

Never place business logic inside:

- views.py
- templates
- signals

---

# 5. File Organisation

Every module follows:

```
models.py

views.py

urls.py

forms.py

services.py

selectors.py

permissions.py

filters.py

tables.py

signals.py

admin.py

tests/
```

---

# 6. Naming Conventions

## Apps

```
students
attendance
grades
fees
```

---

## Models

Singular.

```
Student
Guardian
Invoice
AttendanceRecord
```

---

## Services

Verb-based.

```
create_student()

promote_student()

archive_student()
```

---

## Selectors

Noun-based.

```
active_students()

student_dashboard()

teacher_sections()
```

---

## Variables

Use descriptive names.

Good

```python
student_count
invoice_total
```

Avoid

```python
x
temp
data
obj
```

---

# 7. Imports

Order imports as follows:

```python
# Standard library

# Third-party packages

# Django

# Local apps
```

Example

```python
import uuid

from django.db import models

from apps.students.models import Student
```

Never use wildcard imports.

---

# 8. Views

Views should:

- validate permissions
- validate forms
- call services
- return responses

Views should NOT:

- contain business logic
- perform complex queries
- duplicate validation

---

# 9. Models

Models should contain:

- fields
- relationships
- simple helper properties
- model validation when appropriate

Avoid placing large workflows inside models.

---

# 10. Services

Services are responsible for:

- creating records
- updating records
- deleting/archiving
- business rules
- workflows
- transactions

Services should be reusable.

---

# 11. Selectors

Selectors perform read operations.

Examples

```
active_students()

student_profile()

pending_invoices()
```

Selectors should not modify data.

---

# 12. Forms

Forms handle:

- validation
- cleaning data
- displaying errors

Forms should never perform business workflows.

---

# 13. Templates

Templates should contain presentation only.

Never place business logic inside templates.

Prefer reusable components.

---

# 14. CSS

- Use shared design tokens.
- Use shared component classes.
- Do not create page-specific CSS unless absolutely necessary.
- Avoid inline styles.

---

# 15. JavaScript

- Vanilla JavaScript only.
- Prefer HTMX before writing JavaScript.
- Keep JavaScript modular.
- Avoid global variables.
- No jQuery.

---

# 16. HTMX

Use HTMX for:

- search
- filters
- pagination
- modals
- inline editing
- partial updates

Avoid writing custom JavaScript if HTMX can solve the problem.

---

# 17. Permissions

Every endpoint must check permissions.

Never expose functionality based solely on hiding UI elements.

Always validate permissions server-side.

---

# 18. Multi-Tenancy

Every tenant-owned query must be tenant-scoped.

Never trust tenant IDs from user input.

Never bypass tenant filtering.

---

# 19. Error Handling

- Fail clearly.
- Return useful validation messages.
- Log unexpected exceptions.
- Never expose stack traces to users.

---

# 20. Logging

Log:

- authentication events
- permission failures
- important business actions
- unexpected exceptions

Do not log:

- passwords
- tokens
- sensitive personal information

---

# 21. Testing

Every feature should include tests where applicable.

Minimum:

```
test_models.py

test_services.py

test_views.py

test_forms.py

test_permissions.py
```

Bug fixes should include regression tests whenever practical.

---

# 22. Git Standards

Branch names

```
feature/student-module

feature/attendance

bugfix/fees

refactor/services
```

Commit messages

```
Add student promotion workflow

Fix attendance validation

Refactor student service
```

Keep commits focused on a single logical change.

---

# 23. Documentation

When making a material change:

- Update the PRD if product behaviour changes.
- Update the Database Schema if data structures change.
- Update Module Specifications if screens, fields, or actions change.
- Update the Permission Matrix if permissions change.
- Update the Component Library if reusable UI changes.
- Update the Architecture Guide if implementation architecture changes.
- Update this document if coding conventions change.

Documentation should be updated as part of the same change.

---

# 24. Code Review Checklist

Before merging:

- Code follows architecture guide.
- Permissions implemented.
- Tenant-safe.
- No duplicated logic.
- Uses services and selectors correctly.
- Reuses components.
- Tests pass.
- Documentation updated if required.

---

# 25. AI Agent Rules

When generating code:

- Follow the PRD.
- Follow the Architecture Guide.
- Follow these Coding Standards.
- Do not invent new architectural patterns.
- Do not duplicate components.
- Keep code simple.
- Flag uncertainty instead of guessing.

---

# 26. Change Log

## v1

- Initial coding standards.
- Established Python, Django, HTMX, CSS, JavaScript, testing, Git, documentation, and code review conventions.
- Defined standards for all future ClassiX development.