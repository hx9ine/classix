from django.db import models

from apps.core.models import BaseModel


class Tenant(BaseModel):
    class SubscriptionTier(models.TextChoices):
        BASIC = "basic", "Basic"
        PRO = "pro", "Pro"
        ULTRA = "ultra", "Ultra"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        CANCELLED = "cancelled", "Cancelled"

    school_name = models.CharField(
        max_length=255,
    )

    subdomain_slug = models.SlugField(
        max_length=63,
        unique=True,
    )

    custom_domain = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    subscription_tier = models.CharField(
        max_length=10,
        choices=SubscriptionTier.choices,
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    admin_license_limit = models.PositiveIntegerField()

    faculty_license_limit = models.PositiveIntegerField()

    staff_license_limit = models.PositiveIntegerField()

    student_license_limit = models.PositiveIntegerField()

    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["school_name"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self):
        return self.school_name