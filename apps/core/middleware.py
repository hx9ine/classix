from django.conf import settings
from django.http import Http404

from apps.core.constants import RESERVED_SUBDOMAINS
from apps.tenants.selectors import get_tenant_by_subdomain

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
        host = request.get_host().split(":", 1)[0].lower()

        # Local development without tenant
        if host in ("localhost", "127.0.0.1"):
            return None

        parts = host.split(".")

        # Expect:
        # demo.localhost
        # school.classix.com
        if len(parts) < 2:
            return None

        subdomain = parts[0]

        if subdomain in RESERVED_SUBDOMAINS:
            raise Http404("Reserved subdomain")

        tenant = get_tenant_by_subdomain(
            subdomain_slug=subdomain,
        )

        if tenant is None:
            raise Http404("School not found")

        return tenant