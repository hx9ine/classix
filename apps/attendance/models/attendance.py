import uuid

from django.db import models

from apps.core.models import BaseModel


class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"
    EXCUSED = "excused", "Excused"


class AttendanceRecord(BaseModel):
    """
    Attendance record for a student.

    A NULL period represents daily attendance.
    A TimetablePeriod represents period-wise attendance.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    section = models.ForeignKey(
        "academic_structure.Section",
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    date = models.DateField()

    period = models.ForeignKey(
        "academics.TimetablePeriod",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_records",
    )

    status = models.CharField(
        max_length=10,
        choices=AttendanceStatus.choices,
    )

    marked_by = models.ForeignKey(
        "staff.Staff",
        on_delete=models.PROTECT,
        related_name="marked_attendance_records",
    )

    note = models.TextField(
        null=True,
        blank=True,
    )

    academic_session = models.ForeignKey(
        "academic_structure.AcademicSession",
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    class Meta:
        db_table = "attendance_record"

        ordering = [
            "date",
            "student__student_code",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "date",
                    "period",
                ],
                name="uq_attendance_student_date_period",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.date} - "
            f"{self.get_status_display()}"
        )