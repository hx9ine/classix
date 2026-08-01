from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.tenants.models import Tenant

from .models import Role, RolePermission
from .selectors import (
    get_role_by_name,
    get_system_roles,
    get_tenant_roles,
)


class RoleService:
    """
    Service layer for Role management.
    """

    @staticmethod
    def create_role(
        *,
        tenant: Tenant,
        name: str,
        license_category: Role.LicenseCategory,
        is_admin_role: bool = False,
        is_editable: bool = True,
    ) -> Role:
        """
        Create a new tenant-specific role.
        """

        if get_role_by_name(
            tenant=tenant,
            name=name,
        ):
            raise ValidationError(
                f'Role "{name}" already exists.'
            )

        return Role.objects.create(
            tenant=tenant,
            name=name,
            license_category=license_category,
            is_admin_role=is_admin_role,
            is_editable=is_editable,
        )

    @staticmethod
    def update_role(
        *,
        role: Role,
        name: str,
    ) -> Role:
        """
        Rename an existing tenant role.
        """

        if role.tenant is None:
            raise ValidationError(
                "System roles cannot be modified."
            )

        if not role.is_editable:
            raise ValidationError(
                "This role cannot be modified."
            )

        existing_role = get_role_by_name(
            tenant=role.tenant,
            name=name,
        )

        if existing_role and existing_role.id != role.id:
            raise ValidationError(
                f'Role "{name}" already exists.'
            )

        role.name = name
        role.save(update_fields=["name", "updated_at"])

        return role

    @staticmethod
    @transaction.atomic
    def clone_system_roles(
        *,
        tenant: Tenant,
    ) -> None:
        """
        Clone all system roles and their permissions for a tenant.
        """

        if get_tenant_roles(
            tenant=tenant,
        ).exists():
            raise ValidationError(
                "Roles have already been initialized for this tenant."
            )

        for system_role in get_system_roles():

            cloned_role = Role.objects.create(
                tenant=tenant,
                name=system_role.name,
                license_category=system_role.license_category,
                is_admin_role=system_role.is_admin_role,
                is_editable=system_role.is_editable,
                cloned_from_role=system_role,
            )

            RoleService._clone_role_permissions(
                source_role=system_role,
                target_role=cloned_role,
            )

    @staticmethod
    def _clone_role_permissions(
        *,
        source_role: Role,
        target_role: Role,
    ) -> None:
        """
        Clone all permissions from one role to another.
        """

        permissions = RolePermission.objects.filter(
            role=source_role,
        )

        RolePermission.objects.bulk_create(
            [
                RolePermission(
                    role=target_role,
                    module=permission.module,
                    action=permission.action,
                    allowed=permission.allowed,
                )
                for permission in permissions
            ]
        )