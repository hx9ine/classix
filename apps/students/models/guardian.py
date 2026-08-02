import uuid

from django.db import models

from apps.accounts.models import User
from apps.core.models import BaseModel
from apps.tenants.models import Tenant


class Guardian(BaseModel):
    """
    Parent or guardian associated with one or more students.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="guardians",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guardian_profile",
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    phone = models.CharField(
        max_length=20,
    )

    email = models.EmailField()

    relationship = models.CharField(
        max_length=50,
    )

    class Meta:
        ordering = [
            "first_name",
            "last_name",
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"