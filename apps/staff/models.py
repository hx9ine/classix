from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TenantModel
from apps.rbac.models import Role


class EmploymentStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")


class Staff(TenantModel):
    """
    Basic staff profile.

    Phase 1:
        - Profile information
        - Role assignment

    Phase 4:
        - Leave management
        - Payroll
        - Teacher assignments
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="staff_profile",
        null=True,
        blank=True,
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    photo_url = models.ImageField(
        upload_to="staff/photos/",
        null=True,
        blank=True,
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="staff",
    )

    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
    )

    joining_date = models.DateField()

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    class Meta:
        ordering = [
            "first_name",
            "last_name",
        ]

        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["role"]),
            models.Index(fields=["employment_status"]),
        ]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self):
        return (
            self.employment_status
            == EmploymentStatus.ACTIVE
        )