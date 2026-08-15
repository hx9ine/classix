from django.db import models

from apps.core.models import BaseModel
from apps.tenants.models import Tenant


class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    PAST_DUE = "past_due", "Past Due"
    CANCELLED = "cancelled", "Cancelled"


class Subscription(BaseModel):
    """
    Billing subscription belonging to exactly one tenant.

    The subscription tier is the billing source of truth.
    Tenant.subscription_tier remains a cached value.
    """

    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name="subscription",
    )

    tier = models.CharField(
        max_length=10,
        choices=Tenant.SubscriptionTier.choices,
    )

    stripe_subscription_id = models.CharField(
        max_length=255,
    )

    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
    )

    current_period_end = models.DateTimeField()

    class Meta:
        ordering = [
            "-current_period_end",
        ]

    def __str__(self):
        return (
            f"{self.tenant} - "
            f"{self.get_tier_display()}"
        )
