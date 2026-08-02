from django import forms

from ..models import ClassLevel


class ClassLevelForm(forms.ModelForm):
    """
    Form for creating and updating class levels.
    """

    class Meta:
        model = ClassLevel

        fields = [
            "name",
            "sort_order",
        ]