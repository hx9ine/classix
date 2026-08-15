from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import GradeEntry


# ============================================================================
# List
# ============================================================================

def get_grade_entries(
    *,
    tenant,
) -> QuerySet[GradeEntry]:
    """
    Return all grade entries for a tenant.
    """

    return (
        GradeEntry.objects
        .filter(
            tenant=tenant,
        )
        .select_related(
            "student",
            "exam",
            "subject",
        )
        .order_by(
            "exam__start_date",
            "subject__name",
            "student__first_name",
            "student__last_name",
        )
    )


# ============================================================================
# Retrieve
# ============================================================================

def get_grade_entry(
    *,
    tenant,
    pk,
) -> GradeEntry:
    """
    Return a single grade entry for a tenant.
    """

    return get_object_or_404(
        GradeEntry.objects.select_related(
            "student",
            "exam",
            "subject",
        ),
        tenant=tenant,
        pk=pk,
    )


# ============================================================================
# Filters
# ============================================================================

def get_grade_entries_by_exam(
    *,
    tenant,
    exam,
) -> QuerySet[GradeEntry]:
    """
    Return grade entries for an exam within a tenant.
    """

    return (
        GradeEntry.objects
        .filter(
            tenant=tenant,
            exam=exam,
        )
        .select_related(
            "student",
            "subject",
        )
        .order_by(
            "subject__name",
            "student__first_name",
            "student__last_name",
        )
    )


def get_grade_entries_by_student(
    *,
    tenant,
    student,
) -> QuerySet[GradeEntry]:
    """
    Return grade entries for a student within a tenant.
    """

    return (
        GradeEntry.objects
        .filter(
            tenant=tenant,
            student=student,
        )
        .select_related(
            "exam",
            "subject",
        )
        .order_by(
            "-exam__start_date",
            "subject__name",
        )
    )