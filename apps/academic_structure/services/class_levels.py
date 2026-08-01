from django.db import transaction

from ..models import ClassLevel


# ============================================================================
# Class Level Services
# ============================================================================

@transaction.atomic
def create_class_level(*, tenant, form) -> ClassLevel:
    """
    Create a new class level.
    """
    class_level = form.save(commit=False)
    class_level.tenant = tenant
    class_level.save()

    return class_level


@transaction.atomic
def update_class_level(*, form) -> ClassLevel:
    """
    Update an existing class level.
    """
    return form.save()


@transaction.atomic
def delete_class_level(*, instance) -> None:
    """
    Delete a class level.
    """
    instance.delete()