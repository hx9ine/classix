from django.db.models import Q
from django.shortcuts import get_object_or_404

from ..models import Subject


# ============================================================================
# Subject Selectors
# ============================================================================

def get_subjects(tenant):
    """
    Return all subjects for a tenant.
    """
    return (
        Subject.objects
        .filter(tenant=tenant)
        .order_by(
            "name",
            "code",
        )
    )


def get_subject(tenant, pk):
    """
    Return a single subject.
    """
    return get_object_or_404(
        Subject,
        tenant=tenant,
        pk=pk,
    )


def search_subjects(
    tenant,
    query,
):
    """
    Search subjects by name or code.
    """

    query = query.strip()

    if not query:
        return get_subjects(tenant)

    return (
        get_subjects(tenant)
        .filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
        )
    )


# ============================================================================
# Counts
# ============================================================================

def count_subjects(tenant):
    """
    Return total number of subjects.
    """
    return get_subjects(tenant).count()


# ============================================================================
# Exists
# ============================================================================

def subject_name_exists(
    tenant,
    name,
    *,
    exclude_pk=None,
):
    """
    Return whether a subject name already exists.
    """

    queryset = Subject.objects.filter(
        tenant=tenant,
        name__iexact=name.strip(),
    )

    if exclude_pk:
        queryset = queryset.exclude(
            pk=exclude_pk,
        )

    return queryset.exists()


def subject_code_exists(
    tenant,
    code,
    *,
    exclude_pk=None,
):
    """
    Return whether a subject code already exists.
    """

    queryset = Subject.objects.filter(
        tenant=tenant,
        code__iexact=code.strip(),
    )

    if exclude_pk:
        queryset = queryset.exclude(
            pk=exclude_pk,
        )

    return queryset.exists()