from ..forms import AcademicSessionForm
from ..selectors import (
    get_academic_session,
    get_academic_sessions,
)
from ..services import (
    create_academic_session,
    delete_academic_session,
    update_academic_session,
)

from apps.core.crud import crud_success

from apps.core.htmx import (
    htmx_modal,
    render_partial,
)


def academic_session_list(request):
    """
    Academic Session listing.
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


def academic_session_create(request):
    """
    Create Academic Session.
    """

    if request.method == "POST":

        form = AcademicSessionForm(request.POST)

        if form.is_valid():

            create_academic_session(
                tenant=request.tenant,
                form=form,
            )

            sessions = get_academic_sessions(
                tenant=request.tenant,
            )

            return crud_success(
                request=request,
                template="academic_structure/partials/session_table.html",
                context={
                    "sessions": sessions,
                },
            )

    else:

        form = AcademicSessionForm()

    return htmx_modal(
        request=request,
        template="academic_structure/modals/session_form.html",
        context={
            "form": form,
            "title": "New Academic Session",
            "submit_label": "Create Session",
        },
    )


def academic_session_update(request, pk):
    """
    Update Academic Session.
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

            update_academic_session(
                tenant=request.tenant,
                instance=session,
                form=form,
            )

            sessions = get_academic_sessions(
                tenant=request.tenant,
            )

            return crud_success(
                request=request,
                template="academic_structure/partials/session_table.html",
                context={
                    "sessions": sessions,
                },
            )

    else:

        form = AcademicSessionForm(
            instance=session,
        )

    return htmx_modal(
        request=request,
        template="academic_structure/modals/session_form.html",
        context={
            "form": form,
            "title": "Edit Academic Session",
            "submit_label": "Save Changes",
            "session": session,
        },
    )


def academic_session_delete(request, pk):
    """
    Delete Academic Session.
    """

    session = get_academic_session(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_academic_session(
            instance=session,
        )

        sessions = get_academic_sessions(
            tenant=request.tenant,
        )

        return crud_success(
            request=request,
            template="academic_structure/partials/session_table.html",
            context={
                "sessions": sessions,
            },
        )

    return htmx_modal(
        request=request,
        template="academic_structure/modals/delete_session.html",
        context={
            "session": session,
        },
    )