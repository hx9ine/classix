from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import AttendanceRecord


# ============================================================================
# Attendance Selectors
# ============================================================================

def get_attendance_records(
    *,
    tenant,
) -> QuerySet[AttendanceRecord]:
    """
    Return all attendance records for a tenant.
    """

    return (
        AttendanceRecord.objects
        .filter(
            tenant=tenant,
        )
        .select_related(
            "student",
            "section",
            "section__class_level",
            "period",
            "period__subject",
            "period__staff",
            "marked_by",
            "academic_session",
        )
        .order_by(
            "-date",
            "student__student_code",
        )
    )


def get_attendance_records_by_date(
    *,
    tenant,
    date,
) -> QuerySet[AttendanceRecord]:
    """
    Return attendance records for a tenant and date.
    """

    return (
        get_attendance_records(
            tenant=tenant,
        )
        .filter(
            date=date,
        )
    )


def get_attendance_records_by_section(
    *,
    tenant,
    section,
    date,
    period=None,
) -> QuerySet[AttendanceRecord]:
    """
    Return attendance records for a section, date,
    and optional timetable period.
    """

    queryset = (
        get_attendance_records(
            tenant=tenant,
        )
        .filter(
            section=section,
            date=date,
        )
    )

    if period is None:
        return queryset.filter(
            period__isnull=True,
        )

    return queryset.filter(
        period=period,
    )


def get_attendance_record(
    *,
    tenant,
    pk,
) -> AttendanceRecord:
    """
    Return a single attendance record.
    """

    return get_object_or_404(
        get_attendance_records(
            tenant=tenant,
        ),
        pk=pk,
    )


def get_student_attendance(
    *,
    tenant,
    student,
) -> QuerySet[AttendanceRecord]:
    """
    Return attendance history for a student.
    """

    return (
        get_attendance_records(
            tenant=tenant,
        )
        .filter(
            student=student,
        )
        .order_by(
            "-date",
            "-period__start_time",
        )
    )


def get_student_attendance_by_date(
    *,
    tenant,
    student,
    date,
) -> QuerySet[AttendanceRecord]:
    """
    Return a student's attendance for a date.
    """

    return (
        get_student_attendance(
            tenant=tenant,
            student=student,
        )
        .filter(
            date=date,
        )
    )


def get_student_attendance_for_period(
    *,
    tenant,
    student,
    date,
    period,
) -> AttendanceRecord | None:
    """
    Return a student's attendance record for a
    specific date and timetable period.
    """

    return (
        get_attendance_records(
            tenant=tenant,
        )
        .filter(
            student=student,
            date=date,
            period=period,
        )
        .first()
    )



from apps.students.models import Student
from apps.academic_structure.models import Section


def get_attendance_sections(
    *,
    tenant,
    staff=None,
):
    """
    Return sections available for attendance.

    Admin roles can see all tenant sections.
    Non-admin staff members are restricted to sections
    for which they have timetable assignments.
    """

    queryset = (
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

    if staff is None:
        return queryset.none()

    if staff.role.is_admin_role:
        return queryset

    return queryset.filter(
        timetable_periods__tenant=tenant,
        timetable_periods__staff=staff,
    ).distinct()


def get_attendance_roster(
    *,
    tenant,
    section,
):
    """
    Return active students belonging to the selected section.
    """

    return (
        Student.objects
        .filter(
            tenant=tenant,
            section=section,
            status="active",
        )
        .order_by(
            "student_code",
        )
    )