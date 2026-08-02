import uuid

from django.db import models
from django.urls import reverse

from apps.core.models import BaseModel


class AcademicSession(BaseModel):
    """
    Academic year/session for a tenant.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="academic_sessions",
    )

    name = models.CharField(
        max_length=100,
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_current = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = [
            "-start_date",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tenant",
                    "name",
                ],
                name="uq_academic_session_tenant_name",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def update_url(self):
        return reverse(
            "academic_structure:academic_session_update",
            kwargs={
                "pk": self.pk,
            },
        )

    @property
    def delete_url(self):
        return reverse(
            "academic_structure:academic_session_delete",
            kwargs={
                "pk": self.pk,
            },
        )