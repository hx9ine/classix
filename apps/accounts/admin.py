from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "full_name",
        "tenant",
        "account_category",
        "is_active",
        "is_email_verified",
    )

    list_filter = (
        "tenant",
        "account_category",
        "is_active",
        "is_email_verified",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    ordering = (
        "tenant",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )