from django import forms

from apps.rbac.models import Role

from .models import Staff


class BaseStaffForm(forms.ModelForm):
    """
    Shared validation for staff forms.
    """

    class Meta:
        model = Staff

        fields = [
            "user",
            "first_name",
            "last_name",
            "photo",
            "role",
            "joining_date",
            "phone",
        ]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.tenant = tenant

        if tenant:
            self.fields["role"].queryset = Role.objects.filter(
                tenant__in=[tenant, None]
            )

    def clean_role(self):
        role = self.cleaned_data["role"]

        if role.tenant and role.tenant != self.tenant:
            raise forms.ValidationError(
                "Invalid role selected."
            )

        return role

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")

        if phone:
            phone = phone.strip()

        return phone


class StaffCreateForm(BaseStaffForm):
    """
    Create form.
    """

    pass


class StaffUpdateForm(BaseStaffForm):
    """
    Update form.
    """

    pass