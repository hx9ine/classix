from django import forms

from apps.academic_structure.models import ClassLevel

from ..models import Applicant


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = [
            "first_name",
            "last_name",
            "dob",
            "gender",
            "applying_for_class_level",
            "guardian_name",
            "guardian_phone",
            "guardian_email",
            "status",
            "entrance_score",
        ]

        widgets = {
            "dob": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, tenant, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["applying_for_class_level"].queryset = (
            ClassLevel.objects.filter(
                tenant=tenant,
            ).order_by(
                "sort_order",
                "name",
            )
        )

    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip()

    def clean_guardian_name(self):
        return self.cleaned_data["guardian_name"].strip()

    def clean_guardian_phone(self):
        return self.cleaned_data["guardian_phone"].strip()

    def clean_guardian_email(self):
        return (
            self.cleaned_data["guardian_email"]
            .strip()
            .lower()
        )