from django import forms

from ..models import AcademicSession


class AcademicSessionForm(forms.ModelForm):
    """
    Form for creating and updating academic sessions.
    """

    class Meta:
        model = AcademicSession

        fields = [
            "name",
            "start_date",
            "end_date",
            "is_current",
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