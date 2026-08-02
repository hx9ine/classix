import uuid

from django.db import models
from django.urls import reverse

from apps.core.models import BaseModel

from .academic_session import AcademicSession
from .class_level import ClassLevel


class Section(BaseModel):
    """
    Represents a section within a class level
    for an academic session.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="sections",
    )

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="sections",
    )

    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        related_name="sections",
    )

    name = models.CharField(
        max_length=20,
    )

    class Meta:
        ordering = [
            "class_level__sort_order",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tenant",
                    "academic_session",
                    "class_level",
                    "name",
                ],
                name="uq_section_tenant_session_class_name",
            ),
        ]

    def __str__(self):
        return f"{self.class_level.name} - {self.name}"

    @property
    def update_url(self):
        return reverse(
            "academic_structure:section_update",
            kwargs={
                "pk": self.pk,
            },
        )

    @property
    def delete_url(self):
        return reverse(
            "academic_structure:section_delete",
            kwargs={
                "pk": self.pk,
            },
        )