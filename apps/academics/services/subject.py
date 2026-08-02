from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import Subject
from ..selectors import (
    get_subject,
    subject_code_exists,
    subject_name_exists,
)


# ============================================================================
# Create
# ============================================================================

@transaction.atomic
def create_subject(
    *,
    tenant,
    name,
    code,
):
    """
    Create a subject.
    """

    name = name.strip()
    code = code.strip().upper()

    if subject_name_exists(
        tenant,
        name,
    ):
        raise ValidationError(
            "A subject with this name already exists."
        )

    if subject_code_exists(
        tenant,
        code,
    ):
        raise ValidationError(
            "A subject with this code already exists."
        )

    subject = Subject(
        tenant=tenant,
        name=name,
        code=code,
    )

    subject.full_clean()
    subject.save()

    return subject


# ============================================================================
# Update
# ============================================================================

@transaction.atomic
def update_subject(
    *,
    subject,
    name,
    code,
):
    """
    Update a subject.
    """

    name = name.strip()
    code = code.strip().upper()

    if subject_name_exists(
        subject.tenant,
        name,
        exclude_pk=subject.pk,
    ):
        raise ValidationError(
            "A subject with this name already exists."
        )

    if subject_code_exists(
        subject.tenant,
        code,
        exclude_pk=subject.pk,
    ):
        raise ValidationError(
            "A subject with this code already exists."
        )

    subject.name = name
    subject.code = code

    subject.full_clean()
    subject.save()

    return subject


# ============================================================================
# Delete
# ============================================================================

@transaction.atomic
def delete_subject(
    *,
    subject,
):
    """
    Delete a subject.

    NOTE:
    Once Timetable, Homework, Exams and Grades are
    implemented, this should become a soft delete
    or include dependency checks.
    """

    subject.delete()