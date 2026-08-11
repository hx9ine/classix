from django.core.management.base import BaseCommand
from django.db import transaction

from apps.rbac.models import Role, RolePermission


SYSTEM_ROLES = [
    {
        "name": "Admin",
        "license_category": Role.LicenseCategory.ADMIN,
        "is_admin_role": True,
    },
    {
        "name": "Teacher",
        "license_category": Role.LicenseCategory.FACULTY,
        "is_admin_role": False,
    },
    {
        "name": "Accountant",
        "license_category": Role.LicenseCategory.STAFF,
        "is_admin_role": False,
    },
    {
        "name": "Librarian",
        "license_category": Role.LicenseCategory.STAFF,
        "is_admin_role": False,
    },
    {
        "name": "Registrar / Front Desk",
        "license_category": Role.LicenseCategory.STAFF,
        "is_admin_role": False,
    },
    {
        "name": "Transport Coordinator",
        "license_category": Role.LicenseCategory.STAFF,
        "is_admin_role": False,
    },
    {
        "name": "Nurse / Health Officer",
        "license_category": Role.LicenseCategory.STAFF,
        "is_admin_role": False,
    },
]


PERMISSIONS = {
    "Teacher": {
        "students": ["view"],
        "attendance": ["view", "create", "edit"],
        "academics": ["view", "create", "edit"],
        "grades": ["view", "create", "edit"],
        "messages": ["view", "create"],
        "schedule": ["view"],
    },
    "Accountant": {
        "students": ["view"],
        "fees": ["view", "create", "edit", "delete"],
        "messages": ["view", "create"],
        "staff": ["view"],
        "schedule": ["view"],
    },
    "Librarian": {
        "students": ["view"],
        "messages": ["view", "create"],
        "staff": ["view"],
        "schedule": ["view"],
        "library": ["view", "create", "edit", "delete"],
    },
    "Registrar / Front Desk": {
        "students": ["view", "create", "edit"],
        "attendance": ["view"],
        "academics": ["view"],
        "grades": ["view"],
        "messages": ["view", "create"],
        "staff": ["view"],
        "schedule": ["view", "create"],
        "admissions": ["view", "create", "edit", "delete"],
        "documents": ["view", "create", "edit"],
    },
    "Transport Coordinator": {
        "students": ["view"],
        "messages": ["view", "create"],
        "staff": ["view"],
        "schedule": ["view"],
        "transport": ["view", "create", "edit", "delete"],
    },
    "Nurse / Health Officer": {
        "students": ["view"],
        "messages": ["view", "create"],
        "staff": ["view"],
        "schedule": ["view"],
        "health": ["view", "create", "edit", "delete"],
    },
}


class Command(BaseCommand):
    help = "Seed the predefined ClassiX system role templates."

    @transaction.atomic
    def handle(self, *args, **options):
        for role_data in SYSTEM_ROLES:

            role, created = Role.objects.get_or_create(
                tenant=None,
                name=role_data["name"],
                defaults={
                    "license_category": role_data["license_category"],
                    "is_admin_role": role_data["is_admin_role"],
                    "is_editable": False,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created system role: {role.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"System role already exists: {role.name}"
                    )
                )

            if role.license_category != role_data["license_category"]:
                raise ValueError(
                    f'System role "{role.name}" has an unexpected '
                    "license category."
                )

            if role.is_admin_role != role_data["is_admin_role"]:
                raise ValueError(
                    f'System role "{role.name}" has an unexpected '
                    "admin-role flag."
                )

            if role.is_editable:
                role.is_editable = False
                role.save(
                    update_fields=["is_editable"],
                )

            if role.name == "Admin":
                continue

            permissions = PERMISSIONS[role.name]

            for module, actions in permissions.items():

                for action in actions:

                    RolePermission.objects.get_or_create(
                        role=role,
                        module=module,
                        action=action,
                        defaults={
                            "allowed": True,
                        },
                    )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "System role provisioning complete."
            )
        )