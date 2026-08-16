from apps.rbac.models import Role
from apps.staff.models import EmploymentStatus, Staff
from apps.students.models import Student, StudentStatus
from .license_addon import get_license_addon_quantities


# ============================================================================
# License Usage Selectors
# ============================================================================

def count_active_students(*, tenant):
    """
    Return the number of active students consuming Student licenses.

    Usage is computed live from Student records rather than stored separately.
    """

    return (
        Student._base_manager
        .filter(
            tenant=tenant,
            status=StudentStatus.ACTIVE,
        )
        .count()
    )


def count_active_staff_by_category(
    *,
    tenant,
    license_category,
):
    """
    Return the number of active staff consuming licenses
    in the requested license category.

    License category is derived from the Staff member's assigned Role.
    """

    return (
        Staff._base_manager
        .filter(
            tenant=tenant,
            employment_status=EmploymentStatus.ACTIVE,
            role__license_category=license_category,
        )
        .count()
    )


def count_active_admins(*, tenant):
    """
    Return the number of active Admin-license consumers.
    """

    return count_active_staff_by_category(
        tenant=tenant,
        license_category=Role.LicenseCategory.ADMIN,
    )


def count_active_faculty(*, tenant):
    """
    Return the number of active Faculty-license consumers.
    """

    return count_active_staff_by_category(
        tenant=tenant,
        license_category=Role.LicenseCategory.FACULTY,
    )


def count_active_staff(*, tenant):
    """
    Return the number of active Staff-license consumers.
    """

    return count_active_staff_by_category(
        tenant=tenant,
        license_category=Role.LicenseCategory.STAFF,
    )


def get_license_usage(*, tenant):
    """
    Return live license usage for all four license categories.

    Returns:
        dict:
            {
                "admin": int,
                "faculty": int,
                "staff": int,
                "student": int,
            }
    """

    return {
        Role.LicenseCategory.ADMIN: count_active_admins(
            tenant=tenant,
        ),
        Role.LicenseCategory.FACULTY: count_active_faculty(
            tenant=tenant,
        ),
        Role.LicenseCategory.STAFF: count_active_staff(
            tenant=tenant,
        ),
        "student": count_active_students(
            tenant=tenant,
        ),
    }


def get_license_limits(*, tenant):
    """
    Return the tenant's current license limits.

    Current limits consist of:
    - the tenant's base license allocation
    - all purchased license add-ons for that tenant

    Add-on quantities are calculated live from LicenseAddon records.
    """

    addon_quantities = get_license_addon_quantities(
        tenant=tenant,
    )

    return {
        Role.LicenseCategory.ADMIN: (
            tenant.admin_license_limit
            + addon_quantities[
                Role.LicenseCategory.ADMIN
            ]
        ),
        Role.LicenseCategory.FACULTY: (
            tenant.faculty_license_limit
            + addon_quantities[
                Role.LicenseCategory.FACULTY
            ]
        ),
        Role.LicenseCategory.STAFF: (
            tenant.staff_license_limit
            + addon_quantities[
                Role.LicenseCategory.STAFF
            ]
        ),
        "student": (
            tenant.student_license_limit
            + addon_quantities[
                "student"
            ]
        ),
    }


def get_license_status(*, tenant):
    """
    Return live usage together with the tenant's current limits.

    Usage is never persisted as a separate counter.
    """

    usage = get_license_usage(
        tenant=tenant,
    )

    limits = get_license_limits(
        tenant=tenant,
    )

    return {
        category: {
            "used": usage[category],
            "limit": limits[category],
            "available": max(
                limits[category] - usage[category],
                0,
            ),
            "at_capacity": (
                usage[category] >= limits[category]
            ),
        }
        for category in limits
    }