from django import forms

from apps.academic_structure.models import Section
from apps.staff.models import Staff

from ..models import (
    Subject,
    TimetablePeriod,
)


class TimetablePeriodForm(forms.ModelForm):

    class Meta:
        model = TimetablePeriod

        fields = [
            "section",
            "subject",
            "staff",
            "day_of_week",
            "start_time",
            "end_time",
            "room",
        ]

        widgets = {
            "start_time": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),
            "end_time": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),
        }

    def __init__(
        self,
        *args,
        tenant,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.tenant = tenant

        self.fields["section"].queryset = (
            Section.objects
            .filter(
                tenant=tenant,
            )
            .select_related(
                "academic_session",
                "class_level",
            )
            .order_by(
                "class_level__sort_order",
                "name",
            )
        )

        self.fields["subject"].queryset = (
            Subject.objects
            .filter(
                tenant=tenant,
            )
            .order_by(
                "name",
            )
        )

        self.fields["staff"].queryset = (
            Staff.objects
            .filter(
                tenant=tenant,
            )
            .order_by(
                "first_name",
                "last_name",
            )
        )

    def clean_day_of_week(self):
        day_of_week = self.cleaned_data["day_of_week"]

        if not 0 <= day_of_week <= 6:
            raise forms.ValidationError(
                "Select a valid day of the week."
            )

        return day_of_week

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if (
            start_time is not None
            and end_time is not None
            and start_time >= end_time
        ):
            self.add_error(
                "end_time",
                "End time must be later than start time.",
            )

        return cleaned_data

    def clean_section(self):
        section = self.cleaned_data["section"]

        if section.tenant_id != self.tenant.pk:
            raise forms.ValidationError(
                "Invalid section selected."
            )

        return section

    def clean_subject(self):
        subject = self.cleaned_data["subject"]

        if subject.tenant_id != self.tenant.pk:
            raise forms.ValidationError(
                "Invalid subject selected."
            )

        return subject

    def clean_staff(self):
        staff = self.cleaned_data["staff"]

        if staff.tenant_id != self.tenant.pk:
            raise forms.ValidationError(
                "Invalid staff member selected."
            )

        return staff