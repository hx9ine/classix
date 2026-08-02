from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import ClassLevel


# ============================================================================
# List
# ============================================================================

def get_class_levels(
    *,
    tenant,
) -> QuerySet[ClassLevel]:
    """
    Return all class levels.
    """

    return (
        ClassLevel.objects
        .filter(
            tenant=tenant,
        )
        .order_by(
            "sort_order",
            "name",
        )
    )


# ============================================================================
# Retrieve
# ============================================================================

def get_class_level(
    *,
    tenant,
    pk,
) -> ClassLevel:
    """
    Return a single class level.
    """

    return get_object_or_404(
        ClassLevel,
        tenant=tenant,
        pk=pk,
    )


# ============================================================================
# Exists
# ============================================================================

def class_level_name_exists(
    *,
    tenant,
    name,
    exclude_pk=None,
) -> bool:
    """
    Return True if a class level with the given
    name already exists for the tenant.
    """

    queryset = ClassLevel.objects.filter(
        tenant=tenant,
        name=name,
    )

    if exclude_pk:

        queryset = queryset.exclude(
            pk=exclude_pk,
        )

    return queryset.exists()