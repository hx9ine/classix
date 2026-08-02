from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from apps.core.crud import render_success
from apps.core.htmx import (
    render_modal,
    render_partial,
)
from apps.rbac.decorators import permission_required

from ..forms import AcademicSessionForm
from ..permissions import academic_session as permissions
from ..selectors import (
    get_academic_session,
    get_academic_sessions,
)
from ..services import (
    create_academic_session,
    delete_academic_session,
    update_academic_session,
)


# ============================================================================
# Academic Session Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
def academic_session_list(request):
    """
    Display all academic sessions.
    """

    sessions = get_academic_sessions(
        tenant=request.tenant,
    )

    template = (
        "academic_structure/partials/session_table.html"
        if request.htmx
        else "academic_structure/pages/sessions.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "sessions": sessions,
        },
    )


@login_required
@permission_required(**permissions.CREATE)
def academic_session_create(request):
    """
    Create an academic session.
    """

    if request.method == "POST":

        form = AcademicSessionForm(request.POST)

        if form.is_valid():

            try:

                create_academic_session(
                    tenant=request.tenant,
                    name=form.cleaned_data["name"],
                    start_date=form.cleaned_data["start_date"],
                    end_date=form.cleaned_data["end_date"],
                    is_current=form.cleaned_data["is_current"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_success(
                    request=request,
                    template="academic_structure/partials/session_table.html",
                    context={
                        "sessions": get_academic_sessions(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = AcademicSessionForm()

    return render_modal(
        request=request,
        template="academic_structure/modals/session_form.html",
        context={
            "form": form,
            "title": "New Academic Session",
            "submit_label": "Create Session",
            "target": "#session-table",
        },
    )


@login_required
@permission_required(**permissions.EDIT)
def academic_session_update(request, pk):
    """
    Update an academic session.
    """

    session = get_academic_session(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = AcademicSessionForm(
            request.POST,
            instance=session,
        )

        if form.is_valid():

            try:

                update_academic_session(
                    academic_session=session,
                    name=form.cleaned_data["name"],
                    start_date=form.cleaned_data["start_date"],
                    end_date=form.cleaned_data["end_date"],
                    is_current=form.cleaned_data["is_current"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_success(
                    request=request,
                    template="academic_structure/partials/session_table.html",
                    context={
                        "sessions": get_academic_sessions(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = AcademicSessionForm(
            instance=session,
        )

    return render_modal(
        request=request,
        template="academic_structure/modals/session_form.html",
        context={
            "form": form,
            "title": "Edit Academic Session",
            "submit_label": "Save Changes",
            "target": "#session-table",
        },
    )


@login_required
@permission_required(**permissions.DELETE)
def academic_session_delete(request, pk):
    """
    Delete an academic session.
    """

    session = get_academic_session(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_academic_session(
            academic_session=session,
        )

        return render_success(
            request=request,
            template="academic_structure/partials/session_table.html",
            context={
                "sessions": get_academic_sessions(
                    tenant=request.tenant,
                ),
            },
            event="modal:close",
        )

    return render_modal(
        request=request,
        template="academic_structure/modals/delete_session.html",
        context={
            "session": session,
            "post_url": request.path,
            "target": "#session-table",
        },
    )