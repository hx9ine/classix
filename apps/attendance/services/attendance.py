from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import AttendanceRecord


# ============================================================================
# Validation
# ============================================================================

def _validate_tenant_scope(
    *,
    tenant,
    section,
    academic_session,
    marked_by,
    student=None,
    period=None,
):
    """
    Ensure all supplied tenant-owned objects belong
    to the current tenant.
    """

    objects = [
        ("section", section),
        ("academic_session", academic_session),
        ("marked_by", marked_by),
    ]

    if student is not None:
        objects.append(
            ("student", student),
        )

    if period is not None:
        objects.append(
            ("period", period),
        )

    for name, obj in objects:

        if obj.tenant_id != tenant.pk:
            raise ValidationError(
                f"The selected {name} does not belong to the current tenant."
            )


def _validate_student_section(
    *,
    student,
    section,
):
    """
    Ensure the student currently belongs to the
    selected section.
    """

    if student.section_id != section.pk:
        raise ValidationError(
            "The selected student does not belong to the selected section."
        )


def _validate_student_session(
    *,
    student,
    academic_session,
):
    """
    Ensure the student belongs to the selected
    academic session.
    """

    if student.academic_session_id != academic_session.pk:
        raise ValidationError(
            "The selected student does not belong to the selected academic session."
        )


def _validate_period_section(
    *,
    period,
    section,
):
    """
    Ensure a timetable period belongs to the
    selected section.
    """

    if period.section_id != section.pk:
        raise ValidationError(
            "The selected timetable period does not belong to the selected section."
        )


# ============================================================================
# Create
# ============================================================================

@transaction.atomic
def create_attendance_record(
    *,
    tenant,
    student,
    section,
    date,
    period,
    status,
    marked_by,
    note,
    academic_session,
):
    """
    Create a single attendance record.
    """

    _validate_tenant_scope(
        tenant=tenant,
        student=student,
        section=section,
        academic_session=academic_session,
        marked_by=marked_by,
        period=period,
    )

    _validate_student_section(
        student=student,
        section=section,
    )

    _validate_student_session(
        student=student,
        academic_session=academic_session,
    )

    if period is not None:
        _validate_period_section(
            period=period,
            section=section,
        )

    if AttendanceRecord.objects.filter(
        tenant=tenant,
        student=student,
        date=date,
        period=period,
    ).exists():

        raise ValidationError(
            "Attendance has already been marked for this student, date, and period."
        )

    attendance_record = AttendanceRecord(
        tenant=tenant,
        student=student,
        section=section,
        date=date,
        period=period,
        status=status,
        marked_by=marked_by,
        note=note,
        academic_session=academic_session,
    )

    attendance_record.full_clean()
    attendance_record.save()

    return attendance_record


# ============================================================================
# Update
# ============================================================================

@transaction.atomic
def update_attendance_record(
    *,
    attendance_record,
    status,
    note,
):
    """
    Update an existing attendance record.

    Audit logging for past attendance edits is intentionally
    deferred until the Audit module provides its service API.
    """

    attendance_record.status = status
    attendance_record.note = note

    attendance_record.full_clean()
    attendance_record.save(
        update_fields=[
            "status",
            "note",
            "updated_at",
        ],
    )

    return attendance_record


# ============================================================================
# Bulk Marking
# ============================================================================

@transaction.atomic
def mark_attendance(
    *,
    tenant,
    section,
    date,
    period,
    academic_session,
    marked_by,
    attendance,
):
    """
    Create or update attendance records for a roster.

    `attendance` must contain dictionaries in the form:

        {
            "student": student,
            "status": status,
            "note": note,
        }

    Existing records are updated.
    Missing records are created.

    This supports the roster workflow where attendance
    defaults to Present and only exceptions need changing.
    """

    _validate_tenant_scope(
        tenant=tenant,
        section=section,
        academic_session=academic_session,
        marked_by=marked_by,
        period=period,
    )

    if period is not None:
        _validate_period_section(
            period=period,
            section=section,
        )

    records = []

    for entry in attendance:

        student = entry["student"]
        status = entry["status"]
        note = entry.get("note")

        _validate_tenant_scope(
            tenant=tenant,
            student=student,
            section=section,
            academic_session=academic_session,
            marked_by=marked_by,
            period=period,
        )

        _validate_student_section(
            student=student,
            section=section,
        )

        _validate_student_session(
            student=student,
            academic_session=academic_session,
        )

        record = (
            AttendanceRecord.objects
            .filter(
                tenant=tenant,
                student=student,
                date=date,
                period=period,
            )
            .first()
        )

        if record is None:

            record = AttendanceRecord(
                tenant=tenant,
                student=student,
                section=section,
                date=date,
                period=period,
                status=status,
                marked_by=marked_by,
                note=note,
                academic_session=academic_session,
            )

        else:

            record.status = status
            record.note = note
            record.marked_by = marked_by
            record.academic_session = academic_session

        record.full_clean()
        record.save()

        records.append(record)

    return records


# ============================================================================
# Delete
# ============================================================================

@transaction.atomic
def delete_attendance_record(
    *,
    attendance_record,
):
    """
    Delete an attendance record.
    """

    attendance_record.delete()