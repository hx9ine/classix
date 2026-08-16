from django.shortcuts import render

from apps.rbac.decorators import admin_required

from ..selectors import (
    get_license_status,
    get_subscription,
)


@admin_required
def billing_dashboard(request):
    """
    Display the current tenant's subscription and licensing status.

    Billing is strictly scoped to request.tenant.
    """

    subscription = get_subscription(
        tenant=request.tenant,
    )

    license_status = get_license_status(
        tenant=request.tenant,
    )

    return render(
        request,
        "billing/pages/dashboard.html",
        {
            "subscription": subscription,
            "license_status": license_status,
        },
    )