from django.shortcuts import get_object_or_404

from ..models import Student


# ============================================================================
# Student Selectors
# ============================================================================

def get_students(tenant):
    """
    Return all students for a tenant.
    """
    return (
        Student.objects
        .filter(tenant=tenant)
        .select_related(
            "academic_session",
            "section",
            "section__class_level",
        )
        .order_by(
            "student_code",
        )
    )


def get_student(tenant, pk):
    """
    Return a single student.
    """
    return get_object_or_404(
        Student.objects.select_related(
            "academic_session",
            "section",
            "section__class_level",
        ),
        tenant=tenant,
        pk=pk,
    )


def get_students_by_section(
    *,
    tenant,
    section,
):
    """
    Return all students in a section.
    """
    return (
        Student.objects
        .filter(
            tenant=tenant,
            section=section,
        )
        .select_related(
            "academic_session",
            "section",
            "section__class_level",
        )
        .order_by(
            "roll_number",
            "student_code",
        )
    )