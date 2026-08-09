from django.db.models import Q
from django.shortcuts import get_object_or_404

from ..models import (
    EmploymentStatus,
    Staff,
)


# ============================================================================
# Staff Selectors
# ============================================================================

def get_staff_members(tenant):
    """
    Return all staff for a tenant.
    """
    return (
        Staff.objects
        .filter(
            tenant=tenant,
        )
        .select_related(
            "user",
            "role",
        )
        .order_by(
            "first_name",
            "last_name",
        )
    )


def get_active_staff(tenant):
    """
    Return active staff.
    """
    return get_staff_members(
        tenant,
    ).filter(
        employment_status=EmploymentStatus.ACTIVE,
    )


def get_inactive_staff(tenant):
    """
    Return inactive staff.
    """
    return get_staff_members(
        tenant,
    ).filter(
        employment_status=EmploymentStatus.INACTIVE,
    )


def get_staff(tenant, pk):
    """
    Return a single staff member.
    """
    return get_object_or_404(
        Staff.objects.select_related(
            "user",
            "role",
        ),
        tenant=tenant,
        pk=pk,
    )


def get_staff_by_user(user):
    """
    Return the staff profile for a user.
    """
    return (
        Staff.objects
        .select_related(
            "tenant",
            "role",
        )
        .get(
            user=user,
        )
    )


def get_staff_by_role(tenant, role):
    """
    Return staff assigned to a role.
    """
    return (
        Staff.objects
        .filter(
            tenant=tenant,
            role=role,
        )
        .select_related(
            "user",
            "role",
        )
        .order_by(
            "first_name",
            "last_name",
        )
    )


def search_staff(tenant, query):
    """
    Search staff by name, phone or role.
    """
    query = query.strip()

    if not query:
        return get_staff_members(
            tenant,
        )

    return (
        get_staff_members(
            tenant,
        )
        .filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(role__name__icontains=query)
        )
        .distinct()
    )


# ============================================================================
# Counts
# ============================================================================

def count_staff(tenant):
    return get_staff_members(
        tenant,
    ).count()


def count_active_staff(tenant):
    return get_active_staff(
        tenant,
    ).count()


def count_inactive_staff(tenant):
    return get_inactive_staff(
        tenant,
    ).count()


def count_active_staff_by_role(tenant, role):
    return (
        Staff.objects
        .filter(
            tenant=tenant,
            role=role,
            employment_status=EmploymentStatus.ACTIVE,
        )
        .count()
    )


# ============================================================================
# Exists
# ============================================================================

def staff_exists(user):
    """
    Return whether a user already has a staff profile.
    """
    return Staff.objects.filter(
        user=user,
    ).exists()