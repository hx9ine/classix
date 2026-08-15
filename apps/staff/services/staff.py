from django.core.exceptions import ValidationError
from django.db import transaction

from apps.billing.services.licensing import (
    ensure_staff_license_available,
    ensure_staff_role_change_available,
)

from ..models import EmploymentStatus, Staff
from ..selectors import staff_exists


# ============================================================================
# Staff Services
# ============================================================================

@transaction.atomic
def create_staff(*, tenant, form):
    """
    Create a staff member.

    Active staff consume a license from the category represented
    by their assigned role.
    """

    staff = form.save(
        commit=False,
    )

    staff.tenant = tenant

    if staff.employment_status == EmploymentStatus.ACTIVE:
        ensure_staff_license_available(
            tenant=tenant,
            role=staff.role,
        )

    staff.save()

    return staff


@transaction.atomic
def update_staff(*, form):
    """
    Update a staff member.

    If an active staff member is moved to a different license
    category, the destination category must have capacity.

    The persisted database state is used to determine the
    staff member's original role because ModelForm validation
    may already have mutated form.instance.
    """

    staff = form.instance
    tenant = form.tenant

    if staff.tenant_id != tenant.pk:
        raise ValidationError(
            "The staff member does not belong to the current tenant."
        )

    persisted_staff = (
        Staff._base_manager
        .select_related("role")
        .get(
            pk=staff.pk,
            tenant=tenant,
        )
    )

    new_role = form.cleaned_data["role"]

    if (
        persisted_staff.employment_status
        == EmploymentStatus.ACTIVE
    ):
        ensure_staff_role_change_available(
            tenant=tenant,
            staff=persisted_staff,
            new_role=new_role,
        )

    return form.save()


# ============================================================================
# Staff Lifecycle
# ============================================================================

@transaction.atomic
def activate_staff(*, instance):
    """
    Activate a staff member.

    Activation consumes a license from the category represented
    by the staff member's current role.
    """

    if instance.employment_status == EmploymentStatus.ACTIVE:
        return instance

    ensure_staff_license_available(
        tenant=instance.tenant,
        role=instance.role,
    )

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

    Inactive staff do not consume a license.
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