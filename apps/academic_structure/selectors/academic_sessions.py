from django.shortcuts import get_object_or_404

from ..models import AcademicSession


# ============================================================================
# Academic Session Selectors
# ============================================================================

def get_academic_sessions(tenant):
    """
    Return all academic sessions for the tenant.
    """
    return (
        AcademicSession.objects
        .filter(tenant=tenant)
        .order_by("-start_date")
    )


def get_current_academic_session(tenant):
    """
    Return the current academic session for the tenant.
    """
    return (
        AcademicSession.objects
        .filter(
            tenant=tenant,
            is_current=True,
        )
        .first()
    )


def get_academic_session(tenant, pk):
    """
    Return a single academic session.
    """
    return get_object_or_404(
        AcademicSession,
        tenant=tenant,
        pk=pk,
    )



