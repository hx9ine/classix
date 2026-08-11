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


@transaction.atomic
def provision_tenant_roles(*, tenant):
    """
    Provision the predefined system roles for a tenant.

    A newly provisioned tenant receives tenant-owned clones of
    all predefined system roles.
    """

    system_roles = list(
        get_system_roles()
    )

    if not system_roles:
        raise ValidationError(
            "System roles have not been seeded."
        )

    tenant_roles = list(
        get_tenant_roles(
            tenant=tenant,
        )
    )

    if not tenant_roles:
        clone_system_roles(
            tenant=tenant,
        )
        return

    if len(tenant_roles) != 1:
        raise ValidationError(
            "Tenant role provisioning cannot proceed because "
            "the tenant already has multiple roles."
        )

    existing_role = tenant_roles[0]

    if existing_role.name != "Faculty":
        raise ValidationError(
            "Tenant has an unexpected existing role. "
            "Manual review is required."
        )

    teacher_role = next(
        (
            role
            for role in system_roles
            if role.name == "Teacher"
        ),
        None,
    )

    if teacher_role is None:
        raise ValidationError(
            "The Teacher system role has not been seeded."
        )

    existing_role.name = teacher_role.name
    existing_role.license_category = (
        teacher_role.license_category
    )
    existing_role.is_admin_role = (
        teacher_role.is_admin_role
    )
    existing_role.is_editable = True
    existing_role.cloned_from_role = teacher_role

    existing_role.save(
        update_fields=[
            "name",
            "license_category",
            "is_admin_role",
            "is_editable",
            "cloned_from_role",
        ],
    )

    RolePermission.objects.filter(
        role=existing_role,
    ).delete()

    _clone_role_permissions(
        source_role=teacher_role,
        target_role=existing_role,
    )

    for system_role in system_roles:

        if system_role.pk == teacher_role.pk:
            continue

        target_role = Role.objects.create(
            tenant=tenant,
            name=system_role.name,
            license_category=system_role.license_category,
            is_admin_role=system_role.is_admin_role,
            is_editable=True,
            cloned_from_role=system_role,
        )

        _clone_role_permissions(
            source_role=system_role,
            target_role=target_role,
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