from django.db import models

from apps.core.models import BaseModel


class Assignment(BaseModel):
    """
    Homework assignment for a section.
    """

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    section = models.ForeignKey(
        "academic_structure.Section",
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    staff = models.ForeignKey(
        "staff.Staff",
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField()

    due_date = models.DateField()

    attachment_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = [
            "due_date",
            "title",
        ]

    def __str__(self):
        return self.title


class Submission(BaseModel):
    """
    Student submission for an assignment.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUBMITTED = "submitted", "Submitted"
        LATE = "late", "Late"

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    file_url = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "assignment",
                    "student",
                ],
                name="unique_submission_per_assignment_student",
            ),
        ]

    def __str__(self):
        return (
            f"{self.assignment.title} - "
            f"{self.student}"
        )