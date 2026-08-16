from django.db import models

from apps.core.models import BaseModel
from apps.tenants.models import Tenant


class LicenseAddonType(models.TextChoices):
    ADMIN = "admin", "Admin"
    FACULTY = "faculty", "Faculty"
    STAFF = "staff", "Staff"
    STUDENT = "student", "Student"


class LicenseAddon(BaseModel):
    """
    Additional license capacity purchased for a tenant.

    A tenant may have multiple license add-ons.
    """

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="license_addons",
    )

    license_type = models.CharField(
        max_length=20,
        choices=LicenseAddonType.choices,
    )

    quantity = models.IntegerField()

    stripe_line_item_id = models.CharField(
        max_length=255,
    )

    purchased_at = models.DateTimeField()

    class Meta:
        ordering = [
            "-purchased_at",
        ]

    def __str__(self):
        return (
            f"{self.tenant} - "
            f"{self.get_license_type_display()} +"
            f"{self.quantity}"
        )
