from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import AcademicSession


# ============================================================================
# List
# ============================================================================

def get_academic_sessions(
    *,
    tenant,
) -> QuerySet[AcademicSession]:
    """
    Return all academic sessions.
    """

    return (
        AcademicSession.objects
        .filter(
            tenant=tenant,
        )
        .order_by(
            "-start_date",
        )
    )


# ============================================================================
# Current
# ============================================================================

def get_current_academic_session(
    *,
    tenant,
) -> AcademicSession | None:
    """
    Return the current academic session.
    """

    return (
        AcademicSession.objects
        .filter(
            tenant=tenant,
            is_current=True,
        )
        .first()
    )


# ============================================================================
# Retrieve
# ============================================================================

def get_academic_session(
    *,
    tenant,
    pk,
) -> AcademicSession:
    """
    Return a single academic session.
    """

    return get_object_or_404(
        AcademicSession,
        tenant=tenant,
        pk=pk,
    )


# ============================================================================
# Exists
# ============================================================================

def academic_session_name_exists(
    *,
    tenant,
    name,
    exclude_pk=None,
) -> bool:
    """
    Return True if an academic session with the given
    name already exists for the tenant.
    """

    queryset = AcademicSession.objects.filter(
        tenant=tenant,
        name=name,
    )

    if exclude_pk:

        queryset = queryset.exclude(
            pk=exclude_pk,
        )

    return queryset.exists()