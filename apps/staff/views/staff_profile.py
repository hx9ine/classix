from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.rbac.decorators import permission_required

from ..permissions import staff as permissions
from ..selectors import get_staff


# ============================================================================
# Staff Profile Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
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