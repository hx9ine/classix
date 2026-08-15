from django.core.exceptions import ValidationError
from django.db import transaction

from apps.academics.models import TimetablePeriod

from ..models import GradeEntry


# ============================================================================
# Validation
# ============================================================================

def _validate_tenant_scope(
    *,
    tenant,
    student,
    exam,
    subject,
):
    """
    Ensure all tenant-owned objects belong to the current tenant.
    """

    objects = [
        ("student", student),
        ("exam", exam),
        ("subject", subject),
    ]

    for name, obj in objects:

        if obj.tenant_id != tenant.pk:
            raise ValidationError(
                f"The selected {name} does not belong to the current tenant."
            )


def _validate_teacher_scope(
    *,
    tenant,
    staff,
    student,
    subject,
):
    """
    Ensure a teacher can only create or update grades for a
    section/subject combination assigned to that teacher.
    """

    if staff is None:
        return

    has_assignment = (
        TimetablePeriod.objects
        .filter(
            tenant=tenant,
            staff=staff,
            section_id=student.section_id,
            subject=subject,
        )
        .exists()
    )

    if not has_assignment:
        raise ValidationError(
            "You can only manage grades for your assigned "
            "sections and subjects."
        )


# ============================================================================
# Create
# ============================================================================

@transaction.atomic
def create_grade_entry(
    *,
    tenant,
    form,
    staff=None,
):
    """
    Create a grade entry.

    When staff is supplied, the teacher's timetable scope is
    enforced in addition to tenant validation.
    """

    grade_entry = form.save(
        commit=False,
    )

    grade_entry.tenant = tenant

    _validate_tenant_scope(
        tenant=tenant,
        student=grade_entry.student,
        exam=grade_entry.exam,
        subject=grade_entry.subject,
    )

    _validate_teacher_scope(
        tenant=tenant,
        staff=staff,
        student=grade_entry.student,
        subject=grade_entry.subject,
    )

    grade_entry.full_clean()
    grade_entry.save()

    return grade_entry


# ============================================================================
# Update
# ============================================================================

@transaction.atomic
def update_grade_entry(
    *,
    grade_entry,
    form,
    staff=None,
):
    """
    Update a grade entry.

    When staff is supplied, the teacher's timetable scope is
    enforced against the resulting student/subject combination.
    """

    if grade_entry.tenant_id != form.tenant.pk:
        raise ValidationError(
            "The grade entry does not belong to the current tenant."
        )

    grade_entry = form.save(
        commit=False,
    )

    grade_entry.tenant = form.tenant

    _validate_tenant_scope(
        tenant=form.tenant,
        student=grade_entry.student,
        exam=grade_entry.exam,
        subject=grade_entry.subject,
    )

    _validate_teacher_scope(
        tenant=form.tenant,
        staff=staff,
        student=grade_entry.student,
        subject=grade_entry.subject,
    )

    grade_entry.full_clean()
    grade_entry.save()

    return grade_entry