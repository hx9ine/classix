from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import Assignment


# ============================================================================
# Validation
# ============================================================================

def _validate_tenant_scope(
    *,
    tenant,
    section,
    subject,
    staff,
):
    """
    Ensure all tenant-owned objects belong to the current tenant.
    """

    objects = [
        ("section", section),
        ("subject", subject),
        ("staff", staff),
    ]

    for name, obj in objects:

        if obj.tenant_id != tenant.pk:
            raise ValidationError(
                f"The selected {name} does not belong to the current tenant."
            )


# ============================================================================
# Create
# ============================================================================

@transaction.atomic
def create_assignment(
    *,
    tenant,
    form,
):
    """
    Create an assignment.
    """

    assignment = form.save(
        commit=False,
    )

    assignment.tenant = tenant

    _validate_tenant_scope(
        tenant=tenant,
        section=assignment.section,
        subject=assignment.subject,
        staff=assignment.staff,
    )

    assignment.full_clean()
    assignment.save()

    return assignment


# ============================================================================
# Update
# ============================================================================

@transaction.atomic
def update_assignment(
    *,
    assignment,
    form,
):
    """
    Update an assignment.
    """

    if assignment.tenant_id != form.tenant.pk:
        raise ValidationError(
            "The assignment does not belong to the current tenant."
        )

    assignment = form.save(
        commit=False,
    )

    assignment.tenant = form.tenant

    _validate_tenant_scope(
        tenant=form.tenant,
        section=assignment.section,
        subject=assignment.subject,
        staff=assignment.staff,
    )

    assignment.full_clean()
    assignment.save()

    return assignment


# ============================================================================
# Delete
# ============================================================================

@transaction.atomic
def delete_assignment(
    *,
    tenant,
    assignment,
):
    """
    Delete an assignment belonging to the current tenant.
    """

    if assignment.tenant_id != tenant.pk:
        raise ValidationError(
            "The assignment does not belong to the current tenant."
        )

    assignment.delete()