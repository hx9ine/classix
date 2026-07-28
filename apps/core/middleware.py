from django.conf import settings
from django.http import Http404

from apps.core.constants import RESERVED_SUBDOMAINS
from apps.tenants.models import Tenant

from apps.core.utils import (
    set_current_tenant,
    clear_current_tenant,
)


class TenantMiddleware:
    """
    Resolves the current tenant from the request host.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = self.get_tenant(request)

        request.tenant = tenant
        set_current_tenant(tenant)

        try:
            response = self.get_response(request)
        finally:
            clear_current_tenant()

        return response

    def get_tenant(self, request):
        host = request.get_host().split(":")[0]

        # Local development
        if host in ("localhost", "127.0.0.1"):
            return None

        parts = host.split(".")

        # No subdomain
        if len(parts) < 3:
            return None

        subdomain = parts[0].lower()

        if subdomain in RESERVED_SUBDOMAINS:
            raise Http404("Reserved subdomain")

        try:
            return Tenant.objects.get(
                subdomain_slug=subdomain,
                status=Tenant.Status.ACTIVE,
            )
        except Tenant.DoesNotExist:
            raise Http404("School not found")