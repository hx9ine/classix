from django.core.management.base import BaseCommand

from apps.accounts.models import (
    AccountCategory,
    User,
)
from apps.tenants.models import Tenant
from apps.rbac.models import Role
from apps.rbac.services import provision_tenant_roles
from apps.staff.models import Staff


class Command(BaseCommand):
    help = (
        "Seeds a local development tenant "
        "and administrator."
    )

    def handle(self, *args, **options):

        tenant, tenant_created = (
            Tenant.objects.get_or_create(
                subdomain_slug="demo",
                defaults={
                    "school_name": "Demo School",
                    "subscription_tier": (
                        Tenant.SubscriptionTier.ULTRA
                    ),
                    "status": Tenant.Status.ACTIVE,
                    "admin_license_limit": 5,
                    "faculty_license_limit": 100,
                    "staff_license_limit": 50,
                    "student_license_limit": 1000,
                },
            )
        )

        provision_tenant_roles(
            tenant=tenant,
        )

        if tenant_created:

            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Demo tenant created."
                )
            )

        else:

            self.stdout.write(
                self.style.WARNING(
                    "✓ Demo tenant already exists."
                )
            )

        user, user_created = (
            User.objects.get_or_create(
                tenant=tenant,
                email="admin@classix.test",
                defaults={
                    "first_name": "Demo",
                    "last_name": "Administrator",
                    "account_category": (
                        AccountCategory.ADMIN
                    ),
                    "is_active": True,
                    "is_staff": True,
                },
            )
        )

        staff = (
            Staff._base_manager
            .filter(
                tenant=tenant,
                user=user,
            )
            .first()
        )

        if staff is not None:

            admin_role = (
                Role.objects
                .filter(
                    tenant=tenant,
                    is_admin_role=True,
                )
                .first()
            )

            if admin_role is None:
                raise RuntimeError(
                    "Demo tenant Admin role was not provisioned."
                )

            if staff.role_id != admin_role.pk:

                staff.role = admin_role

                staff.save(
                    update_fields=[
                        "role",
                    ],
                )

        if user_created:

            user.set_password("admin123")
            user.save(
                update_fields=[
                    "password",
                ]
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Demo administrator created."
                )
            )

        else:

            self.stdout.write(
                self.style.WARNING(
                    "✓ Demo administrator already exists."
                )
            )

        self.stdout.write("")
        self.stdout.write("=" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                "Development environment ready"
            )
        )
        self.stdout.write("")
        self.stdout.write(
            "URL:"
        )
        self.stdout.write(
            "http://demo.localhost:8000"
        )
        self.stdout.write("")
        self.stdout.write(
            "Email:"
        )
        self.stdout.write(
            "admin@classix.test"
        )
        self.stdout.write("")
        self.stdout.write(
            "Password:"
        )
        self.stdout.write(
            "admin123"
        )
        self.stdout.write("=" * 50)