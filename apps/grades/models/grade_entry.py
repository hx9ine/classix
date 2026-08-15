from django.db import models

from apps.core.models import BaseModel


class GradeEntry(BaseModel):
    """
    Represents a student's marks for a subject
    within an exam.
    """

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="grade_entries",
    )

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="grade_entries",
    )

    exam = models.ForeignKey(
        "grades.Exam",
        on_delete=models.CASCADE,
        related_name="grade_entries",
    )

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="grade_entries",
    )

    marks_obtained = models.DecimalField(
        max_digits=7,
        decimal_places=2,
    )

    max_marks = models.DecimalField(
        max_digits=7,
        decimal_places=2,
    )

    grade_letter = models.CharField(
        max_length=10,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = [
            "exam",
            "subject",
            "student",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "exam",
                    "subject",
                ],
                name="uq_grade_entry_student_exam_subject",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.subject} - "
            f"{self.exam}"
        )