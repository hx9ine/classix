from django.core.exceptions import ValidationError
from django.db import transaction

from apps.rbac.models import Role

from .models import EmploymentStatus, Staff
from .selectors import (
    get_staff,
    staff_exists,
)


# ============================================================
# Private Helpers
# ============================================================

def _validate_role(role: Role, tenant):
    """
    Ensure the role belongs to the current tenant or is
    a system role.
    """

    if role.tenant is None:
        return

    if role.tenant != tenant:
        raise ValidationError(
            "Selected role does not belong to this tenant."
        )


def _sync_role_label(staff: Staff):
    """
    Keep denormalized role label synchronized.
    """

    staff.staff_role_label = staff.role.name


# ============================================================
# Create
# ============================================================

@transaction.atomic
def create_staff(
    *,
    tenant,
    first_name,
    last_name,
    role,
    joining_date,
    phone="",
    photo=None,
    user=None,
):
    """
    Create a staff member.
    """

    if user and staff_exists(user):
        raise ValidationError(
            "This user already has a staff profile."
        )

    _validate_role(role, tenant)

    staff = Staff(
        tenant=tenant,
        user=user,
        first_name=first_name,
        last_name=last_name,
        role=role,
        joining_date=joining_date,
        phone=phone,
        photo=photo,
        employment_status=EmploymentStatus.ACTIVE,
    )

    _sync_role_label(staff)

    staff.full_clean()
    staff.save()

    # Future:
    # licensing.consume_license(staff)

    return staff


# ============================================================
# Update
# ============================================================

@transaction.atomic
def update_staff(
    *,
    staff,
    first_name,
    last_name,
    role,
    joining_date,
    phone,
    photo,
):
    """
    Update a staff profile.
    """

    _validate_role(role, staff.tenant)

    role_changed = staff.role_id != role.id

    staff.first_name = first_name
    staff.last_name = last_name
    staff.role = role
    staff.joining_date = joining_date
    staff.phone = phone

    if photo is not None:
        staff.photo = photo

    if role_changed:
        _sync_role_label(staff)

        # Future:
        # licensing.move_license(
        #     old_role,
        #     new_role,
        # )

    staff.full_clean()
    staff.save()

    return staff


# ============================================================
# Activation
# ============================================================

@transaction.atomic
def activate_staff(staff):
    """
    Reactivate staff.
    """

    if staff.employment_status == EmploymentStatus.ACTIVE:
        return staff

    # Future:
    # licensing.consume_license(staff)

    staff.employment_status = EmploymentStatus.ACTIVE

    staff.save(
        update_fields=[
            "employment_status",
            "updated_at",
        ]
    )

    return staff


@transaction.atomic
def deactivate_staff(staff):
    """
    Deactivate staff.
    """

    if staff.employment_status == EmploymentStatus.INACTIVE:
        return staff

    staff.employment_status = EmploymentStatus.INACTIVE

    staff.save(
        update_fields=[
            "employment_status",
            "updated_at",
        ]
    )

    # Future:
    # licensing.release_license(staff)

    return staff


# ============================================================
# User Assignment
# ============================================================

@transaction.atomic
def assign_user(
    *,
    staff,
    user,
):
    """
    Link a Django user account to staff.
    """

    if staff_exists(user):
        raise ValidationError(
            "This user already belongs to another staff profile."
        )

    staff.user = user

    staff.full_clean()

    staff.save(
        update_fields=[
            "user",
            "updated_at",
        ]
    )

    return staff


@transaction.atomic
def remove_user(staff):
    """
    Unlink login account.
    """

    staff.user = None

    staff.save(
        update_fields=[
            "user",
            "updated_at",
        ]
    )

    return staff