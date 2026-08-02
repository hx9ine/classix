from django import forms

from ..models import Subject


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject

        fields = [
            "name",
            "code",
        ]

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()