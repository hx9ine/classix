from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import EmploymentStatus
from ..selectors import staff_exists


# ============================================================================
# Staff Services
# ============================================================================

@transaction.atomic
def create_staff(*, tenant, form):
    """
    Create a staff member.
    """

    staff = form.save(commit=False)
    staff.tenant = tenant
    staff.save()

    return staff


@transaction.atomic
def update_staff(*, form):
    """
    Update a staff member.
    """

    return form.save()



# ============================================================================
# Staff Lifecycle
# ============================================================================

@transaction.atomic
def activate_staff(*, instance):
    """
    Activate a staff member.
    """

    if instance.employment_status == EmploymentStatus.ACTIVE:
        return instance

    instance.employment_status = EmploymentStatus.ACTIVE

    instance.save(
        update_fields=[
            "employment_status",
        ]
    )

    return instance


@transaction.atomic
def deactivate_staff(*, instance):
    """
    Deactivate a staff member.
    """

    if instance.employment_status == EmploymentStatus.INACTIVE:
        return instance

    instance.employment_status = EmploymentStatus.INACTIVE

    instance.save(
        update_fields=[
            "employment_status",
        ]
    )

    return instance


# ============================================================================
# User Assignment
# ============================================================================

@transaction.atomic
def assign_user(*, instance, user):
    """
    Link a portal user account to a staff member.
    """

    if staff_exists(user):
        raise ValidationError(
            "This user already has a staff profile."
        )

    instance.user = user

    instance.save(
        update_fields=[
            "user",
        ]
    )

    return instance


@transaction.atomic
def remove_user(*, instance):
    """
    Remove the linked portal user account.
    """

    instance.user = None

    instance.save(
        update_fields=[
            "user",
        ]
    )

    return instance