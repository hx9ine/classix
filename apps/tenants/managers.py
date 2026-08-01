from django.db import models

from apps.core.utils import get_current_tenant


class TenantQuerySet(models.QuerySet):
    """
    QuerySet scoped to the current tenant.
    """

    def for_current_tenant(self):
        tenant = get_current_tenant()

        if tenant is None:
            return self.none()

        return self.filter(tenant=tenant)


class TenantManager(models.Manager):
    """
    Default manager for tenant-owned models.
    """

    def get_queryset(self):
        return (
            TenantQuerySet(self.model, using=self._db)
            .for_current_tenant()
        )