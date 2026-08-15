from django.shortcuts import get_object_or_404

from ..models import Subscription


# ============================================================================
# Subscription Selectors
# ============================================================================

def get_subscription(
    *,
    tenant,
):
    """
    Return the subscription belonging to the current tenant.

    Tenant isolation is enforced directly in the query.
    """

    return get_object_or_404(
        Subscription,
        tenant=tenant,
    )


def subscription_exists(
    *,
    tenant,
):
    """
    Return whether the current tenant has a subscription.
    """

    return Subscription.objects.filter(
        tenant=tenant,
    ).exists()