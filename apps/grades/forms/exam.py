from django import forms

from apps.academic_structure.models import AcademicSession

from ..models import Exam


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam

        fields = [
            "name",
            "academic_session",
            "start_date",
            "end_date",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                },
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                },
            ),
        }

    def __init__(
        self,
        *args,
        tenant,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.tenant = tenant

        self.fields["academic_session"].queryset = (
            AcademicSession.objects
            .filter(
                tenant=tenant,
            )
            .order_by(
                "-start_date",
            )
        )

    def clean_academic_session(self):
        academic_session = self.cleaned_data["academic_session"]

        if academic_session.tenant_id != self.tenant.pk:
            raise forms.ValidationError(
                "Invalid academic session selected."
            )

        return academic_session

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if (
            start_date
            and end_date
            and end_date < start_date
        ):
            raise forms.ValidationError(
                "End date cannot be earlier than start date."
            )

        return cleaned_data