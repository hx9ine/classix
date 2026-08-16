from django.core.exceptions import PermissionDenied
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import AccountCategory, User
from apps.billing.models import (
    Subscription,
    SubscriptionStatus,
)
from apps.billing.views import billing_dashboard
from apps.tenants.models import Tenant


@override_settings(
    ALLOWED_HOSTS=[
        "demo.localhost",
        "other.localhost",
    ],
)
class BillingDashboardViewTests(TestCase):
    """
    Tests for the tenant-admin Billing dashboard.

    Tenant resolution is exercised through the real TenantMiddleware
    by making requests against the tenant's subdomain.
    """

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        self.tenant = Tenant.objects.create(
            school_name="Demo School",
            subdomain_slug="demo",
            subscription_tier=Tenant.SubscriptionTier.BASIC,
            admin_license_limit=1,
            faculty_license_limit=2,
            staff_license_limit=2,
            student_license_limit=2,
        )

        self.other_tenant = Tenant.objects.create(
            school_name="Other School",
            subdomain_slug="other",
            subscription_tier=Tenant.SubscriptionTier.PRO,
            admin_license_limit=1,
            faculty_license_limit=5,
            staff_license_limit=5,
            student_license_limit=50,
        )

        self.admin_user = User.objects.create_user(
            tenant=self.tenant,
            email="admin@demo.example",
            password="test-password",
            first_name="Demo",
            last_name="Admin",
            account_category=AccountCategory.ADMIN,
        )

        self.staff_user = User.objects.create_user(
            tenant=self.tenant,
            email="staff@demo.example",
            password="test-password",
            first_name="Demo",
            last_name="Staff",
            account_category=AccountCategory.STAFF,
        )

        self.other_admin_user = User.objects.create_user(
            tenant=self.other_tenant,
            email="admin@other.example",
            password="test-password",
            first_name="Other",
            last_name="Admin",
            account_category=AccountCategory.ADMIN,
        )

        self.subscription = Subscription.objects.create(
            tenant=self.tenant,
            tier=Tenant.SubscriptionTier.BASIC,
            stripe_subscription_id="sub_demo_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=timezone.now(),
        )

        self.other_subscription = Subscription.objects.create(
            tenant=self.other_tenant,
            tier=Tenant.SubscriptionTier.PRO,
            stripe_subscription_id="sub_other_123",
            status=SubscriptionStatus.ACTIVE,
            current_period_end=timezone.now(),
        )

    # ========================================================================
    # Direct View Helper
    # ========================================================================

    def _request(
        self,
        *,
        user,
        tenant,
    ):
        request = self.factory.get(
            reverse("billing:dashboard"),
        )

        request.user = user
        request.tenant = tenant

        return request

    # ========================================================================
    # Authentication
    # ========================================================================

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse("billing:dashboard"),
            HTTP_HOST="demo.localhost",
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertIn(
            "/accounts/login/",
            response.url,
        )

    # ========================================================================
    # Authorization
    # ========================================================================

    def test_admin_can_access_billing_dashboard(self):
        self.client.force_login(
            self.admin_user,
        )

        response = self.client.get(
            reverse("billing:dashboard"),
            HTTP_HOST="demo.localhost",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "billing/pages/dashboard.html",
        )

    def test_non_admin_cannot_access_billing_dashboard(self):
        request = self._request(
            user=self.staff_user,
            tenant=self.tenant,
        )

        with self.assertRaises(
            PermissionDenied,
        ):
            billing_dashboard(
                request,
            )

    # ========================================================================
    # Tenant Isolation
    # ========================================================================

    def test_admin_sees_current_tenant_subscription(self):
        self.client.force_login(
            self.admin_user,
        )

        response = self.client.get(
            reverse("billing:dashboard"),
            HTTP_HOST="demo.localhost",
        )

        self.assertContains(
            response,
            "Basic",
        )

        self.assertNotContains(
            response,
            "Pro",
        )

    def test_other_tenant_admin_sees_only_other_tenant_subscription(self):
        self.client.force_login(
            self.other_admin_user,
        )

        response = self.client.get(
            reverse("billing:dashboard"),
            HTTP_HOST="other.localhost",
        )

        self.assertContains(
            response,
            "Pro",
        )

        self.assertNotContains(
            response,
            "Basic",
        )

    # ========================================================================
    # License Status
    # ========================================================================

    def test_dashboard_contains_license_status(self):
        self.client.force_login(
            self.admin_user,
        )

        response = self.client.get(
            reverse("billing:dashboard"),
            HTTP_HOST="demo.localhost",
        )

        self.assertContains(
            response,
            "0 / 1",
        )

        self.assertContains(
            response,
            "0 / 2",
        )

    def test_license_status_is_scoped_to_current_tenant(self):
        self.client.force_login(
            self.admin_user,
        )

        response = self.client.get(
            reverse("billing:dashboard"),
            HTTP_HOST="demo.localhost",
        )

        self.assertContains(
            response,
            f"0 / {self.tenant.admin_license_limit}",
        )

        self.assertContains(
            response,
            f"0 / {self.tenant.faculty_license_limit}",
        )

        self.assertContains(
            response,
            f"0 / {self.tenant.staff_license_limit}",
        )

        self.assertContains(
            response,
            f"0 / {self.tenant.student_license_limit}",
        )

    def test_other_tenant_license_limits_are_not_exposed(self):
        self.client.force_login(
            self.admin_user,
        )

        response = self.client.get(
            reverse("billing:dashboard"),
            HTTP_HOST="demo.localhost",
        )

        self.assertContains(
            response,
            "0 / 2",
        )

        self.assertNotContains(
            response,
            "0 / 5",
        )

        self.assertNotContains(
            response,
            "0 / 50",
        )

    # ========================================================================
    # Subscription
    # ========================================================================

    def test_subscription_status_is_available_to_template(self):
        self.client.force_login(
            self.admin_user,
        )

        response = self.client.get(
            reverse("billing:dashboard"),
            HTTP_HOST="demo.localhost",
        )

        self.assertContains(
            response,
            "Active",
        )

    def test_subscription_tier_is_current_tenant_tier(self):
        self.client.force_login(
            self.admin_user,
        )

        response = self.client.get(
            reverse("billing:dashboard"),
            HTTP_HOST="demo.localhost",
        )

        self.assertContains(
            response,
            "Basic",
        )

        self.assertNotContains(
            response,
            "Pro",
        )