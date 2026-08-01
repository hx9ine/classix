from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import Applicant


# ============================================================================
# Applicant Selectors
# ============================================================================

def get_applicants(*, tenant) -> QuerySet[Applicant]:
    """
    Return all applicants for the current tenant.
    """
    return (
        Applicant.objects
        .filter(tenant=tenant)
        .select_related("applying_for_class_level")
        .order_by(
            "first_name",
            "last_name",
        )
    )


def get_applicant(*, tenant, pk) -> Applicant:
    """
    Return a single applicant.
    """
    return get_object_or_404(
        Applicant,
        tenant=tenant,
        pk=pk,
    )


def get_applicants_by_status(
    *,
    tenant,
    status,
) -> QuerySet[Applicant]:
    """
    Return applicants by status.
    """
    return (
        Applicant.objects
        .filter(
            tenant=tenant,
            status=status,
        )
        .select_related("applying_for_class_level")
        .order_by(
            "first_name",
            "last_name",
        )
    )