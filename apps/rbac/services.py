from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    Role,
    RolePermission,
)
from .selectors import (
    get_role_by_name,
    get_system_roles,
    get_tenant_roles,
)


# ============================================================================
# Role Services
# ============================================================================

@transaction.atomic
def create_role(*, tenant, form):
    """
    Create a tenant role.

    License category and other infrastructure fields are inherited
    from the selected template or defaulted when creating a custom
    role through the UI.
    """

    name = form.cleaned_data["name"]

    if get_role_by_name(
        tenant=tenant,
        name=name,
    ):
        raise ValidationError(
            f'Role "{name}" already exists.'
        )

    role = Role.objects.create(
        tenant=tenant,
        name=name,
        license_category=Role.LicenseCategory.STAFF,
        is_admin_role=False,
        is_editable=True,
    )

    return role


@transaction.atomic
def update_role(*, form):
    """
    Rename a tenant role.
    """

    role = form.instance

    if role.tenant is None:
        raise ValidationError(
            "System roles cannot be modified."
        )

    if not role.is_editable:
        raise ValidationError(
            "This role cannot be modified."
        )

    name = form.cleaned_data["name"]

    existing = get_role_by_name(
        tenant=role.tenant,
        name=name,
    )

    if existing and existing.pk != role.pk:
        raise ValidationError(
            f'Role "{name}" already exists.'
        )

    form.save()

    return role


# ============================================================================
# Tenant Provisioning
# ============================================================================

@transaction.atomic
def clone_system_roles(*, tenant):
    """
    Clone all system roles for a newly created tenant.
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

        _clone_role_permissions(
            source_role=system_role,
            target_role=cloned_role,
        )


# ============================================================================
# Private Helpers
# ============================================================================

def _clone_role_permissions(
    *,
    source_role,
    target_role,
):
    """
    Clone all permission rows from one role to another.
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