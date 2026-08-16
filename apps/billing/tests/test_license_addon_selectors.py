from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.billing.models import (
    LicenseAddon,
    LicenseAddonType,
)
from apps.billing.selectors import (
    get_license_addon_quantities,
    get_license_addons,
)
from apps.tenants.models import Tenant


class LicenseAddonSelectorTests(TestCase):

    def setUp(self):
        self.tenant = Tenant.objects.create(
            school_name="Demo School",
            subdomain_slug="demo",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            status=Tenant.Status.ACTIVE,
            admin_license_limit=1,
            faculty_license_limit=5,
            staff_license_limit=5,
            student_license_limit=50,
        )

        self.other_tenant = Tenant.objects.create(
            school_name="Other School",
            subdomain_slug="other",
            subscription_tier=Tenant.SubscriptionTier.PRO,
            status=Tenant.Status.ACTIVE,
            admin_license_limit=2,
            faculty_license_limit=10,
            staff_license_limit=10,
            student_license_limit=100,
        )

        self.purchased_at = timezone.now()

    def test_get_license_addons_returns_only_current_tenant_addons(self):
        addon = LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=25,
            stripe_line_item_id="li_demo_123",
            purchased_at=self.purchased_at,
        )

        LicenseAddon.objects.create(
            tenant=self.other_tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=50,
            stripe_line_item_id="li_other_123",
            purchased_at=self.purchased_at,
        )

        addons = list(
            get_license_addons(
                tenant=self.tenant,
            )
        )

        self.assertEqual(
            addons,
            [addon],
        )

    def test_get_license_addon_quantities_returns_zero_without_addons(self):
        quantities = get_license_addon_quantities(
            tenant=self.tenant,
        )

        self.assertEqual(
            quantities,
            {
                "admin": 0,
                "faculty": 0,
                "staff": 0,
                "student": 0,
            },
        )

    def test_get_license_addon_quantities_sums_each_category(self):
        LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.ADMIN,
            quantity=2,
            stripe_line_item_id="li_admin_1",
            purchased_at=self.purchased_at,
        )

        LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.FACULTY,
            quantity=10,
            stripe_line_item_id="li_faculty_1",
            purchased_at=self.purchased_at,
        )

        LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.FACULTY,
            quantity=5,
            stripe_line_item_id="li_faculty_2",
            purchased_at=(
                self.purchased_at
                + timedelta(minutes=1)
            ),
        )

        LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STAFF,
            quantity=7,
            stripe_line_item_id="li_staff_1",
            purchased_at=self.purchased_at,
        )

        LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=25,
            stripe_line_item_id="li_student_1",
            purchased_at=self.purchased_at,
        )

        quantities = get_license_addon_quantities(
            tenant=self.tenant,
        )

        self.assertEqual(
            quantities,
            {
                "admin": 2,
                "faculty": 15,
                "staff": 7,
                "student": 25,
            },
        )

    def test_addon_quantities_do_not_include_other_tenant(self):
        LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=25,
            stripe_line_item_id="li_demo_123",
            purchased_at=self.purchased_at,
        )

        LicenseAddon.objects.create(
            tenant=self.other_tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=100,
            stripe_line_item_id="li_other_123",
            purchased_at=self.purchased_at,
        )

        quantities = get_license_addon_quantities(
            tenant=self.tenant,
        )

        self.assertEqual(
            quantities["student"],
            25,
        )