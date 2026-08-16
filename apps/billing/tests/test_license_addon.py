from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.billing.models import (
    LicenseAddon,
    LicenseAddonType,
)
from apps.tenants.models import Tenant


class LicenseAddonModelTests(TestCase):

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

    def test_license_addon_belongs_to_tenant(self):
        addon = LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=25,
            stripe_line_item_id="li_demo_123",
            purchased_at=self.purchased_at,
        )

        self.assertEqual(
            addon.tenant,
            self.tenant,
        )

        self.assertEqual(
            self.tenant.license_addons.get(),
            addon,
        )

    def test_tenant_can_have_multiple_license_addons(self):
        first_addon = LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=25,
            stripe_line_item_id="li_demo_123",
            purchased_at=self.purchased_at,
        )

        second_addon = LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.FACULTY,
            quantity=10,
            stripe_line_item_id="li_demo_456",
            purchased_at=(
                self.purchased_at
                + timedelta(minutes=1)
            ),
        )

        addons = list(
            self.tenant.license_addons.order_by(
                "purchased_at",
            )
        )

        self.assertEqual(
            addons,
            [
                first_addon,
                second_addon,
            ],
        )

    def test_license_type_choices(self):
        addon = LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.ADMIN,
            quantity=1,
            stripe_line_item_id="li_demo_admin",
            purchased_at=self.purchased_at,
        )

        self.assertEqual(
            addon.license_type,
            LicenseAddonType.ADMIN,
        )

        self.assertEqual(
            addon.get_license_type_display(),
            "Admin",
        )

    def test_all_four_license_types_are_available(self):
        expected_types = {
            "admin",
            "faculty",
            "staff",
            "student",
        }

        actual_types = {
            value
            for value, label
            in LicenseAddonType.choices
        }

        self.assertEqual(
            actual_types,
            expected_types,
        )

    def test_quantity_is_stored(self):
        addon = LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STAFF,
            quantity=25,
            stripe_line_item_id="li_demo_staff",
            purchased_at=self.purchased_at,
        )

        self.assertEqual(
            addon.quantity,
            25,
        )

    def test_stripe_line_item_id_is_stored(self):
        addon = LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=25,
            stripe_line_item_id="li_demo_123",
            purchased_at=self.purchased_at,
        )

        self.assertEqual(
            addon.stripe_line_item_id,
            "li_demo_123",
        )

    def test_purchased_at_is_stored(self):
        addon = LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=25,
            stripe_line_item_id="li_demo_123",
            purchased_at=self.purchased_at,
        )

        self.assertEqual(
            addon.purchased_at,
            self.purchased_at,
        )

    def test_addons_are_tenant_isolated_at_relationship_level(self):
        tenant_addon = LicenseAddon.objects.create(
            tenant=self.tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=25,
            stripe_line_item_id="li_demo_123",
            purchased_at=self.purchased_at,
        )

        other_addon = LicenseAddon.objects.create(
            tenant=self.other_tenant,
            license_type=LicenseAddonType.STUDENT,
            quantity=50,
            stripe_line_item_id="li_other_123",
            purchased_at=self.purchased_at,
        )

        self.assertEqual(
            list(self.tenant.license_addons.all()),
            [tenant_addon],
        )

        self.assertEqual(
            list(self.other_tenant.license_addons.all()),
            [other_addon],
        )
