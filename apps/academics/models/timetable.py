from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from apps.core.models import BaseModel


class TimetablePeriod(BaseModel):
    """
    Represents a scheduled teaching period for a section.
    """

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="timetable_periods",
    )

    section = models.ForeignKey(
        "academic_structure.Section",
        on_delete=models.CASCADE,
        related_name="timetable_periods",
    )

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="timetable_periods",
    )

    staff = models.ForeignKey(
        "staff.Staff",
        on_delete=models.CASCADE,
        related_name="timetable_periods",
    )

    day_of_week = models.PositiveSmallIntegerField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    room = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = [
            "day_of_week",
            "start_time",
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    day_of_week__gte=0,
                    day_of_week__lte=6,
                ),
                name="timetable_period_day_of_week_valid",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "tenant",
                    "section",
                    "day_of_week",
                ],
            ),
            models.Index(
                fields=[
                    "tenant",
                    "staff",
                    "day_of_week",
                ],
            ),
        ]

    def __str__(self):
        return (
            f"{self.section} - "
            f"{self.subject} - "
            f"{self.start_time:%H:%M}"
        )

    def clean(self):
        super().clean()

        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time >= self.end_time
        ):
            raise ValidationError(
                {
                    "end_time": (
                        "End time must be later than start time."
                    ),
                }
            )

    @property
    def update_url(self):
        return reverse(
            "academics:timetable_update",
            kwargs={
                "pk": self.pk,
            },
        )

    @property
    def delete_url(self):
        return reverse(
            "academics:timetable_delete",
            kwargs={
                "pk": self.pk,
            },
        )