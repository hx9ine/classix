from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import Exam


# ============================================================================
# List
# ============================================================================

def get_exams(
    *,
    tenant,
) -> QuerySet[Exam]:
    """
    Return all exams for a tenant.
    """

    return (
        Exam.objects
        .filter(
            tenant=tenant,
        )
        .select_related(
            "academic_session",
        )
        .order_by(
            "-start_date",
            "name",
        )
    )


# ============================================================================
# Retrieve
# ============================================================================

def get_exam(
    *,
    tenant,
    pk,
) -> Exam:
    """
    Return a single exam for a tenant.
    """

    return get_object_or_404(
        Exam.objects.select_related(
            "academic_session",
        ),
        tenant=tenant,
        pk=pk,
    )