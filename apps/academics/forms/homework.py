from django import forms

from apps.academic_structure.models import Section
from apps.staff.models import Staff

from ..models import Assignment, Subject


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment

        fields = [
            "title",
            "description",
            "section",
            "subject",
            "staff",
            "due_date",
            "attachment_url",
        ]

        widgets = {
            "due_date": forms.DateInput(
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

        self.tenant = tenant

        self.fields["section"].queryset = (
            Section.objects
            .filter(
                tenant=tenant,
            )
            .select_related(
                "academic_session",
                "class_level",
            )
            .order_by(
                "class_level__sort_order",
                "name",
            )
        )

        self.fields["subject"].queryset = (
            Subject.objects
            .filter(
                tenant=tenant,
            )
            .order_by(
                "name",
            )
        )

        self.fields["staff"].queryset = (
            Staff._base_manager
            .filter(
                tenant=tenant,
            )
            .select_related(
                "role",
            )
            .order_by(
                "first_name",
                "last_name",
            )
        )

    def clean_section(self):
        section = self.cleaned_data["section"]

        if section.tenant_id != self.tenant.pk:
            raise forms.ValidationError(
                "Invalid section selected."
            )

        return section

    def clean_subject(self):
        subject = self.cleaned_data["subject"]

        if subject.tenant_id != self.tenant.pk:
            raise forms.ValidationError(
                "Invalid subject selected."
            )

        return subject

    def clean_staff(self):
        staff = self.cleaned_data["staff"]

        if staff.tenant_id != self.tenant.pk:
            raise forms.ValidationError(
                "Invalid staff member selected."
            )

        return staff

    def clean_title(self):
        return self.cleaned_data["title"].strip()

    def clean_description(self):
        return self.cleaned_data["description"].strip()

    def clean_attachment_url(self):
        attachment_url = self.cleaned_data.get(
            "attachment_url",
        )

        if attachment_url:
            attachment_url = attachment_url.strip()

        return attachment_url