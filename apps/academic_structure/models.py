import uuid

from django.db import models


class AcademicSession(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="academic_sessions",
    )

    name = models.CharField(max_length=100)

    start_date = models.DateField()
    end_date = models.DateField()

    is_current = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_session"
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "name"],
                name="uq_academic_session_tenant_name",
            ),
        ]

    def __str__(self):
        return self.name


class ClassLevel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="class_levels",
    )

    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "class_level"
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "name"],
                name="uq_class_level_tenant_name",
            ),
        ]

    def __str__(self):
        return self.name


class Section(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="sections",
    )

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="sections",
    )

    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        related_name="sections",
    )

    name = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "section"
        ordering = [
            "class_level__sort_order",
            "name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tenant",
                    "academic_session",
                    "class_level",
                    "name",
                ],
                name="uq_section_tenant_session_class_name",
            ),
        ]

    def __str__(self):
        return f"{self.class_level.name} - {self.name}"