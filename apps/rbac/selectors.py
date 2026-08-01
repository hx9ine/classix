from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.tenants.models import Tenant

from .models import Role, RolePermission


def get_role(
    *,
    tenant: Tenant,
    role_id: UUID,
) -> Role | None:
    """
    Retrieve a tenant-specific role by ID.
    """
    return (
        Role.objects.filter(
            tenant=tenant,
            id=role_id,
        )
        .first()
    )


def get_role_by_name(
    *,
    tenant: Tenant,
    name: str,
) -> Role | None:
    """
    Retrieve a tenant-specific role by name.
    """
    return (
        Role.objects.filter(
            tenant=tenant,
            name=name,
        )
        .first()
    )


def get_system_role_by_name(
    *,
    name: str,
) -> Role | None:
    """
    Retrieve a system role template by name.
    """
    return (
        Role.objects.filter(
            tenant__isnull=True,
            name=name,
        )
        .first()
    )


def get_system_roles() -> QuerySet[Role]:
    """
    Return all system role templates.
    """
    return (
        Role.objects.filter(
            tenant__isnull=True,
        )
        .order_by("name")
    )


def get_tenant_roles(
    *,
    tenant: Tenant,
) -> QuerySet[Role]:
    """
    Return all roles belonging to a tenant.
    """
    return (
        Role.objects.filter(
            tenant=tenant,
        )
        .order_by("name")
    )


def get_role_permissions(
    *,
    role: Role,
) -> QuerySet[RolePermission]:
    """
    Return all permissions assigned to a role.
    """
    return (
        RolePermission.objects.filter(
            role=role,
        )
        .select_related("role")
        .order_by(
            "module",
            "action",
        )
    )


def has_permission(
    *,
    role: Role,
    module: RolePermission.Module,
    action: RolePermission.Action,
) -> bool:
    """
    Check whether a role has permission to perform an action.

    Admin roles bypass permission checks.
    """
    if role.is_admin_role:
        return True

    return RolePermission.objects.filter(
        role=role,
        module=module,
        action=action,
        allowed=True,
    ).exists()