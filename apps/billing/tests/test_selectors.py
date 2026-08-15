from datetime import timedelta

from django.http import Http404
from django.test import TestCase
from django.utils import timezone

from apps.billing.models import (
    Subscription,
    SubscriptionStatus,
)
from apps.billing.selectors import (
    get_subscription,
    subscription_exists,
)
from apps.tenants.models import Tenant


class SubscriptionSelectorTests(TestCase):

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

        self.subscription = Subscription.objects.create(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )

        self.other_subscription = Subscription.objects.create(
            tenant=self.other_tenant,
            tier=Tenant.SubscriptionTier.PRO,
            stripe_subscription_id="sub_other_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )

    def test_get_subscription_returns_current_tenant_subscription(self):
        subscription = get_subscription(
            tenant=self.tenant,
        )

        self.assertEqual(
            subscription,
            self.subscription,
        )

    def test_get_subscription_returns_other_tenant_subscription_for_other_tenant(
        self,
    ):
        subscription = get_subscription(
            tenant=self.other_tenant,
        )

        self.assertEqual(
            subscription,
            self.other_subscription,
        )

        self.assertNotEqual(
            subscription,
            self.subscription,
        )

    def test_get_subscription_raises_for_tenant_without_subscription(self):
        tenant_without_subscription = Tenant.objects.create(
            school_name="Third School",
            subdomain_slug="third",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            status=Tenant.Status.ACTIVE,
            admin_license_limit=1,
            faculty_license_limit=5,
            staff_license_limit=5,
            student_license_limit=50,
        )

        with self.assertRaises(Http404):
            get_subscription(
                tenant=tenant_without_subscription,
            )

    def test_subscription_exists_returns_true_for_current_tenant(self):
        self.assertTrue(
            subscription_exists(
                tenant=self.tenant,
            )
        )

    def test_subscription_exists_returns_true_for_other_tenant(self):
        self.assertTrue(
            subscription_exists(
                tenant=self.other_tenant,
            )
        )

    def test_subscription_exists_returns_false_without_subscription(self):
        tenant_without_subscription = Tenant.objects.create(
            school_name="Third School",
            subdomain_slug="third",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            status=Tenant.Status.ACTIVE,
            admin_license_limit=1,
            faculty_license_limit=5,
            staff_license_limit=5,
            student_license_limit=50,
        )

        self.assertFalse(
            subscription_exists(
                tenant=tenant_without_subscription,
            )
        )