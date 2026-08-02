from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.rbac.decorators import permission_required

from ..permissions import student as permissions
from ..selectors import get_student


# ============================================================================
# Student Profile Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
def student_detail(request, pk):
    """
    Display a student's profile.
    """

    student = get_student(
        tenant=request.tenant,
        pk=pk,
    )

    return render(
        request,
        "students/pages/student_profile.html",
        {
            "student": student,
        },
    )