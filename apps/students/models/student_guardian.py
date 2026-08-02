from django.db import models

from apps.accounts.models import User

from apps.core.models import BaseModel

from .guardian import Guardian
from .student import Student


class StudentGuardian(BaseModel):
    """
    Relationship between students and guardians.
    """

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="student_guardians",
    )

    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.CASCADE,
        related_name="guardian_students",
    )

    is_emergency_contact = models.BooleanField(
        default=False,
    )

    consent_recorded_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    consent_recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_guardian_consents",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "guardian",
                ],
                name="unique_student_guardian",
            ),
        ]

    def __str__(self):
        return f"{self.student} ↔ {self.guardian}"