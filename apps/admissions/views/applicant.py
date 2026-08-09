from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from apps.core.crud import render_success
from apps.core.htmx import (
    render_modal,
    render_partial,
)
from apps.rbac.decorators import permission_required

from ..forms import ApplicantForm
from ..permissions import applicant as permissions
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

@login_required
@permission_required(**permissions.VIEW)
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


@login_required
@permission_required(**permissions.CREATE)
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

            try:

                create_applicant(
                    tenant=request.tenant,
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
            "target": "#applicant-table",
        },
    )


@login_required
@permission_required(**permissions.EDIT)
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

            try:

                update_applicant(
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
            "target": "#applicant-table",
        },
    )


@login_required
@permission_required(**permissions.DELETE)
def applicant_delete(request, pk):
    """
    Delete Applicant.
    """

    applicant = get_applicant(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        try:

            delete_applicant(
                instance=applicant,
            )

        except ValidationError as e:

            return render_modal(
                request=request,
                template="admissions/modals/delete_applicant.html",
                context={
                    "applicant": applicant,
                    "error": e.message,
                },
            )

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

    return render_modal(
        request=request,
        template="admissions/modals/delete_applicant.html",
        context={
            "applicant": applicant,
            "target": "#applicant-table",
        },
    )