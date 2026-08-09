from django.db import transaction

from apps.students.models import (
    Student,
    StudentStatus,
)
from apps.students.services.student_codes import (
    generate_student_code,
)

from ..models import Applicant


# ============================================================================
# Enrollment Services
# ============================================================================

@transaction.atomic
def enroll_applicant(
    *,
    tenant,
    applicant: Applicant,
    form,
) -> Student:
    """
    Enroll an applicant as a student.
    """

    student = Student.objects.create(
        tenant=tenant,
        student_code=generate_student_code(
            tenant=tenant,
        ),
        first_name=applicant.first_name,
        last_name=applicant.last_name,
        dob=applicant.dob,
        gender=applicant.gender,
        academic_session=form.cleaned_data["academic_session"],
        section=form.cleaned_data["section"],
        roll_number=form.cleaned_data["roll_number"],
        enrollment_date=form.cleaned_data["enrollment_date"],
        status=StudentStatus.ACTIVE,
    )

    applicant.status = Applicant.Status.ENROLLED
    applicant.linked_student = student

    applicant.save(
        update_fields=[
            "status",
            "linked_student",
        ],
    )

    return student