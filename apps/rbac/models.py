from django.db import models

from apps.core.models import BaseModel


class Role(BaseModel):
    """
    Represents either:

    - a system role template (tenant=None)
    - a tenant-specific cloned/custom role.
    """

    class LicenseCategory(models.TextChoices):
        ADMIN = "admin", "Admin"
        FACULTY = "faculty", "Faculty"
        STAFF = "staff", "Staff"

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="roles",
    )

    name = models.CharField(
        max_length=100,
    )

    is_admin_role = models.BooleanField(
        default=False,
        help_text=(
            "Admin roles bypass role permissions entirely and always "
            "have full access."
        ),
    )

    license_category = models.CharField(
        max_length=20,
        choices=LicenseCategory.choices,
    )

    is_editable = models.BooleanField(
        default=True,
    )

    cloned_from_role = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cloned_roles",
    )

    class Meta:
        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "name"],
                name="unique_role_name_per_tenant",
            ),
        ]

    def __str__(self):
        if self.tenant is None:
            return f"{self.name} (System)"

        return self.name


class RolePermission(BaseModel):
    """
    Permission assigned to a role.

    Admin roles ignore these rows entirely.
    """

    class Action(models.TextChoices):
        VIEW = "view", "View"
        CREATE = "create", "Create"
        EDIT = "edit", "Edit"
        DELETE = "delete", "Delete"

    class Module(models.TextChoices):
        STUDENTS = "students", "Students"
        ATTENDANCE = "attendance", "Attendance"
        ACADEMICS = "academics", "Academics"
        GRADES = "grades", "Grades"
        FEES = "fees", "Fees"
        MESSAGES = "messages", "Messages"
        STAFF = "staff", "Staff"
        CALENDAR = "calendar", "Calendar"
        LIBRARY = "library", "Library"
        TRANSPORT = "transport", "Transport"
        ADMISSIONS = "admissions", "Admissions"
        DOCUMENTS = "documents", "Documents"
        CAFETERIA = "cafeteria", "Cafeteria"
        HEALTH = "health", "Health"
        ALUMNI = "alumni", "Alumni"

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="permissions",
    )

    module = models.CharField(
        max_length=30,
        choices=Module.choices,
    )

    action = models.CharField(
        max_length=10,
        choices=Action.choices,
    )

    allowed = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = [
            "module",
            "action",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "role",
                    "module",
                    "action",
                ],
                name="unique_role_permission",
            ),
        ]

    def __str__(self):
        return (
            f"{self.role.name} | "
            f"{self.module}:{self.action}"
        )