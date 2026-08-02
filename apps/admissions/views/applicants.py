from apps.core.crud import render_success
from apps.core.htmx import (
    render_modal,
    render_partial,
)

from ..forms import ApplicantForm
from ..selectors import (
    get_applicant,
    get_applicants,
)
from ..services import (
    create_applicant,
    delete_applicant,
    update_applicant,
)


# ============================================================================
# Applicant Views
# ============================================================================

def applicant_list(request):
    """
    Applicant listing.
    """

    applicants = get_applicants(
        tenant=request.tenant,
    )

    template = (
        "admissions/partials/applicant_table.html"
        if request.htmx
        else "admissions/pages/applicants.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "applicants": applicants,
        },
    )


def applicant_create(request):
    """
    Create Applicant.
    """

    if request.method == "POST":

        form = ApplicantForm(
            request.POST,
            tenant=request.tenant,
        )

        if form.is_valid():

            create_applicant(
                tenant=request.tenant,
                form=form,
            )

            return render_success(
                request=request,
                template="admissions/partials/applicant_table.html",
                context={
                    "applicants": get_applicants(
                        tenant=request.tenant,
                    ),
                },
            )

    else:

        form = ApplicantForm(
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="admissions/modals/applicant_form.html",
        context={
            "form": form,
            "title": "New Applicant",
            "submit_label": "Create Applicant",
        },
    )


def applicant_update(request, pk):
    """
    Update Applicant.
    """

    applicant = get_applicant(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = ApplicantForm(
            request.POST,
            instance=applicant,
            tenant=request.tenant,
        )

        if form.is_valid():

            update_applicant(
                form=form,
            )

            return render_success(
                request=request,
                template="admissions/partials/applicant_table.html",
                context={
                    "applicants": get_applicants(
                        tenant=request.tenant,
                    ),
                },
            )

    else:

        form = ApplicantForm(
            instance=applicant,
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="admissions/modals/applicant_form.html",
        context={
            "form": form,
            "title": "Edit Applicant",
            "submit_label": "Save Changes",
            "applicant": applicant,
        },
    )


def applicant_delete(request, pk):
    """
    Delete Applicant.
    """

    applicant = get_applicant(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_applicant(
            instance=applicant,
        )

        return render_success(
            request=request,
            template="admissions/partials/applicant_table.html",
            context={
                "applicants": get_applicants(
                    tenant=request.tenant,
                ),
            },
        )

    return render_modal(
        request=request,
        template="admissions/modals/delete_applicant.html",
        context={
            "applicant": applicant,
        },
    )