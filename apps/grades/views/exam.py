from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.core.crud import render_success
from apps.core.htmx import (
    render_modal,
    render_partial,
)
from apps.rbac.decorators import permission_required
from apps.rbac.selectors import has_permission

from ..forms import ExamForm
from ..permissions import exam as permissions
from ..selectors import (
    get_exam,
    get_exams,
)
from ..services import (
    create_exam,
    delete_exam,
    update_exam,
)


# ============================================================================
# Exam Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
def exam_list(request):
    """
    Exam listing.
    """

    exams = get_exams(
        tenant=request.tenant,
    )

    staff_profile = getattr(
        request.user,
        "staff_profile",
        None,
    )

    role = getattr(
        staff_profile,
        "role",
        None,
    )

    can_edit = (
        role is not None
        and has_permission(
            role=role,
            **permissions.EDIT,
        )
    )

    can_delete = (
        role is not None
        and has_permission(
            role=role,
            **permissions.DELETE,
        )
    )

    template = (
        "grades/partials/exam_table.html"
        if request.htmx
        else "grades/pages/exams.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "exams": exams,
            "can_edit": can_edit,
            "can_delete": can_delete,
        },
    )


@login_required
@permission_required(**permissions.CREATE)
def exam_create(request):
    """
    Create an exam.
    """

    if request.method == "POST":

        form = ExamForm(
            request.POST,
            tenant=request.tenant,
        )

        if form.is_valid():

            try:

                create_exam(
                    tenant=request.tenant,
                    form=form,
                )

            except ValidationError as e:

                if hasattr(e, "message_dict"):

                    for field, messages in e.message_dict.items():

                        for message in messages:

                            form.add_error(
                                field,
                                message,
                            )

                else:

                    form.add_error(
                        None,
                        e.message,
                    )

            else:

                return render_success(
                    request=request,
                    template="grades/partials/exam_table.html",
                    context={
                        "exams": get_exams(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = ExamForm(
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="grades/modals/exam_form.html",
        context={
            "form": form,
            "title": "New Exam",
            "submit_label": "Create Exam",
            "post_url": reverse(
                "grades:exam_create",
            ),
            "target": "#exam-table",
        },
    )


@login_required
@permission_required(**permissions.EDIT)
def exam_update(request, pk):
    """
    Update an exam.
    """

    exam = get_exam(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = ExamForm(
            request.POST,
            instance=exam,
            tenant=request.tenant,
        )

        if form.is_valid():

            try:

                update_exam(
                    exam=exam,
                    form=form,
                )

            except ValidationError as e:

                if hasattr(e, "message_dict"):

                    for field, messages in e.message_dict.items():

                        for message in messages:

                            form.add_error(
                                field,
                                message,
                            )

                else:

                    form.add_error(
                        None,
                        e.message,
                    )

            else:

                return render_success(
                    request=request,
                    template="grades/partials/exam_table.html",
                    context={
                        "exams": get_exams(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = ExamForm(
            instance=exam,
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="grades/modals/exam_form.html",
        context={
            "form": form,
            "exam": exam,
            "title": "Edit Exam",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "grades:exam_update",
                kwargs={
                    "pk": exam.pk,
                },
            ),
            "target": "#exam-table",
        },
    )


@login_required
@permission_required(**permissions.DELETE)
def exam_delete(request, pk):
    """
    Delete an exam.
    """

    exam = get_exam(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_exam(
            tenant=request.tenant,
            exam=exam,
        )

        return render_success(
            request=request,
            template="grades/partials/exam_table.html",
            context={
                "exams": get_exams(
                    tenant=request.tenant,
                ),
            },
            event="modal:close",
        )

    return render_modal(
        request=request,
        template="grades/modals/delete_exam.html",
        context={
            "exam": exam,
            "title": "Delete Exam",
            "submit_label": "Delete",
            "post_url": reverse(
                "grades:exam_delete",
                kwargs={
                    "pk": exam.pk,
                },
            ),
            "target": "#exam-table",
        },
    )