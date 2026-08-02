from django import forms

from ..models import (
    AcademicSession,
    ClassLevel,
    Section,
)


class SectionForm(forms.ModelForm):
    """
    Form for creating and updating sections.
    """

    class Meta:
        model = Section

        fields = [
            "academic_session",
            "class_level",
            "name",
        ]

    def __init__(
        self,
        *args,
        tenant,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.fields["academic_session"].queryset = (
            AcademicSession.objects.filter(
                tenant=tenant,
            ).order_by(
                "-start_date",
            )
        )

        self.fields["class_level"].queryset = (
            ClassLevel.objects.filter(
                tenant=tenant,
            ).order_by(
                "sort_order",
                "name",
            )
        )