from django import forms
from django.db import models

from apps.accounts.models import AccountCategory, User


class StaffUserAssignmentForm(forms.Form):
    """
    Form for assigning an existing portal user to a staff profile.
    """

    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Portal User",
        empty_label="Select a user",
    )

    def __init__(
        self,
        *args,
        tenant,
        instance=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.tenant = tenant
        self.instance = instance

        queryset = (
            User.objects
            .filter(
                tenant=tenant,
                is_active=True,
                account_category__in=[
                    AccountCategory.ADMIN,
                    AccountCategory.STAFF,
                ],
            )
            .order_by(
                "first_name",
                "last_name",
            )
        )

        if instance is not None and instance.user_id:

            queryset = queryset.filter(
                models.Q(
                    staff_profile__isnull=True,
                )
                | models.Q(
                    pk=instance.user_id,
                )
            )

        else:

            queryset = queryset.filter(
                staff_profile__isnull=True,
            )

        self.fields["user"].queryset = queryset