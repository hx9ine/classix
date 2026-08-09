from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404

from apps.core.crud import render_success
from apps.core.htmx import render_modal
from apps.rbac.decorators import permission_required

from ..forms import EnrollmentForm
from ..permissions import enrollment as permissions
from ..selectors import (
    get_applicant,
    get_applicants,
)
from ..services.enrollment import enroll_applicant


# ============================================================================
# Enrollment Views
# ============================================================================

@login_required
@permission_required(**permissions.CREATE)
def applicant_enroll(request, pk):
    """
    Enroll an accepted applicant as a student.
    """

    applicant = get_applicant(
        tenant=request.tenant,
        pk=pk,
    )

    if applicant.status != applicant.Status.ACCEPTED:
        raise Http404(
            "Applicant cannot be enrolled."
        )

    if request.method == "POST":

        form = EnrollmentForm(
            request.POST,
            tenant=request.tenant,
            applicant=applicant,
        )

        if form.is_valid():

            try:

                enroll_applicant(
                    tenant=request.tenant,
                    applicant=applicant,
                    form=form,
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_success(
                    request=request,
                    template="admissions/partials/applicant_table.html",
                    context={
                        "applicants": get_applicants(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = EnrollmentForm(
            tenant=request.tenant,
            applicant=applicant,
        )

    return render_modal(
        request=request,
        template="admissions/modals/enroll_applicant.html",
        context={
            "form": form,
            "applicant": applicant,
            "title": "Enroll Applicant",
            "submit_label": "Enroll Student",
            "target": "#applicant-table",
        },
    )