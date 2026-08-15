from django.db.models import Exists, OuterRef, QuerySet

from apps.academics.models import TimetablePeriod
from apps.students.models import Student

from ..models import GradeEntry


def get_teacher_timetable_periods(
    *,
    tenant,
    staff,
) -> QuerySet[TimetablePeriod]:
    """
    Return timetable assignments for a teacher within the tenant.
    """

    return (
        TimetablePeriod.objects
        .filter(
            tenant=tenant,
            staff=staff,
        )
        .select_related(
            "section",
            "subject",
        )
        .order_by(
            "section__class_level__sort_order",
            "section__name",
            "subject__name",
        )
    )


def get_teacher_students(
    *,
    tenant,
    staff,
) -> QuerySet[Student]:
    """
    Return students belonging to sections assigned to the teacher.
    """

    section_ids = (
        get_teacher_timetable_periods(
            tenant=tenant,
            staff=staff,
        )
        .values("section_id")
        .distinct()
    )

    return (
        Student.objects
        .filter(
            tenant=tenant,
            section_id__in=section_ids,
        )
        .select_related(
            "section",
            "section__class_level",
        )
        .order_by(
            "first_name",
            "last_name",
        )
    )


def get_teacher_grade_entries(
    *,
    tenant,
    staff,
) -> QuerySet[GradeEntry]:
    """
    Return grade entries restricted to the teacher's
    assigned section/subject combinations.
    """

    teacher_assignment = TimetablePeriod.objects.filter(
        tenant=tenant,
        staff=staff,
        section_id=OuterRef(
            "student__section_id",
        ),
        subject_id=OuterRef(
            "subject_id",
        ),
    )

    return (
        GradeEntry.objects
        .filter(
            tenant=tenant,
        )
        .annotate(
            teacher_has_assignment=Exists(
                teacher_assignment,
            ),
        )
        .filter(
            teacher_has_assignment=True,
        )
        .select_related(
            "student",
            "student__section",
            "exam",
            "subject",
        )
        .order_by(
            "exam__start_date",
            "subject__name",
            "student__first_name",
            "student__last_name",
        )
    )