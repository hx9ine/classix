from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from apps.core.crud import render_success
from apps.core.htmx import (
    render_modal,
    render_partial,
)
from apps.rbac.decorators import permission_required

from .. import permissions
from ..forms import SubjectForm
from ..selectors import (
    get_subject,
    get_subjects,
)
from ..services import (
    create_subject,
    delete_subject,
    update_subject,
)


# ============================================================================
# Subject Views
# ============================================================================

@login_required
@permission_required(
    module=permissions.MODULE,
    action=permissions.VIEW,
)
def subject_list(request):
    """
    Subject listing.
    """

    subjects = get_subjects(
        tenant=request.tenant,
    )

    template = (
        "academics/partials/subject_table.html"
        if request.htmx
        else "academics/pages/subject.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "subjects": subjects,
        },
    )


@login_required
@permission_required(
    module=permissions.MODULE,
    action=permissions.CREATE,
)
def subject_create(request):
    """
    Create Subject.
    """

    if request.method == "POST":

        form = SubjectForm(request.POST)

        if form.is_valid():

            try:

                create_subject(
                    tenant=request.tenant,
                    name=form.cleaned_data["name"],
                    code=form.cleaned_data["code"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_success(
                    request=request,
                    template="academics/partials/subject_table.html",
                    context={
                        "subjects": get_subjects(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = SubjectForm()

    return render_modal(
        request=request,
        template="academics/modals/subject_form.html",
        context={
            "form": form,
            "title": "New Subject",
            "submit_label": "Create Subject",
            "target": "#subject-table",
        },
    )


@login_required
@permission_required(
    module=permissions.MODULE,
    action=permissions.EDIT,
)
def subject_update(request, pk):
    """
    Update Subject.
    """

    subject = get_subject(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = SubjectForm(
            request.POST,
            instance=subject,
        )

        if form.is_valid():

            try:

                update_subject(
                    subject=subject,
                    name=form.cleaned_data["name"],
                    code=form.cleaned_data["code"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_success(
                    request=request,
                    template="academics/partials/subject_table.html",
                    context={
                        "subjects": get_subjects(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = SubjectForm(
            instance=subject,
        )

    return render_modal(
        request=request,
        template="academics/modals/subject_form.html",
        context={
            "form": form,
            "title": "Edit Subject",
            "submit_label": "Save Changes",
            "subject": subject,
            "target": "#subject-table",
        },
    )


@login_required
@permission_required(
    module=permissions.MODULE,
    action=permissions.DELETE,
)
def subject_delete(request, pk):
    """
    Delete Subject.
    """

    subject = get_subject(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_subject(
            subject=subject,
        )

        return render_success(
            request=request,
            template="academics/partials/subject_table.html",
            context={
                "subjects": get_subjects(
                    tenant=request.tenant,
                ),
            },
            event="modal:close",
        )

    return render_modal(
        request=request,
        template="academics/modals/delete_subject.html",
        context={
            "subject": subject,
        },
    )