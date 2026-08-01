import uuid

from django.db import models

from apps.core.models import TimeStampedModel
from apps.core.choices import Gender
from apps.tenants.models import Tenant
from apps.accounts.models import User
from apps.academic_structure.models import (
    AcademicSession,
    Section,
)


class StudentStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ALUMNI = "alumni", "Alumni"
    TRANSFERRED = "transferred", "Transferred"


class Student(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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

    student_code = models.CharField(max_length=50)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    dob = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
    )

    photo_url = models.URLField(blank=True, null=True)

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

    status = models.CharField(
        max_length=20,
        choices=StudentStatus.choices,
        default=StudentStatus.ACTIVE,
    )

    enrollment_date = models.DateField()

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

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.PROTECT,
        related_name="students",
    )

    class Meta:
        db_table = "student"
        ordering = ["student_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "student_code"],
                name="uniq_student_code_per_tenant",
            ),
        ]

    def __str__(self):
        return f"{self.student_code} - {self.first_name} {self.last_name}"


class Guardian(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)
    email = models.EmailField()

    relationship = models.CharField(max_length=50)

    class Meta:
        db_table = "guardian"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class StudentGuardian(TimeStampedModel):
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

    is_emergency_contact = models.BooleanField(default=False)

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
        db_table = "student_guardian"
        unique_together = (
            ("student", "guardian"),
        )

    def __str__(self):
        return f"{self.student} ↔ {self.guardian}"