# ClassiX Module Blueprint

## Purpose

This document defines the standard implementation architecture for every
new ClassiX module. It complements the PRD by standardizing folder
structure, naming, CRUD patterns, HTMX usage, UI composition, and layer
responsibilities.

------------------------------------------------------------------------

# 1. Design Principles

-   The PRD is the source of truth.
-   Keep modules self-contained.
-   Models define data.
-   Forms validate data.
-   Selectors read data.
-   Services contain business logic.
-   Views orchestrate requests.
-   Reuse shared UI components.
-   Reuse shared HTMX helpers.

# 2. Standard Module Structure

``` text
apps/<module>/
├── admin/
├── forms/
├── models/
├── permissions/
├── selectors/
├── services/
├── views/
├── templates/
│   └── <module>/
│       ├── pages/
│       ├── partials/
│       └── modals/
├── urls.py
└── apps.py
```

# 3. Naming

-   Package names are plural.
-   Entity filenames are singular.
-   Templates:
    -   pages/`<entity>`{=html}s.html
    -   partials/`<entity>`{=html}\_table.html
    -   modals/`<entity>`{=html}\_form.html
    -   modals/delete\_`<entity>`{=html}.html

# 4. Layer Responsibilities

## Models

Own persistent data.

## Forms

Validation and cleaning only.

## Selectors

Read-only database access.

## Services

Business logic, transactions, create/update/delete.

## Views

HTTP orchestration only.

# 5. CRUD Convention

Each CRUD entity provides:

-   list
-   create
-   update
-   delete

Profile pages exist only when justified (e.g. Student, Staff).

# 6. UI Composition

Every page extends:

``` django
layouts/page.html
```

Structure:

``` text
Page Header
Toolbar (optional)
Filters (optional)
Content
```

# 7. Shared Components

-   Layout: card, modal, page_section
-   Navigation: page_header, topbar
-   Forms: field, row, section, actions, dependent_select,
    select_options
-   Search: search_bar
-   Toolbar: page_toolbar
-   Data: table, badge, empty_state
-   Feedback: alert

# 8. HTMX

Use shared helpers:

-   apps/core/htmx.py
-   apps/core/crud.py
-   apps/core/oob.py

# 9. Multi-tenancy

Always tenant-scope tenant-owned data.

# 10. RBAC

All module actions require permission checks. Admin access remains
hardcoded.

# 11. Import Convention

Expose public APIs via package **init**.py.

# 12. Goal

Every module should follow one consistent architecture and reuse the
shared framework wherever possible.
