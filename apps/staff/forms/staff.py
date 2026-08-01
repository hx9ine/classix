from django import forms

from apps.rbac.models import Role

from ..models import Staff


class StaffForm(forms.ModelForm):

    joining_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        )
    )

    class Meta:
        model = Staff

        fields = [
            "first_name",
            "last_name",
            "role",
            "joining_date",
            "phone",
            "photo_url",
        ]

    def __init__(self, *args, tenant, **kwargs):
        super().__init__(*args, **kwargs)

        self.tenant = tenant

        self.fields["role"].queryset = (
            Role.objects.filter(
                tenant__in=[tenant, None],
            )
            .order_by("name")
        )

    def clean_role(self):
        role = self.cleaned_data["role"]

        if role.tenant and role.tenant != self.tenant:
            raise forms.ValidationError(
                "Invalid role selected."
            )

        return role

    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip()

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if phone:
            phone = phone.strip()

        return phone