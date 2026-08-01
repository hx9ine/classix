from django import forms

from .models import Role


class RoleForm(forms.ModelForm):
    """
    Role create/update form.

    Billing-related fields and system flags are intentionally
    excluded from user-editable forms.
    """

    class Meta:
        model = Role

        fields = [
            "name",
        ]

    def __init__(self, *args, tenant, **kwargs):
        super().__init__(*args, **kwargs)

        self.tenant = tenant

    def clean_name(self):
        return self.cleaned_data["name"].strip()