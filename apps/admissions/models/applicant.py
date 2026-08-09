from django.db import models

from apps.core.choices import Gender
from apps.core.models import BaseModel


class Applicant(BaseModel):
    """
    Student applicant awaiting admission.
    """

    class Status(models.TextChoices):
        INQUIRY = "inquiry", "Inquiry"
        APPLIED = "applied", "Applied"
        INTERVIEW = "interview", "Interview"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        ENROLLED = "enrolled", "Enrolled"

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="applicants",
    )

    first_name = models.CharField(
        max_length=150,
    )

    last_name = models.CharField(
        max_length=150,
    )

    dob = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
    )

    applying_for_class_level = models.ForeignKey(
        "academic_structure.ClassLevel",
        on_delete=models.PROTECT,
        related_name="applicants",
    )

    guardian_name = models.CharField(
        max_length=150,
    )

    guardian_phone = models.CharField(
        max_length=20,
    )

    guardian_email = models.EmailField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INQUIRY,
    )

    entrance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )

    linked_student = models.ForeignKey(
        "students.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
    )

    class Meta:
        db_table = "applicant"

        ordering = [
            "first_name",
            "last_name",
        ]

        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["status"]),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name