# Component Library — ClassiX
**Companion document to:** `PRD-school-management-software.md` (Section 1 — Design Philosophy, Section 5 — Tech Stack) and `wireframes.html`
**Status:** Living document — the reusable UI building blocks every module is built from. Build these once in Phase 0 (base UI shell); every module afterward composes screens from this set rather than writing new one-off markup.

**Instruction to AI coding agents:** Before writing markup for any screen, check whether it should be composed from a component listed here. Do not create ad-hoc, one-off HTML for something that matches an existing component's purpose — extend the component instead, so behavior (htmx wiring, styling) stays consistent everywhere. If a screen genuinely needs a new repeating pattern not listed here, propose adding it to this document rather than inlining it silently.

---

## Approach (no component framework, no CSS framework — still component-driven)

Since the stack is Django templates + htmx + vanilla JS + **hand-written custom CSS** (no React/shadcn, no Tailwind or other utility framework), "components" are built with two complementary mechanisms:

1. **Django template includes** (`{% include %}`) — the structural/behavioral reuse layer. Each component is a small template file in `templates/components/`, parameterized via Django's `with` syntax. This is the direct equivalent of a component's "props."
2. **A hand-authored CSS design-token system** — the visual consistency layer. Define a small set of CSS custom properties (`--color-*`, `--space-*`, `--font-*`, `--radius-*`, etc.) once in a root stylesheet, then write one dedicated class per component (`.btn-primary`, `.modal`, `.card`) that references those tokens. Every call site just uses the class name — no utility classes strung together in markup, no framework dependency, but still a single source of truth for the look.

Together, a component = one template file (structure + htmx behavior) + one dedicated CSS class built from shared design tokens (appearance). Change either once, it updates everywhere the component is used. This is arguably a *tighter* discipline than a utility framework, since there's no fallback to ad-hoc inline utility combinations — every visual decision has to go through a named class.

**Example usage pattern (illustrative, not final code):**
```
{% include "components/button.html" with label="Save Student" variant="primary" %}

{% include "components/modal.html" with modal_id="addStudent" title="Add Student" %}
  {% include "components/form_field.html" with label="Full name" name="full_name" %}
{% endinclude %}
```

```css
/* design tokens — decided in PRD Section 5, defined once here */
:root {
  --color-ink: #1C1F26;
  --color-canvas: #FAFAF8;
  --color-slate: #6B7280;
  --color-accent: #2F5FDB;
  --color-moss: #2F7D5E;   /* success — Present, Paid */
  --color-rust: #C4432B;   /* alert — Absent, Overdue */
  --space-sm: 8px;
  --space-md: 16px;
  --radius: 8px;
  --font-ui: -apple-system, "Segoe UI", sans-serif;
  --font-display: Georgia, "Iowan Old Style", serif; /* report cards, certificates, login wordmark only */
}

/* component class — built from tokens, referenced everywhere */
.btn-primary {
  background: var(--color-ink);
  color: #fff;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius);
  border: none;
  font-family: var(--font-ui);
}
```

### Templating mechanism: `{% include %}` vs. custom `{% component %}...{% endcomponent %}`

Django's built-in `{% include %}` only takes simple values as parameters (via `with`) — it can't cleanly accept **arbitrary nested HTML** as a parameter. That's fine for components whose varying part is just text/labels, but not for components whose entire inner content changes every time they're used.

**Use `{% include ... with %}` for:** Button, Tag/Badge, License Chip, Sidebar Nav Item, Toggle Group — their "varying part" is simple values (a label, a variant name, a state).
```django
{% include "components/button.html" with label="Save Student" variant="primary" %}
```

**Use a hand-written custom `{% component %}...{% endcomponent %}` block tag for:** Modal (including nested modals), Card, and any wrapper whose inner content is genuinely different markup each time (e.g. the Add Student modal's form fields vs. the Record Payment modal's form fields). This is a small, self-authored Django template tag (no third-party package — it's a templating mechanism, not a UI dependency, so it doesn't conflict with the "no component library" decision), implemented once in `templatetags/components.py`:

```python
from django import template
register = template.Library()

@register.tag(name="component")
def do_component(parser, token):
    args = token.split_contents()
    component_name = args[1]
    nodelist = parser.parse(("endcomponent",))
    parser.delete_first_token()
    return ComponentNode(component_name, nodelist)

class ComponentNode(template.Node):
    def __init__(self, component_name, nodelist):
        self.component_name = component_name
        self.nodelist = nodelist

    def render(self, context):
        slot_content = self.nodelist.render(context)  # everything between the tags
        return template.loader.render_to_string(
            f"components/{self.component_name}.html",
            {"slot": slot_content},
            request=context.get("request"),
        )
```
Usage — the content between the tags is captured and rendered inside the component template via `{{ slot }}`:
```django
{% component "modal" %}
  <h3>Add Student</h3>
  {% include "components/form_field.html" with label="Full name" %}
{% endcomponent %}
```
This is what makes the Modal component genuinely reusable despite every modal in the app having completely different contents — the shell (header, overlay, footer, close behavior, htmx wiring) lives once in `components/modal.html`; only the `{{ slot }}` changes per call site.

---

## Component inventory

Pulled directly from `wireframes.html` — every one of these appeared at least twice across the wireframe screens, confirming it's a real reusable pattern and not a one-off.

### 1. Modal
The core interaction shell (PRD Section 1 — modal-based workflows). Used for: Add Student, Record Payment, New Announcement, Add Staff, Create New Class (nested).
- **Variants:** standard modal, **nested modal** (opens on top of another, lower z-index overlay tint per the wireframe convention, preserves the parent form underneath)
- **Structure:** header (title + close ✕), body (slot for form content), footer (Cancel + primary action button)
- **Behavior baked in:** open/close via htmx or vanilla JS toggle; nested modals must not close their parent; supports receiving an out-of-band swap target reference (Section 5 nested-modal sync pattern) for its trigger button
- **Implementation:** built via the custom `{% component %}...{% endcomponent %}` block tag (see "Templating mechanism" above), not `{% include %}` — every modal's inner content is different form markup, which only the block-tag/slot approach handles cleanly

### 2. Button
- **Variants:** `primary` (solid dark, main action — "Save," "Post"), `secondary` (outline, "Cancel"), and implicitly a `danger` variant should be added for destructive actions (Delete) not yet in the wireframes — flagging this as a gap to fill before build, since Delete actions exist in the permission matrix but weren't wireframed
- **Consistent rule:** the action verb on the button must match the resulting confirmation message (per PRD's interface-writing convention — "Save Student" → success message says "Student saved," not "Submitted")

### 3. Form Field
Used across every Add/Edit modal (Students, Staff, Fees, Messages).
- **Variants:** text input, textarea (Message body), **dependent dropdown** (Class, Section, Role — see below), plain dropdown (Payment method)
- **Dependent dropdown is a distinct sub-component**, not just a `<select>`: it includes the "+ Create new…" inline option and the htmx out-of-band wiring described in the PRD Section 5 implementation pattern. Any dropdown backed by admin-configurable setup data (Class, Section, Role, Subject, Route) should use this sub-component, not a plain dropdown.

### 4. Table
Used for: Students list, Fees list, Staff list, Gradebook, Permission Matrix.
- **Variants:** standard read list (Students, Fees), **editable grid** (Gradebook — cells behave like inline form fields), **matrix/toggle grid** (Permission Matrix — cells are tap-to-toggle rather than text)
- Consistent header styling (uppercase, muted) and row-hover treatment across all variants

### 5. Sidebar Nav Item
Used in the app shell across every admin/staff screen.
- **States:** default, active (`on` in the wireframe), locked (tier-gated — e.g. "Library 🔒 Ultra" — shown but not clickable, with a tooltip/label explaining the tier requirement rather than just hiding it, so schools on lower tiers know the feature exists)

### 6. License Chip
Used on the Admin Dashboard — one per license category (Admin/Faculty/Staff/Student per PRD Section 4.2).
- **States:** normal, near-limit (visual warning treatment — not yet color-defined, deferred to visual design pass), at-limit (paired with a "buy more" affordance)

### 7. Card / Box
The generic content container (dashboard summary tiles, announcement list items, parent mobile cards). Lowest-common-denominator component — most other components are built from it plus additional structure.

### 8. Toggle Group
Used specifically for Attendance marking (Present/Absent/Late) — a compact multi-state selector, single tap to change state, no separate save step per row (batch-saved via the screen's main Save action).

### 9. Tag / Badge
Small inline label — used for role indicators ("Role: Accountant — full access"), status indicators (Active/Inactive), and tier-lock indicators.

### 10. Mobile Tab Bar
Bottom navigation for the Parent/Student mobile views — fixed position, icon+label per tab, active-state indicator. Distinct from Sidebar Nav (desktop) — per PRD Section 2, Parent/Student get a genuinely different, minimal surface, not a responsive collapse of the admin sidebar.

---

## Explicit gaps to design before Phase 0 build (not yet wireframed)

- **Danger/destructive button variant** — Delete actions exist in the permission matrix but no wireframe screen exercised one; needs a confirmation pattern too (e.g. a confirm step inside the same modal, not a separate browser `confirm()` dialog, to stay consistent with the modal-based philosophy)
- **Toast/inline success & error messaging** — none of the wireframes show what happens after a Save succeeds or fails; needs a consistent pattern (per PRD's interface-writing convention: errors state what happened and how to fix it, never vague)
- **Empty states** — what Students/Fees/Messages tables look like with zero rows (e.g. a brand-new school) — PRD's writing guidance already says empty states should be "an invitation to act," but no component defines this yet
- **Loading/pending states** — htmx requests aren't instant; needs a consistent in-flight indicator for buttons/forms so nothing feels unresponsive

---

## Document History

- **v1:** Initial component inventory derived from `wireframes.html` — 10 core reusable components (Modal, Button, Form Field, Table, Sidebar Nav Item, License Chip, Card, Toggle Group, Tag/Badge, Mobile Tab Bar), plus flagged gaps (danger button, toasts, empty states, loading states) not yet covered by any wireframe screen.
- **v2:** Removed Tailwind from the approach — replaced with a hand-authored CSS design-token system (custom properties for color/spacing/type/radius) plus one dedicated class per component. No utility-class framework in the stack.
- **v3:** Documented the templating mechanism decision: `{% include %}` for simple-value components (Button, Tag, License Chip, Sidebar Nav Item, Toggle Group) vs. a hand-written custom `{% component %}...{% endcomponent %}` block tag with slot-capturing for components whose inner content varies structurally each use (Modal, Card). Included the full custom tag implementation.
- **v4:** Replaced placeholder token values with the final decided design tokens from PRD Section 5 — color palette (ink/canvas/slate/accent/moss/rust), system-font UI typeface, sparingly-used serif display face, 8px radius.
