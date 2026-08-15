import uuid
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.billing.models import (
    Subscription,
    SubscriptionStatus,
)
from apps.tenants.models import Tenant


class SubscriptionModelTests(TestCase):

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

    def test_subscription_belongs_to_tenant(self):
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_test_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )

        self.assertEqual(
            subscription.tenant,
            self.tenant,
        )

        self.assertEqual(
            self.tenant.subscription,
            subscription,
        )

    def test_subscription_tenant_relationship_is_one_to_one(self):
        Subscription.objects.create(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_test_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )

        with self.assertRaises(Exception):
            Subscription.objects.create(
                tenant=self.tenant,
                tier=Tenant.SubscriptionTier.PRO,
                stripe_subscription_id="sub_test_456",
                status=SubscriptionStatus.ACTIVE,
                current_period_end=timezone.now() + timedelta(days=30),
            )

    def test_subscription_uses_tenant_tier_choices(self):
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.PRO,
            stripe_subscription_id="sub_test_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )

        self.assertEqual(
            subscription.tier,
            Tenant.SubscriptionTier.PRO,
        )

    def test_subscription_has_uuid_primary_key(self):
        subscription = Subscription.objects.create(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_test_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=timezone.now() + timedelta(days=30),
        )

        self.assertIsInstance(
            subscription.pk,
            uuid.UUID,
        )
