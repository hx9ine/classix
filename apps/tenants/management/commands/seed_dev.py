from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import (
    AccountCategory,
    User,
)
from apps.billing.models import (
    LicenseAddon,
    LicenseAddonType,
    Subscription,
    SubscriptionStatus,
)
from apps.rbac.models import Role
from apps.rbac.services import provision_tenant_roles
from apps.staff.models import Staff
from apps.tenants.models import Tenant


class Command(BaseCommand):
    help = (
        "Seeds a local development tenant, "
        "administrator, subscription, and billing data."
    )

    def handle(self, *args, **options):

        # ====================================================================
        # Demo Tenant
        # ====================================================================

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

        # ====================================================================
        # Tenant Roles
        # ====================================================================

        if not Role.objects.filter(
            tenant=tenant,
        ).exists():

            provision_tenant_roles(
                tenant=tenant,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Demo tenant roles provisioned."
                )
            )

        else:

            self.stdout.write(
                self.style.WARNING(
                    "✓ Demo tenant roles already exist."
                )
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

        # ====================================================================
        # Demo Administrator
        # ====================================================================

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
                ],
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

        # ====================================================================
        # Demo Subscription
        # ====================================================================

        subscription, subscription_created = (
            Subscription.objects.update_or_create(
                tenant=tenant,
                defaults={
                    "tier": Tenant.SubscriptionTier.ULTRA,
                    "stripe_subscription_id": (
                        "sub_dev_demo_ultra"
                    ),
                    "status": SubscriptionStatus.ACTIVE,
                    "current_period_end": (
                        timezone.now()
                        + timedelta(days=30)
                    ),
                },
            )
        )

        if subscription_created:

            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Demo subscription created."
                )
            )

        else:

            self.stdout.write(
                self.style.WARNING(
                    "✓ Demo subscription updated."
                )
            )

        # ====================================================================
        # Demo License Add-ons
        # ====================================================================

        addon_data = [
            (
                LicenseAddonType.ADMIN,
                2,
                "li_dev_demo_admin",
            ),
            (
                LicenseAddonType.FACULTY,
                25,
                "li_dev_demo_faculty",
            ),
            (
                LicenseAddonType.STAFF,
                10,
                "li_dev_demo_staff",
            ),
            (
                LicenseAddonType.STUDENT,
                100,
                "li_dev_demo_student",
            ),
        ]

        for license_type, quantity, line_item_id in addon_data:

            addon, addon_created = (
                LicenseAddon.objects.get_or_create(
                    tenant=tenant,
                    license_type=license_type,
                    stripe_line_item_id=line_item_id,
                    defaults={
                        "quantity": quantity,
                        "purchased_at": timezone.now(),
                    },
                )
            )

            if addon_created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Demo {license_type} license add-on "
                        f"+{quantity} created."
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"✓ Demo {license_type} license add-on "
                        f"already exists."
                    )
                )

        # ====================================================================
        # Output
        # ====================================================================

        self.stdout.write("")
        self.stdout.write("=" * 50)

        self.stdout.write(
            self.style.SUCCESS(
                "Development environment ready"
            )
        )

        self.stdout.write("")

        self.stdout.write(
            "Billing URL:"
        )

        self.stdout.write(
            "http://demo.localhost:8000/billing/"
        )

        self.stdout.write("")

        self.stdout.write(
            "Application URL:"
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