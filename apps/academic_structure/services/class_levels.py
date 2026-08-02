from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import ClassLevel
from ..selectors import (
    class_level_name_exists,
)


# ============================================================================
# Create
# ============================================================================

@transaction.atomic
def create_class_level(
    *,
    tenant,
    name,
    sort_order,
):
    """
    Create a class level.
    """

    name = name.strip()

    if class_level_name_exists(
        tenant=tenant,
        name=name,
    ):
        raise ValidationError(
            "A class level with this name already exists."
        )

    class_level = ClassLevel(
        tenant=tenant,
        name=name,
        sort_order=sort_order,
    )

    class_level.full_clean()
    class_level.save()

    return class_level


# ============================================================================
# Update
# ============================================================================

@transaction.atomic
def update_class_level(
    *,
    class_level,
    name,
    sort_order,
):
    """
    Update a class level.
    """

    name = name.strip()

    if class_level_name_exists(
        tenant=class_level.tenant,
        name=name,
        exclude_pk=class_level.pk,
    ):
        raise ValidationError(
            "A class level with this name already exists."
        )

    class_level.name = name
    class_level.sort_order = sort_order

    class_level.full_clean()
    class_level.save()

    return class_level


# ============================================================================
# Delete
# ============================================================================

@transaction.atomic
def delete_class_level(
    *,
    class_level,
):
    """
    Delete a class level.

    NOTE:
    Once Sections, Students and Timetables
    depend on Class Levels, this should
    become a soft delete or include
    dependency checks.
    """

    class_level.delete()