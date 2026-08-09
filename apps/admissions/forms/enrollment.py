from django import forms

from apps.academic_structure.models import (
    AcademicSession,
    Section,
)
from apps.academic_structure.selectors import get_sections_by_class


class EnrollmentForm(forms.Form):
    academic_session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.none(),
    )

    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),
    )

    roll_number = forms.CharField(
        max_length=20,
        required=False,
    )

    enrollment_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
            },
        ),
    )

    def __init__(
        self,
        *args,
        tenant,
        applicant,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.fields["academic_session"].queryset = (
            AcademicSession.objects
            .filter(
                tenant=tenant,
            )
            .order_by(
                "-start_date",
            )
        )

        self.fields["section"].queryset = (
            get_sections_by_class(
                tenant=tenant,
                class_level=applicant.applying_for_class_level,
            )
        )

        current_session = (
            self.fields["academic_session"]
            .queryset
            .filter(
                is_current=True,
            )
            .first()
        )

        if current_session and not self.is_bound:
            self.initial["academic_session"] = current_session