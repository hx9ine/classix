from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import Assignment


# ============================================================================
# List
# ============================================================================

def get_assignments(
    *,
    tenant,
) -> QuerySet[Assignment]:
    """
    Return all assignments for a tenant.
    """

    return (
        Assignment.objects
        .filter(
            tenant=tenant,
        )
        .select_related(
            "section",
            "section__academic_session",
            "section__class_level",
            "subject",
            "staff",
        )
        .order_by(
            "-due_date",
            "title",
        )
    )


def get_assignments_by_staff(
    *,
    tenant,
    staff,
) -> QuerySet[Assignment]:
    """
    Return assignments created by a staff member.
    """

    return (
        get_assignments(
            tenant=tenant,
        )
        .filter(
            staff=staff,
        )
        .order_by(
            "-due_date",
            "title",
        )
    )


def get_assignments_by_section(
    *,
    tenant,
    section,
) -> QuerySet[Assignment]:
    """
    Return assignments for a section.
    """

    return (
        get_assignments(
            tenant=tenant,
        )
        .filter(
            section=section,
        )
        .order_by(
            "-due_date",
            "title",
        )
    )


# ============================================================================
# Retrieve
# ============================================================================

def get_assignment(
    *,
    tenant,
    pk,
) -> Assignment:
    """
    Return a single assignment for a tenant.
    """

    return get_object_or_404(
        Assignment.objects.select_related(
            "section",
            "section__academic_session",
            "section__class_level",
            "subject",
            "staff",
        ),
        tenant=tenant,
        pk=pk,
    )


# ============================================================================
# Submissions
# ============================================================================

def get_assignment_submissions(
    *,
    tenant,
    assignment,
):
    """
    Return submissions for an assignment.

    The assignment itself is tenant-scoped before its submissions
    are queried.
    """

    if assignment.tenant_id != tenant.pk:
        return assignment.submissions.none()

    return (
        assignment.submissions
        .select_related(
            "student",
        )
        .order_by(
            "student__student_code",
        )
    )