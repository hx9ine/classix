from django.db import transaction

from ..models import Section


# ============================================================================
# Section Services
# ============================================================================

@transaction.atomic
def create_section(*, tenant, form) -> Section:
    """
    Create a section.
    """
    section = form.save(commit=False)
    section.tenant = tenant
    section.save()

    return section


@transaction.atomic
def update_section(*, form) -> Section:
    """
    Update a section.
    """
    return form.save()


@transaction.atomic
def delete_section(*, instance) -> None:
    """
    Delete a section.
    """
    instance.delete()