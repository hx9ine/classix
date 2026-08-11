from datetime import date

from django import forms

from apps.academic_structure.models import Section
from apps.academics.models import TimetablePeriod
from apps.students.models import Student

from ..models import AttendanceStatus


class AttendanceMarkingForm(forms.Form):
    """
    Form for marking attendance for a section roster.

    Student status fields are added dynamically from the
    students supplied to the form.
    """

    date = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(
            attrs={
                "type": "date",
            },
        ),
    )

    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
    )

    period = forms.ModelChoiceField(
        queryset=TimetablePeriod.objects.none(),
        required=False,
        empty_label="Daily Attendance",
    )

    def __init__(
        self,
        *args,
        tenant,
        students=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.tenant = tenant
        self.students = list(students or [])

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

        self.fields["period"].queryset = (
            TimetablePeriod.objects
            .filter(
                tenant=tenant,
            )
            .select_related(
                "section",
                "subject",
                "staff",
            )
            .order_by(
                "day_of_week",
                "start_time",
            )
        )

        for student in self.students:

            self.fields[
                self.status_field_name(student)
            ] = forms.ChoiceField(
                choices=AttendanceStatus.choices,
                initial=AttendanceStatus.PRESENT,
                widget=forms.RadioSelect,
            )

            self.fields[
                self.note_field_name(student)
            ] = forms.CharField(
                required=False,
                widget=forms.TextInput(
                    attrs={
                        "placeholder": "Optional note",
                    },
                ),
            )

    @staticmethod
    def status_field_name(student):
        return f"status_{student.pk}"

    @staticmethod
    def note_field_name(student):
        return f"note_{student.pk}"

    def clean(self):
        cleaned_data = super().clean()

        section = cleaned_data.get("section")
        period = cleaned_data.get("period")

        if period is not None and section is not None:
            if period.section_id != section.pk:
                self.add_error(
                    "period",
                    "The selected period does not belong to the selected section.",
                )

        return cleaned_data

    def get_student_status(self, student):
        return self.cleaned_data.get(
            self.status_field_name(student),
        )

    def get_student_note(self, student):
        return self.cleaned_data.get(
            self.note_field_name(student),
        )