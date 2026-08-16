from django.db.models import Sum

from ..models import LicenseAddon


# ============================================================================
# License Addon Selectors
# ============================================================================

def get_license_addons(
    *,
    tenant,
):
    """
    Return all license add-ons belonging to the current tenant.

    Every query is explicitly tenant-scoped.
    """

    return (
        LicenseAddon.objects
        .filter(
            tenant=tenant,
        )
        .order_by(
            "-purchased_at",
        )
    )


def get_license_addon_quantities(
    *,
    tenant,
):
    """
    Return the total purchased add-on quantity for each
    license category.

    Multiple add-ons of the same category are summed together.
    """

    totals = {
        "admin": 0,
        "faculty": 0,
        "staff": 0,
        "student": 0,
    }

    rows = (
        LicenseAddon.objects
        .filter(
            tenant=tenant,
        )
        .values(
            "license_type",
        )
        .annotate(
            total_quantity=Sum("quantity"),
        )
    )

    for row in rows:
        totals[row["license_type"]] = (
            row["total_quantity"] or 0
        )

    return totals