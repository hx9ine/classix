from django.core.exceptions import ValidationError

from apps.rbac.models import Role
from apps.staff.models import EmploymentStatus

from ..selectors.licensing import (
    get_license_limits,
    get_license_status,
)


# ============================================================================
# License Categories
# ============================================================================

STUDENT_LICENSE = "student"


# ============================================================================
# License Errors
# ============================================================================

def _license_category_label(license_category):
    """
    Return the human-readable label for a license category.
    """

    if license_category == STUDENT_LICENSE:
        return "Student"

    return dict(
        Role.LicenseCategory.choices,
    )[license_category]


def _license_limit_message(
    *,
    license_category,
    limit,
):
    """
    Return the standard quota-exceeded message.
    """

    label = _license_category_label(
        license_category,
    )

    return (
        f"You've reached your {limit} {label} license limit — "
        "free one up or add more."
    )


# ============================================================================
# License Availability
# ============================================================================

def _ensure_license_available(
    *,
    tenant,
    license_category,
    additional_count=1,
):
    """
    Ensure that the requested number of additional active
    license consumers can be accommodated.

    This function does not modify any records.
    """

    limits = get_license_limits(
        tenant=tenant,
    )

    if license_category not in limits:
        raise ValidationError(
            "Invalid license category."
        )

    status = get_license_status(
        tenant=tenant,
    )[license_category]

    if (
        status["used"] + additional_count
        > status["limit"]
    ):
        raise ValidationError(
            _license_limit_message(
                license_category=license_category,
                limit=status["limit"],
            )
        )


def ensure_student_license_available(
    *,
    tenant,
):
    """
    Ensure that one additional active Student can be created/reactivated.
    """

    _ensure_license_available(
        tenant=tenant,
        license_category=STUDENT_LICENSE,
    )


def ensure_staff_license_available(
    *,
    tenant,
    role,
):
    """
    Ensure that one additional active Staff member can be created/reactivated
    under the supplied role.
    """

    if role is None:
        raise ValidationError(
            "A role is required to determine the staff license category."
        )

    if role.tenant_id not in (None, tenant.pk):
        raise ValidationError(
            "The selected role does not belong to the current tenant."
        )

    if role.license_category == Role.LicenseCategory.ADMIN:
        license_category = Role.LicenseCategory.ADMIN

    elif role.license_category == Role.LicenseCategory.FACULTY:
        license_category = Role.LicenseCategory.FACULTY

    elif role.license_category == Role.LicenseCategory.STAFF:
        license_category = Role.LicenseCategory.STAFF

    else:
        raise ValidationError(
            "The selected role has an invalid license category."
        )

    _ensure_license_available(
        tenant=tenant,
        license_category=license_category,
    )


def ensure_staff_role_change_available(
    *,
    tenant,
    staff,
    new_role,
):
    """
    Ensure that changing an active Staff member's role to a
    different license category is allowed.

    A role change within the same license category does not
    consume an additional license.
    """

    if staff.tenant_id != tenant.pk:
        raise ValidationError(
            "The staff member does not belong to the current tenant."
        )

    if new_role is None:
        raise ValidationError(
            "A role is required to determine the staff license category."
        )

    if new_role.tenant_id not in (None, tenant.pk):
        raise ValidationError(
            "The selected role does not belong to the current tenant."
        )

    old_category = staff.role.license_category
    new_category = new_role.license_category

    if old_category == new_category:
        return

    if staff.employment_status != EmploymentStatus.ACTIVE:
        return

    _ensure_license_available(
        tenant=tenant,
        license_category=new_category,
    )


# ============================================================================
# License Status
# ============================================================================

def get_current_license_status(*, tenant):
    """
    Return the current live license status for the tenant.
    """

    return get_license_status(
        tenant=tenant,
    )