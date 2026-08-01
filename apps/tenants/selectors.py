from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from .models import Tenant


def get_tenant(
    *,
    tenant_id: UUID,
) -> Tenant | None:
    """
    Retrieve a tenant by ID.
    """
    return (
        Tenant.objects.filter(
            id=tenant_id,
        )
        .first()
    )


def get_tenant_by_subdomain(
    *,
    subdomain_slug: str,
) -> Tenant | None:
    """
    Retrieve an active tenant by subdomain.
    """
    return (
        Tenant.objects.filter(
            subdomain_slug=subdomain_slug,
            status=Tenant.Status.ACTIVE,
        )
        .first()
    )


def get_tenant_by_custom_domain(
    *,
    custom_domain: str,
) -> Tenant | None:
    """
    Retrieve an active tenant by custom domain.
    """
    return (
        Tenant.objects.filter(
            custom_domain=custom_domain,
            status=Tenant.Status.ACTIVE,
        )
        .first()
    )


def get_active_tenants() -> QuerySet[Tenant]:
    """
    Return all active tenants.
    """
    return (
        Tenant.objects.filter(
            status=Tenant.Status.ACTIVE,
        )
        .order_by("school_name")
    )