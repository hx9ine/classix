from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import Student
from ..selectors import (
    roll_number_exists,
    student_code_exists,
)


# ============================================================================
# Create
# ============================================================================

@transaction.atomic
def create_student(
    *,
    tenant,
    student_code,
    first_name,
    last_name,
    dob,
    gender,
    academic_session,
    section,
    roll_number,
    enrollment_date,
    blood_group,
    address,
    previous_school,
):
    """
    Create a student.
    """

    student_code = student_code.strip().upper()
    first_name = first_name.strip()
    last_name = last_name.strip()

    if roll_number:
        roll_number = roll_number.strip()

    if student_code_exists(
        tenant=tenant,
        student_code=student_code,
    ):
        raise ValidationError(
            "A student with this code already exists."
        )

    if roll_number_exists(
        tenant=tenant,
        section=section,
        roll_number=roll_number,
    ):
        raise ValidationError(
            "This roll number already exists in the selected section."
        )

    student = Student(
        tenant=tenant,
        student_code=student_code,
        first_name=first_name,
        last_name=last_name,
        dob=dob,
        gender=gender,
        academic_session=academic_session,
        section=section,
        roll_number=roll_number,
        enrollment_date=enrollment_date,
        blood_group=blood_group,
        address=address,
        previous_school=previous_school,
    )

    student.full_clean()
    student.save()

    return student


# ============================================================================
# Update
# ============================================================================

@transaction.atomic
def update_student(
    *,
    student,
    first_name,
    last_name,
    dob,
    gender,
    academic_session,
    section,
    roll_number,
    blood_group,
    address,
    previous_school,
):
    """
    Update a student.
    """

    first_name = first_name.strip()
    last_name = last_name.strip()

    if roll_number:
        roll_number = roll_number.strip()

    if roll_number_exists(
        tenant=student.tenant,
        section=section,
        roll_number=roll_number,
        exclude_pk=student.pk,
    ):
        raise ValidationError(
            "This roll number already exists in the selected section."
        )

    student.first_name = first_name
    student.last_name = last_name
    student.dob = dob
    student.gender = gender
    student.academic_session = academic_session
    student.section = section
    student.roll_number = roll_number
    student.blood_group = blood_group
    student.address = address
    student.previous_school = previous_school

    student.full_clean()
    student.save()

    return student


# ============================================================================
# Delete
# ============================================================================

@transaction.atomic
def delete_student(
    *,
    student,
):
    """
    Delete a student.

    NOTE:
    Once Attendance, Grades, Fees and other
    modules depend on students, this should
    become a soft delete or include dependency
    checks.
    """

    student.delete()