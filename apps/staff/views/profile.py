from django.shortcuts import render

from ..selectors import get_staff


# ============================================================================
# Staff Profile Views
# ============================================================================

def staff_detail(request, pk):
    """
    Display a staff member's profile.
    """

    staff = get_staff(
        tenant=request.tenant,
        pk=pk,
    )

    return render(
        request,
        "staff/pages/staff_profile.html",
        {
            "staff": staff,
        },
    )