from django.db.models import Max

from ..models import Student


def generate_student_code(*, tenant) -> str:
    """
    Generate the next student code for a tenant.

    Format:
        STU-000001
        STU-000002
        STU-000003
    """

    latest = (
        Student.objects.filter(
            tenant=tenant,
            student_code__startswith="STU-",
        )
        .order_by("-student_code")
        .first()
    )

    if latest is None:
        next_number = 1
    else:
        next_number = int(
            latest.student_code.replace("STU-", "")
        ) + 1

    return f"STU-{next_number:06d}"