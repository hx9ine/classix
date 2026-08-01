from django.shortcuts import render

from ..selectors import get_student


# ============================================================================
# Student Profile Views
# ============================================================================

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