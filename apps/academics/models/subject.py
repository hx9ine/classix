from django.db import models
from django.urls import reverse

from apps.core.models import BaseModel


class Subject(BaseModel):
    """
    Academic subject offered by a school.

    Subjects are tenant-scoped and later referenced by:
    - Timetable periods
    - Homework
    - Exams
    - Grades
    """

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="subjects",
    )

    name = models.CharField(
        max_length=100,
    )

    code = models.CharField(
        max_length=20,
    )

    class Meta:
        ordering = [
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tenant",
                    "name",
                ],
                name="unique_subject_name_per_tenant",
            ),
            models.UniqueConstraint(
                fields=[
                    "tenant",
                    "code",
                ],
                name="unique_subject_code_per_tenant",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def update_url(self):
        return reverse(
            "academics:subject_update",
            kwargs={
                "pk": self.pk,
            },
        )

    @property
    def delete_url(self):
        return reverse(
            "academics:subject_delete",
            kwargs={
                "pk": self.pk,
            },
        )