from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import AcademicSession
from ..selectors import (
    academic_session_name_exists,
)


# ============================================================================
# Create
# ============================================================================

@transaction.atomic
def create_academic_session(
    *,
    tenant,
    name,
    start_date,
    end_date,
    is_current,
):
    """
    Create an academic session.
    """

    name = name.strip()

    if academic_session_name_exists(
        tenant=tenant,
        name=name,
    ):
        raise ValidationError(
            "An academic session with this name already exists."
        )

    if end_date <= start_date:
        raise ValidationError(
            "End date must be after the start date."
        )

    if is_current:

        AcademicSession.objects.filter(
            tenant=tenant,
            is_current=True,
        ).update(
            is_current=False,
        )

    academic_session = AcademicSession(
        tenant=tenant,
        name=name,
        start_date=start_date,
        end_date=end_date,
        is_current=is_current,
    )

    academic_session.full_clean()
    academic_session.save()

    return academic_session


# ============================================================================
# Update
# ============================================================================

@transaction.atomic
def update_academic_session(
    *,
    academic_session,
    name,
    start_date,
    end_date,
    is_current,
):
    """
    Update an academic session.
    """

    name = name.strip()

    if academic_session_name_exists(
        tenant=academic_session.tenant,
        name=name,
        exclude_pk=academic_session.pk,
    ):
        raise ValidationError(
            "An academic session with this name already exists."
        )

    if end_date <= start_date:
        raise ValidationError(
            "End date must be after the start date."
        )

    if is_current:

        AcademicSession.objects.filter(
            tenant=academic_session.tenant,
            is_current=True,
        ).exclude(
            pk=academic_session.pk,
        ).update(
            is_current=False,
        )

    academic_session.name = name
    academic_session.start_date = start_date
    academic_session.end_date = end_date
    academic_session.is_current = is_current

    academic_session.full_clean()
    academic_session.save()

    return academic_session


# ============================================================================
# Delete
# ============================================================================

@transaction.atomic
def delete_academic_session(
    *,
    academic_session,
):
    """
    Delete an academic session.

    NOTE:
    Once Attendance, Exams, Grades and
    Student Enrollment depend on academic
    sessions, this should become a soft
    delete or include dependency checks.
    """

    academic_session.delete()


# ============================================================================
# Current Session
# ============================================================================

@transaction.atomic
def set_current_academic_session(
    *,
    tenant,
    academic_session,
):
    """
    Mark an academic session as the current session.
    """

    AcademicSession.objects.filter(
        tenant=tenant,
        is_current=True,
    ).update(
        is_current=False,
    )

    academic_session.is_current = True
    academic_session.save(
        update_fields=[
            "is_current",
        ],
    )

    return academic_session