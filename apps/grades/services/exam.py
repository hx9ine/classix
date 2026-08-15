from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import Exam


# ============================================================================
# Validation
# ============================================================================

def _validate_tenant_scope(
    *,
    tenant,
    academic_session,
):
    """
    Ensure the academic session belongs to the current tenant.
    """

    if academic_session.tenant_id != tenant.pk:
        raise ValidationError(
            "The selected academic session does not belong to the current tenant."
        )


# ============================================================================
# Create
# ============================================================================

@transaction.atomic
def create_exam(
    *,
    tenant,
    form,
):
    """
    Create an exam.
    """

    exam = form.save(
        commit=False,
    )

    exam.tenant = tenant

    _validate_tenant_scope(
        tenant=tenant,
        academic_session=exam.academic_session,
    )

    exam.full_clean()
    exam.save()

    return exam


# ============================================================================
# Update
# ============================================================================

@transaction.atomic
def update_exam(
    *,
    exam,
    form,
):
    """
    Update an exam.
    """

    if exam.tenant_id != form.tenant.pk:
        raise ValidationError(
            "The exam does not belong to the current tenant."
        )

    exam = form.save(
        commit=False,
    )

    exam.tenant = form.tenant

    _validate_tenant_scope(
        tenant=form.tenant,
        academic_session=exam.academic_session,
    )

    exam.full_clean()
    exam.save()

    return exam


# ============================================================================
# Delete
# ============================================================================

@transaction.atomic
def delete_exam(
    *,
    tenant,
    exam,
):
    """
    Delete an exam.
    """

    if exam.tenant_id != tenant.pk:
        raise ValidationError(
            "The exam does not belong to the current tenant."
        )

    exam.delete()