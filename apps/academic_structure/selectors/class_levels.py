from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import ClassLevel


# ============================================================================
# Class Level Selectors
# ============================================================================

def get_class_levels(*, tenant) -> QuerySet[ClassLevel]:
    """
    Return all class levels ordered by sort order.
    """
    return (
        ClassLevel.objects
        .filter(tenant=tenant)
        .order_by("sort_order", "name")
    )


def get_class_level(*, tenant, pk) -> ClassLevel:
    """
    Return a single class level.
    """
    return get_object_or_404(
        ClassLevel,
        tenant=tenant,
        pk=pk,
    )