from django import forms

from ..models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student

        fields = [
            "first_name",
            "last_name",
            "dob",
            "gender",
            "academic_session",
            "section",
            "roll_number",
            "blood_group",
            "address",
            "previous_school",
        ]

        widgets = {
            "dob": forms.DateInput(
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

        self.fields["academic_session"].queryset = (
            self.fields["academic_session"]
            .queryset
            .filter(
                tenant=tenant,
            )
            .order_by(
                "-start_date",
            )
        )

        self.fields["section"].queryset = (
            self.fields["section"]
            .queryset
            .filter(
                tenant=tenant,
            )
            .select_related(
                "class_level",
            )
            .order_by(
                "class_level__sort_order",
                "name",
            )
        )

    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip()

    def clean_roll_number(self):
        roll_number = self.cleaned_data.get(
            "roll_number",
        )

        if roll_number:
            return roll_number.strip()

        return roll_number