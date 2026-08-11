from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404
from django.urls import reverse

from apps.core.crud import render_success
from apps.core.htmx import (
    render_modal,
    render_partial,
)
from apps.rbac.decorators import permission_required

from ..forms import AssignmentForm
from ..models import TimetablePeriod
from ..permissions import homework as permissions
from ..selectors import (
    get_assignment,
    get_assignments,
    get_assignments_by_staff,
)
from ..services import (
    create_assignment,
    delete_assignment,
    update_assignment,
)


# ============================================================================
# Helpers
# ============================================================================

def _get_staff(request):
    return request.user.staff_profile


def _get_assignments_for_user(request):
    """
    Return assignments visible to the current staff member.

    Admin roles can see all tenant assignments.
    Non-admin staff are restricted to assignments belonging
    to their own staff profile.
    """

    staff = _get_staff(request)

    if staff.role.is_admin_role:
        return get_assignments(
            tenant=request.tenant,
        )

    return get_assignments_by_staff(
        tenant=request.tenant,
        staff=staff,
    )


def _get_assignment_for_user(
    *,
    request,
    pk,
):
    """
    Return an assignment visible to the current staff member.
    """

    assignment = get_assignment(
        tenant=request.tenant,
        pk=pk,
    )

    staff = _get_staff(request)

    if (
        not staff.role.is_admin_role
        and assignment.staff_id != staff.pk
    ):
        raise Http404("Assignment not found.")

    return assignment


def _scope_assignment_form(
    *,
    request,
    form,
    staff,
):
    """
    Restrict assignment form choices to the current
    teacher's assigned sections and subjects.

    Admin roles retain access to all tenant-scoped
    form choices.
    """

    if staff.role.is_admin_role:
        return

    assigned_periods = (
        TimetablePeriod.objects
        .filter(
            tenant=request.tenant,
            staff=staff,
        )
    )

    assigned_section_ids = (
        assigned_periods
        .values_list(
            "section_id",
            flat=True,
        )
        .distinct()
    )

    assigned_subject_ids = (
        assigned_periods
        .values_list(
            "subject_id",
            flat=True,
        )
        .distinct()
    )

    form.fields["section"].queryset = (
        form.fields["section"].queryset
        .filter(
            pk__in=assigned_section_ids,
        )
    )

    form.fields["subject"].queryset = (
        form.fields["subject"].queryset
        .filter(
            pk__in=assigned_subject_ids,
        )
    )

    form.fields["staff"].queryset = (
        form.fields["staff"].queryset
        .filter(
            pk=staff.pk,
        )
    )


# ============================================================================
# Homework Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
def homework_list(request):
    """
    Assignment listing.
    """

    assignments = _get_assignments_for_user(
        request,
    )

    template = (
        "academics/partials/homework_table.html"
        if request.htmx
        else "academics/pages/homework.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "assignments": assignments,
        },
    )


@login_required
@permission_required(**permissions.CREATE)
def homework_create(request):
    """
    Create an assignment.
    """

    staff = _get_staff(request)

    if request.method == "POST":

        form = AssignmentForm(
            request.POST,
            tenant=request.tenant,
        )

        _scope_assignment_form(
            request=request,
            form=form,
            staff=staff,
        )

        if form.is_valid():

            try:

                create_assignment(
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
                    template="academics/partials/homework_table.html",
                    context={
                        "assignments": _get_assignments_for_user(
                            request,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = AssignmentForm(
            tenant=request.tenant,
        )

        _scope_assignment_form(
            request=request,
            form=form,
            staff=staff,
        )

        if not staff.role.is_admin_role:
            form.fields["staff"].initial = staff.pk

    return render_modal(
        request=request,
        template="academics/modals/homework_form.html",
        context={
            "form": form,
            "title": "New Assignment",
            "submit_label": "Create Assignment",
            "post_url": reverse(
                "academics:homework_create",
            ),
            "target": "#homework-table",
        },
    )


@login_required
@permission_required(**permissions.EDIT)
def homework_update(request, pk):
    """
    Update an assignment.
    """

    assignment = _get_assignment_for_user(
        request=request,
        pk=pk,
    )

    staff = _get_staff(request)

    if request.method == "POST":

        form = AssignmentForm(
            request.POST,
            instance=assignment,
            tenant=request.tenant,
        )

        _scope_assignment_form(
            request=request,
            form=form,
            staff=staff,
        )

        if form.is_valid():

            try:

                update_assignment(
                    assignment=assignment,
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
                    template="academics/partials/homework_table.html",
                    context={
                        "assignments": _get_assignments_for_user(
                            request,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = AssignmentForm(
            instance=assignment,
            tenant=request.tenant,
        )

        _scope_assignment_form(
            request=request,
            form=form,
            staff=staff,
        )

    return render_modal(
        request=request,
        template="academics/modals/homework_form.html",
        context={
            "form": form,
            "assignment": assignment,
            "title": "Edit Assignment",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "academics:homework_update",
                kwargs={
                    "pk": assignment.pk,
                },
            ),
            "target": "#homework-table",
        },
    )


@login_required
@permission_required(**permissions.DELETE)
def homework_delete(request, pk):
    """
    Delete an assignment.
    """

    assignment = _get_assignment_for_user(
        request=request,
        pk=pk,
    )

    if request.method == "POST":

        delete_assignment(
            tenant=request.tenant,
            assignment=assignment,
        )

        return render_success(
            request=request,
            template="academics/partials/homework_table.html",
            context={
                "assignments": _get_assignments_for_user(
                    request,
                ),
            },
            event="modal:close",
        )

    return render_modal(
        request=request,
        template="academics/modals/delete_homework.html",
        context={
            "assignment": assignment,
            "title": "Delete Assignment",
            "submit_label": "Delete",
            "post_url": reverse(
                "academics:homework_delete",
                kwargs={
                    "pk": assignment.pk,
                },
            ),
            "target": "#homework-table",
        },
    )