from django.db.models import Q, QuerySet

from .models import EmploymentStatus, Staff


# ---------------------------------------------------------------------
# Base QuerySets
# ---------------------------------------------------------------------

def list_staff(tenant) -> QuerySet:
    """
    Base queryset for all staff in a tenant.
    """

    return (
        Staff.objects
        .filter(tenant=tenant)
        .select_related(
            "user",
            "role",
        )
        .order_by(
            "first_name",
            "last_name",
        )
    )


def list_active_staff(tenant) -> QuerySet:
    """
    Active staff.
    """

    return list_staff(tenant).filter(
        employment_status=EmploymentStatus.ACTIVE,
    )


def list_inactive_staff(tenant) -> QuerySet:
    """
    Inactive staff.
    """

    return list_staff(tenant).filter(
        employment_status=EmploymentStatus.INACTIVE,
    )


# ---------------------------------------------------------------------
# Single-object selectors
# ---------------------------------------------------------------------

def get_staff(staff_id, tenant):
    """
    Return a single staff member.

    Raises Staff.DoesNotExist if missing.
    """

    return list_staff(tenant).get(
        id=staff_id,
    )


def get_staff_by_user(user):
    """
    Return staff profile for a user.

    Raises Staff.DoesNotExist if missing.
    """

    return (
        Staff.objects
        .select_related(
            "role",
            "tenant",
        )
        .get(user=user)
    )


# ---------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------

def search_staff(tenant, query: str) -> QuerySet:
    """
    Search by name, phone or role.
    """

    query = query.strip()

    if not query:
        return list_staff(tenant)

    return (
        list_staff(tenant)
        .filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(staff_role_label__icontains=query)
        )
        .distinct()
    )


def list_staff_by_role(role) -> QuerySet:
    """
    Staff assigned to a role.
    """

    return (
        Staff.objects
        .filter(role=role)
        .select_related(
            "user",
            "role",
        )
        .order_by(
            "first_name",
            "last_name",
        )
    )


# ---------------------------------------------------------------------
# Counts
# ---------------------------------------------------------------------

def count_staff(tenant) -> int:
    return list_staff(tenant).count()


def count_active_staff(tenant) -> int:
    return list_active_staff(tenant).count()


def count_inactive_staff(tenant) -> int:
    return list_inactive_staff(tenant).count()


def count_active_staff_by_role(role) -> int:
    return (
        Staff.objects
        .filter(
            role=role,
            employment_status=EmploymentStatus.ACTIVE,
        )
        .count()
    )


# ---------------------------------------------------------------------
# Exists
# ---------------------------------------------------------------------

def staff_exists(user) -> bool:
    """
    Whether the user already has a staff profile.
    """

    return Staff.objects.filter(
        user=user,
    ).exists()