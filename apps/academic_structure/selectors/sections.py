from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import Section


# ============================================================================
# List
# ============================================================================

def get_sections(
    *,
    tenant,
) -> QuerySet[Section]:
    """
    Return all sections.
    """

    return (
        Section.objects
        .filter(
            tenant=tenant,
        )
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
    Return all sections for a class level.
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
        .order_by(
            "name",
        )
    )


# ============================================================================
# Retrieve
# ============================================================================

def get_section(
    *,
    tenant,
    pk,
) -> Section:
    """
    Return a single section.
    """

    return get_object_or_404(
        Section,
        tenant=tenant,
        pk=pk,
    )


# ============================================================================
# Exists
# ============================================================================

def section_exists(
    *,
    tenant,
    academic_session,
    class_level,
    name,
    exclude_pk=None,
) -> bool:
    """
    Return True if a section with the given name
    already exists for the academic session and
    class level.
    """

    queryset = Section.objects.filter(
        tenant=tenant,
        academic_session=academic_session,
        class_level=class_level,
        name=name,
    )

    if exclude_pk:

        queryset = queryset.exclude(
            pk=exclude_pk,
        )

    return queryset.exists()