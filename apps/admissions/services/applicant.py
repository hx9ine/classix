from django.db import transaction

from ..models import Applicant


# ============================================================================
# Applicant Services
# ============================================================================

@transaction.atomic
def create_applicant(
    *,
    tenant,
    form,
) -> Applicant:
    """
    Create a new applicant.
    """

    applicant = form.save(
        commit=False,
    )

    applicant.tenant = tenant
    applicant.save()

    return applicant


@transaction.atomic
def update_applicant(
    *,
    form,
) -> Applicant:
    """
    Update an existing applicant.
    """

    return form.save()


@transaction.atomic
def delete_applicant(
    *,
    instance,
) -> None:
    """
    Delete an applicant.
    """

    instance.delete()