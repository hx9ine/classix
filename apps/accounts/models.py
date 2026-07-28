from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db import models

from apps.accounts.managers import UserManager
from apps.core.models import BaseModel


class AccountCategory(models.TextChoices):
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    PARENT = "parent", "Parent"
    STUDENT = "student", "Student"


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Tenant-scoped application user.
    """
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="users",
    )

    email = models.EmailField(
        blank=False,
    )

    first_name = models.CharField(
        max_length=150,
    )

    last_name = models.CharField(
        max_length=150,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    account_category = models.CharField(
        max_length=20,
        choices=AccountCategory.choices,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_email_verified = models.BooleanField(
        default=False,
    )

    is_staff = models.BooleanField(
        default=False,
        help_text="Compatibility flag for Django admin. Do not use for application authorization.",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"

        ordering = [
            "first_name",
            "last_name",
        ]

        indexes = [
            models.Index(fields=["tenant"]),
            models.Index(fields=["email"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "email"],
                name="unique_email_per_tenant",
            ),
        ]

        verbose_name = "User"
        verbose_name_plural = "Users"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


    @property
    def is_admin(self) -> bool:
        return self.account_category == AccountCategory.ADMIN


    @property
    def is_staff_user(self) -> bool:
        return self.account_category == AccountCategory.STAFF


    @property
    def is_parent(self) -> bool:
        return self.account_category == AccountCategory.PARENT


    @property
    def is_student(self) -> bool:
        return self.account_category == AccountCategory.STUDENT

    def save(self, *args, **kwargs):
        self.email = User.objects.normalize_email(self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} <{self.email}>"