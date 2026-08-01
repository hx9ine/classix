from django.shortcuts import get_object_or_404

from .models import (
    Role,
    RolePermission,
)


# ============================================================================
# Role Selectors
# ============================================================================

def get_roles(tenant):
    """
    Return all roles available to a tenant.

    Includes:
    - System role templates
    - Tenant-specific roles
    """

    return (
        Role.objects
        .filter(
            tenant__in=[tenant, None],
        )
        .order_by("name")
    )


def get_tenant_roles(tenant):
    """
    Return only tenant-owned roles.
    """

    return (
        Role.objects
        .filter(
            tenant=tenant,
        )
        .order_by("name")
    )


def get_system_roles():
    """
    Return all system role templates.
    """

    return (
        Role.objects
        .filter(
            tenant__isnull=True,
        )
        .order_by("name")
    )


def get_role(tenant, pk):
    """
    Return a single role available to the tenant.
    """

    return get_object_or_404(
        Role,
        pk=pk,
        tenant__in=[tenant, None],
    )


def get_role_by_name(
    *,
    tenant,
    name,
):
    """
    Return a tenant-owned role by name.
    """

    return (
        Role.objects
        .filter(
            tenant=tenant,
            name=name,
        )
        .first()
    )


def get_system_role_by_name(name):
    """
    Return a system role template by name.
    """

    return (
        Role.objects
        .filter(
            tenant__isnull=True,
            name=name,
        )
        .first()
    )


# ============================================================================
# Permission Selectors
# ============================================================================

def get_role_permissions(role):
    """
    Return permissions assigned to a role.
    """

    return (
        RolePermission.objects
        .filter(
            role=role,
        )
        .order_by(
            "module",
            "action",
        )
    )


def has_permission(
    *,
    role,
    module,
    action,
):
    """
    Check whether a role has a permission.

    Admin roles bypass permission checks.
    """

    if role.is_admin_role:
        return True

    return (
        RolePermission.objects
        .filter(
            role=role,
            module=module,
            action=action,
            allowed=True,
        )
        .exists()
    )