from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import Section
from ..selectors import (
    section_exists,
)


# ============================================================================
# Create
# ============================================================================

@transaction.atomic
def create_section(
    *,
    tenant,
    academic_session,
    class_level,
    name,
):
    """
    Create a section.
    """

    name = name.strip().upper()

    if section_exists(
        tenant=tenant,
        academic_session=academic_session,
        class_level=class_level,
        name=name,
    ):
        raise ValidationError(
            "A section with this name already exists for the selected class level and academic session."
        )

    section = Section(
        tenant=tenant,
        academic_session=academic_session,
        class_level=class_level,
        name=name,
    )

    section.full_clean()
    section.save()

    return section


# ============================================================================
# Update
# ============================================================================

@transaction.atomic
def update_section(
    *,
    section,
    academic_session,
    class_level,
    name,
):
    """
    Update a section.
    """

    name = name.strip().upper()

    if section_exists(
        tenant=section.tenant,
        academic_session=academic_session,
        class_level=class_level,
        name=name,
        exclude_pk=section.pk,
    ):
        raise ValidationError(
            "A section with this name already exists for the selected class level and academic session."
        )

    section.academic_session = academic_session
    section.class_level = class_level
    section.name = name

    section.full_clean()
    section.save()

    return section


# ============================================================================
# Delete
# ============================================================================

@transaction.atomic
def delete_section(
    *,
    section,
):
    """
    Delete a section.

    NOTE:
    Once Students, Attendance, Timetables and
    Grades reference sections, this should
    become a soft delete or include dependency
    checks.
    """

    section.delete()