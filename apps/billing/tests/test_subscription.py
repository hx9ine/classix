from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.billing.models import (
    Subscription,
    SubscriptionStatus,
)
from apps.billing.services.subscription import (
    cancel_subscription,
    create_subscription,
    update_subscription,
)
from apps.tenants.models import Tenant


class SubscriptionServiceTests(TestCase):

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

        self.period_end = (
            timezone.now()
            + timedelta(days=30)
        )

    # ========================================================================
    # Create
    # ========================================================================

    def test_create_subscription(self):
        subscription = create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=self.period_end,
        )

        self.assertEqual(
            subscription.tenant,
            self.tenant,
        )

        self.assertEqual(
            subscription.tier,
            Tenant.SubscriptionTier.BASIC,
        )

        self.assertEqual(
            self.tenant.subscription_tier,
            Tenant.SubscriptionTier.BASIC,
        )

    def test_create_subscription_synchronizes_tenant_tier(self):
        subscription = create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.PRO,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=self.period_end,
        )

        self.tenant.refresh_from_db()

        self.assertEqual(
            subscription.tier,
            Tenant.SubscriptionTier.PRO,
        )

        self.assertEqual(
            self.tenant.subscription_tier,
            Tenant.SubscriptionTier.PRO,
        )

    def test_create_subscription_rejects_duplicate_subscription(self):
        create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=self.period_end,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "This tenant already has a subscription.",
        ):
            create_subscription(
                tenant=self.tenant,
                tier=Tenant.SubscriptionTier.PRO,
                stripe_subscription_id="sub_demo_456",
                status=SubscriptionStatus.ACTIVE,
                current_period_end=self.period_end,
            )

    # ========================================================================
    # Update
    # ========================================================================

    def test_update_subscription_tier(self):
        subscription = create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=self.period_end,
        )

        updated = update_subscription(
            subscription=subscription,
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.PRO,
        )

        self.assertEqual(
            updated.pk,
            subscription.pk,
        )

        self.assertEqual(
            updated.tier,
            Tenant.SubscriptionTier.PRO,
        )

        self.tenant.refresh_from_db()

        self.assertEqual(
            self.tenant.subscription_tier,
            Tenant.SubscriptionTier.PRO,
        )

    def test_update_subscription_status(self):
        subscription = create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=self.period_end,
        )

        update_subscription(
            subscription=subscription,
            tenant=self.tenant,
            status=SubscriptionStatus.PAST_DUE,
        )

        subscription.refresh_from_db()

        self.assertEqual(
            subscription.status,
            SubscriptionStatus.PAST_DUE,
        )

    def test_update_subscription_period_end(self):
        subscription = create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=self.period_end,
        )

        new_period_end = (
            self.period_end
            + timedelta(days=30)
        )

        update_subscription(
            subscription=subscription,
            tenant=self.tenant,
            current_period_end=new_period_end,
        )

        subscription.refresh_from_db()

        self.assertEqual(
            subscription.current_period_end,
            new_period_end,
        )

    # ========================================================================
    # Tenant Isolation
    # ========================================================================

    def test_other_tenant_cannot_update_subscription(self):
        subscription = create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=self.period_end,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "The subscription does not belong to the current tenant.",
        ):
            update_subscription(
                subscription=subscription,
                tenant=self.other_tenant,
                tier=Tenant.SubscriptionTier.PRO,
            )

        subscription.refresh_from_db()

        self.assertEqual(
            subscription.tier,
            Tenant.SubscriptionTier.BASIC,
        )

        self.other_tenant.refresh_from_db()

        self.assertEqual(
            self.other_tenant.subscription_tier,
            Tenant.SubscriptionTier.PRO,
        )

    def test_other_tenant_cannot_cancel_subscription(self):
        subscription = create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=self.period_end,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "The subscription does not belong to the current tenant.",
        ):
            cancel_subscription(
                subscription=subscription,
                tenant=self.other_tenant,
            )

        subscription.refresh_from_db()

        self.assertEqual(
            subscription.status,
            SubscriptionStatus.ACTIVE,
        )

    # ========================================================================
    # Cancellation
    # ========================================================================

    def test_cancel_subscription(self):
        subscription = create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.PRO,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=self.period_end,
        )

        cancel_subscription(
            subscription=subscription,
            tenant=self.tenant,
        )

        subscription.refresh_from_db()

        self.assertEqual(
            subscription.status,
            SubscriptionStatus.CANCELLED,
        )

    def test_cancellation_does_not_change_tier(self):
        subscription = create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.PRO,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=self.period_end,
        )

        cancel_subscription(
            subscription=subscription,
            tenant=self.tenant,
        )

        self.tenant.refresh_from_db()

        self.assertEqual(
            subscription.tier,
            Tenant.SubscriptionTier.PRO,
        )

        self.assertEqual(
            self.tenant.subscription_tier,
            Tenant.SubscriptionTier.PRO,
        )

    def test_cancel_already_cancelled_subscription_is_idempotent(self):
        subscription = create_subscription(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.CANCELLED,
            current_period_end=self.period_end,
        )

        result = cancel_subscription(
            subscription=subscription,
            tenant=self.tenant,
        )

        self.assertEqual(
            result.pk,
            subscription.pk,
        )

        self.assertEqual(
            result.status,
            SubscriptionStatus.CANCELLED,
        )