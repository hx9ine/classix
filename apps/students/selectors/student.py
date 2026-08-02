from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import Student


# ============================================================================
# Student Selectors
# ============================================================================

def get_students(
    *,
    tenant,
) -> QuerySet[Student]:
    """
    Return all students for a tenant.
    """

    return (
        Student.objects
        .filter(
            tenant=tenant,
        )
        .select_related(
            "academic_session",
            "section",
            "section__class_level",
        )
        .order_by(
            "student_code",
        )
    )


def get_student(
    *,
    tenant,
    pk,
) -> Student:
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
) -> QuerySet[Student]:
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


def student_code_exists(
    *,
    tenant,
    student_code,
    exclude_pk=None,
) -> bool:
    """
    Check whether a student code already exists.
    """

    queryset = Student.objects.filter(
        tenant=tenant,
        student_code=student_code,
    )

    if exclude_pk:
        queryset = queryset.exclude(
            pk=exclude_pk,
        )

    return queryset.exists()


def roll_number_exists(
    *,
    tenant,
    section,
    roll_number,
    exclude_pk=None,
) -> bool:
    """
    Check whether a roll number already exists
    within a section.
    """

    if not roll_number:
        return False

    queryset = Student.objects.filter(
        tenant=tenant,
        section=section,
        roll_number=roll_number,
    )

    if exclude_pk:
        queryset = queryset.exclude(
            pk=exclude_pk,
        )

    return queryset.exists()