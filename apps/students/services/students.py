from django.db import transaction


# ============================================================================
# Student Services
# ============================================================================

@transaction.atomic
def update_student(
    *,
    form,
):
    """
    Update a student.
    """
    return form.save()