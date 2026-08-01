from django import forms

from ..models import ClassLevel


class ClassLevelForm(forms.ModelForm):
    class Meta:
        model = ClassLevel
        fields = [
            "name",
            "sort_order",
        ]

    def clean_name(self):
        return self.cleaned_data["name"].strip()

