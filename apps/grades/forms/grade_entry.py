from django import forms

from apps.academics.models import Subject, TimetablePeriod
from apps.students.models import Student

from ..models import Exam, GradeEntry
from ..selectors.teacher_scope import (
    get_teacher_students,
)


class GradeEntryForm(forms.ModelForm):
    class Meta:
        model = GradeEntry

        fields = [
            "student",
            "exam",
            "subject",
            "marks_obtained",
            "max_marks",
            "grade_letter",
            "remarks",
        ]

    def __init__(
        self,
        *args,
        tenant,
        staff=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.tenant = tenant
        self.staff = staff

        self.fields["student"].queryset = (
            Student.objects
            .filter(
                tenant=tenant,
            )
            .select_related(
                "section",
            )
            .order_by(
                "first_name",
                "last_name",
            )
        )

        self.fields["exam"].queryset = (
            Exam.objects
            .filter(
                tenant=tenant,
            )
            .select_related(
                "academic_session",
            )
            .order_by(
                "-start_date",
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

        if staff is not None:
            self.fields["student"].queryset = (
                get_teacher_students(
                    tenant=tenant,
                    staff=staff,
                )
            )

            self.fields["subject"].queryset = (
                Subject.objects
                .filter(
                    tenant=tenant,
                    timetable_periods__tenant=tenant,
                    timetable_periods__staff=staff,
                )
                .distinct()
                .order_by(
                    "name",
                )
            )

    def clean_student(self):
        student = self.cleaned_data["student"]

        if student.tenant_id != self.tenant.pk:
            raise forms.ValidationError(
                "Invalid student selected."
            )

        return student

    def clean_exam(self):
        exam = self.cleaned_data["exam"]

        if exam.tenant_id != self.tenant.pk:
            raise forms.ValidationError(
                "Invalid exam selected."
            )

        return exam

    def clean_subject(self):
        subject = self.cleaned_data["subject"]

        if subject.tenant_id != self.tenant.pk:
            raise forms.ValidationError(
                "Invalid subject selected."
            )

        return subject

    def clean_marks_obtained(self):
        marks_obtained = self.cleaned_data["marks_obtained"]

        if marks_obtained < 0:
            raise forms.ValidationError(
                "Marks obtained cannot be negative."
            )

        return marks_obtained

    def clean_max_marks(self):
        max_marks = self.cleaned_data["max_marks"]

        if max_marks <= 0:
            raise forms.ValidationError(
                "Maximum marks must be greater than zero."
            )

        return max_marks

    def clean_grade_letter(self):
        return self.cleaned_data["grade_letter"].strip()

    def clean_remarks(self):
        return self.cleaned_data["remarks"].strip()

    def clean(self):
        cleaned_data = super().clean()

        student = cleaned_data.get("student")
        subject = cleaned_data.get("subject")
        marks_obtained = cleaned_data.get("marks_obtained")
        max_marks = cleaned_data.get("max_marks")

        if (
            marks_obtained is not None
            and max_marks is not None
            and marks_obtained > max_marks
        ):
            self.add_error(
                "marks_obtained",
                "Marks obtained cannot exceed maximum marks.",
            )

        if (
            self.staff is not None
            and student is not None
            and subject is not None
        ):
            has_assignment = (
                TimetablePeriod.objects
                .filter(
                    tenant=self.tenant,
                    staff=self.staff,
                    section_id=student.section_id,
                    subject=subject,
                )
                .exists()
            )

            if not has_assignment:
                raise forms.ValidationError(
                    "You can only enter grades for your assigned "
                    "sections and subjects."
                )

        return cleaned_data