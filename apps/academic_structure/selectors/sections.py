from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import Section


# ============================================================================
# Section Selectors
# ============================================================================

def get_sections(*, tenant) -> QuerySet[Section]:
    """
    Return all sections with related objects.
    """
    return (
        Section.objects
        .filter(tenant=tenant)
        .select_related(
            "academic_session",
            "class_level",
        )
        .order_by(
            "class_level__sort_order",
            "name",
        )
    )


def get_sections_by_class(
    *,
    tenant,
    class_level,
) -> QuerySet[Section]:
    """
    Return sections belonging to a class level.
    """
    return (
        Section.objects
        .filter(
            tenant=tenant,
            class_level=class_level,
        )
        .select_related(
            "academic_session",
            "class_level",
        )
        .order_by("name")
    )


def get_section(*, tenant, pk) -> Section:
    """
    Return a single section.
    """
    return get_object_or_404(
        Section,
        tenant=tenant,
        pk=pk,
    )