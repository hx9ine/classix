from django.db import models

from apps.core.models import BaseModel


class Exam(BaseModel):
    """
    Represents an exam or assessment period
    for an academic session.
    """

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="exams",
    )

    academic_session = models.ForeignKey(
        "academic_structure.AcademicSession",
        on_delete=models.CASCADE,
        related_name="exams",
    )

    name = models.CharField(
        max_length=255,
    )

    start_date = models.DateField()

    end_date = models.DateField()

    class Meta:
        ordering = [
            "start_date",
            "name",
        ]

    def __str__(self):
        return self.name