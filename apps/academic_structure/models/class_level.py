import uuid

from django.db import models
from django.urls import reverse

from apps.core.models import BaseModel


class ClassLevel(BaseModel):
    """
    Represents a class level such as
    Grade 1, Grade 2, Year 7, etc.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="class_levels",
    )

    name = models.CharField(
        max_length=100,
    )

    sort_order = models.PositiveIntegerField()

    class Meta:
        ordering = [
            "sort_order",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tenant",
                    "name",
                ],
                name="uq_class_level_tenant_name",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def update_url(self):
        return reverse(
            "academic_structure:class_level_update",
            kwargs={
                "pk": self.pk,
            },
        )

    @property
    def delete_url(self):
        return reverse(
            "academic_structure:class_level_delete",
            kwargs={
                "pk": self.pk,
            },
        )