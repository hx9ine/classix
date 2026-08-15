from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import Subscription, SubscriptionStatus


# ============================================================================
# Subscription Validation
# ============================================================================

def _validate_tenant(*, tenant):
    """
    Ensure a valid tenant was supplied.
    """

    if tenant is None:
        raise ValidationError(
            "A tenant is required."
        )


def _validate_subscription_tenant(
    *,
    subscription,
    tenant,
):
    """
    Ensure the subscription belongs to the current tenant.
    """

    if subscription.tenant_id != tenant.pk:
        raise ValidationError(
            "The subscription does not belong to the current tenant."
        )


# ============================================================================
# Create
# ============================================================================

@transaction.atomic
def create_subscription(
    *,
    tenant,
    tier,
    stripe_subscription_id,
    status,
    current_period_end,
):
    """
    Create the subscription for a tenant.

    The Subscription tier is the billing source of truth.
    Tenant.subscription_tier is synchronized with it.
    """

    _validate_tenant(
        tenant=tenant,
    )

    if Subscription.objects.filter(
        tenant=tenant,
    ).exists():
        raise ValidationError(
            "This tenant already has a subscription."
        )

    subscription = Subscription.objects.create(
        tenant=tenant,
        tier=tier,
        stripe_subscription_id=stripe_subscription_id,
        status=status,
        current_period_end=current_period_end,
    )

    tenant.subscription_tier = subscription.tier

    tenant.save(
        update_fields=[
            "subscription_tier",
        ],
    )

    return subscription


# ============================================================================
# Update
# ============================================================================

@transaction.atomic
def update_subscription(
    *,
    subscription,
    tenant,
    tier=None,
    stripe_subscription_id=None,
    status=None,
    current_period_end=None,
):
    """
    Update a tenant's subscription.

    Only the subscription belonging to the supplied tenant may
    be modified.

    When the tier changes, the tenant's cached subscription tier
    is synchronized.
    """

    _validate_tenant(
        tenant=tenant,
    )

    _validate_subscription_tenant(
        subscription=subscription,
        tenant=tenant,
    )

    update_fields = []

    if tier is not None:
        subscription.tier = tier
        update_fields.append("tier")

    if stripe_subscription_id is not None:
        subscription.stripe_subscription_id = (
            stripe_subscription_id
        )
        update_fields.append(
            "stripe_subscription_id"
        )

    if status is not None:
        subscription.status = status
        update_fields.append("status")

    if current_period_end is not None:
        subscription.current_period_end = (
            current_period_end
        )
        update_fields.append(
            "current_period_end"
        )

    if update_fields:
        subscription.save(
            update_fields=update_fields,
        )

    if tier is not None:
        tenant.subscription_tier = subscription.tier

        tenant.save(
            update_fields=[
                "subscription_tier",
            ],
        )

    return subscription


# ============================================================================
# Cancellation
# ============================================================================

@transaction.atomic
def cancel_subscription(
    *,
    subscription,
    tenant,
):
    """
    Mark a tenant's subscription as cancelled.

    Cancellation does not alter the subscription tier because
    tier and subscription status represent different concepts.
    """

    _validate_tenant(
        tenant=tenant,
    )

    _validate_subscription_tenant(
        subscription=subscription,
        tenant=tenant,
    )

    if subscription.status == SubscriptionStatus.CANCELLED:
        return subscription

    subscription.status = SubscriptionStatus.CANCELLED

    subscription.save(
        update_fields=[
            "status",
        ],
    )

    return subscription