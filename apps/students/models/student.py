import uuid

from django.db import models
from django.urls import reverse

from apps.accounts.models import User
from apps.academic_structure.models import (
    AcademicSession,
    Section,
)
from apps.core.choices import Gender
from apps.core.models import BaseModel
from apps.tenants.models import Tenant


class StudentStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ALUMNI = "alumni", "Alumni"
    TRANSFERRED = "transferred", "Transferred"


class Student(BaseModel):
    """
    Student enrolled in a tenant.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="students",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile",
    )

    student_code = models.CharField(
        max_length=50,
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    dob = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
    )

    photo_url = models.URLField(
        blank=True,
        null=True,
    )

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.PROTECT,
        related_name="students",
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.PROTECT,
        related_name="students",
    )

    roll_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    enrollment_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=StudentStatus.choices,
        default=StudentStatus.ACTIVE,
    )

    blood_group = models.CharField(
        max_length=10,
        blank=True,
        null=True,
    )

    address = models.TextField(
        blank=True,
        null=True,
    )

    previous_school = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = [
            "student_code",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tenant",
                    "student_code",
                ],
                name="uniq_student_code_per_tenant",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student_code} - "
            f"{self.first_name} {self.last_name}"
        )

    @property
    def update_url(self):
        return reverse(
            "students:student_update",
            kwargs={
                "pk": self.pk,
            },
        )

    @property
    def profile_update_url(self):
        return reverse(
            "students:student_profile_update",
            kwargs={
                "pk": self.pk,
            },
        )