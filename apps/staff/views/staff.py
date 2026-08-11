from django.contrib.auth.decorators import login_required
from django.urls import reverse

from apps.core.crud import (
    render_redirect,
    render_success,
)
from apps.core.htmx import (
    render_modal,
    render_partial,
)
from apps.rbac.decorators import permission_required

from ..forms import (
    StaffForm,
    StaffUserAssignmentForm,
)
from ..permissions import staff as permissions
from ..selectors import (
    get_staff,
    get_staff_members,
)
from ..services import (
    activate_staff,
    assign_user,
    create_staff,
    deactivate_staff,
    update_staff,
)


# ============================================================================
# Staff Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
def staff_list(request):
    """
    Staff listing.
    """

    staff = get_staff_members(
        tenant=request.tenant,
    )

    template = (
        "staff/partials/staff_table.html"
        if request.htmx
        else "staff/pages/staff.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "staff": staff,
        },
    )


@login_required
@permission_required(**permissions.CREATE)
def staff_create(request):
    """
    Create a staff member.
    """

    if request.method == "POST":

        form = StaffForm(
            request.POST,
            request.FILES,
            tenant=request.tenant,
        )

        if form.is_valid():

            create_staff(
                tenant=request.tenant,
                form=form,
            )

            return render_success(
                request=request,
                template="staff/partials/staff_table.html",
                context={
                    "staff": get_staff_members(
                        tenant=request.tenant,
                    ),
                },
                event="modal:close",
            )

    else:

        form = StaffForm(
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="staff/modals/staff_form.html",
        context={
            "form": form,
            "title": "Add Staff",
            "submit_label": "Create Staff",
            "post_url": reverse(
                "staff:staff_create",
            ),
            "target": "#staff-table",
        },
    )


@login_required
@permission_required(**permissions.EDIT)
def staff_update(request, pk):
    """
    Update a staff member from the Staff list.
    """

    staff = get_staff(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = StaffForm(
            request.POST,
            request.FILES,
            instance=staff,
            tenant=request.tenant,
        )

        if form.is_valid():

            update_staff(
                form=form,
            )

            return render_success(
                request=request,
                template="staff/partials/staff_table.html",
                context={
                    "staff": get_staff_members(
                        tenant=request.tenant,
                    ),
                },
                event="modal:close",
            )

    else:

        form = StaffForm(
            instance=staff,
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="staff/modals/staff_form.html",
        context={
            "form": form,
            "staff": staff,
            "title": "Edit Staff",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "staff:staff_update",
                kwargs={
                    "pk": staff.pk,
                },
            ),
            "target": "#staff-table",
        },
    )



@login_required
@permission_required(**permissions.EDIT)
def staff_user_assign(request, pk):
    """
    Assign an existing portal user to a staff member.
    """

    staff = get_staff(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = StaffUserAssignmentForm(
            request.POST,
            tenant=request.tenant,
            instance=staff,
        )

        if form.is_valid():

            assign_user(
                instance=staff,
                user=form.cleaned_data["user"],
            )

            return render_success(
                request=request,
                template="staff/partials/staff_table.html",
                context={
                    "staff": get_staff_members(
                        tenant=request.tenant,
                    ),
                },
                event="modal:close",
            )

    else:

        form = StaffUserAssignmentForm(
            tenant=request.tenant,
            instance=staff,
        )

    return render_modal(
        request=request,
        template="staff/modals/staff_user_assign.html",
        context={
            "form": form,
            "staff": staff,
            "title": "Assign Portal User",
            "submit_label": "Assign User",
            "post_url": reverse(
                "staff:staff_user_assign",
                kwargs={
                    "pk": staff.pk,
                },
            ),
            "target": "#staff-table",
        },
    )


@login_required
@permission_required(**permissions.DELETE)
def staff_deactivate(request, pk):
    """
    Deactivate a staff member.
    """

    staff = get_staff(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        deactivate_staff(
            instance=staff,
        )

        return render_success(
            request=request,
            template="staff/partials/staff_table.html",
            context={
                "staff": get_staff_members(
                    tenant=request.tenant,
                ),
            },
            event="modal:close",
        )

    return render_modal(
        request=request,
        template="staff/modals/staff_status.html",
        context={
            "staff": staff,
            "action": "deactivate",
            "title": "Deactivate Staff",
            "submit_label": "Deactivate",
            "post_url": reverse(
                "staff:staff_deactivate",
                kwargs={
                    "pk": staff.pk,
                },
            ),
        },
    )


@login_required
@permission_required(**permissions.DELETE)
def staff_activate(request, pk):
    """
    Activate a staff member.
    """

    staff = get_staff(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        activate_staff(
            instance=staff,
        )

        return render_success(
            request=request,
            template="staff/partials/staff_table.html",
            context={
                "staff": get_staff_members(
                    tenant=request.tenant,
                ),
            },
            event="modal:close",
        )

    return render_modal(
        request=request,
        template="staff/modals/staff_status.html",
        context={
            "staff": staff,
            "action": "activate",
            "title": "Activate Staff",
            "submit_label": "Activate",
            "post_url": reverse(
                "staff:staff_activate",
                kwargs={
                    "pk": staff.pk,
                },
            ),
        },
    )


@login_required
@permission_required(**permissions.EDIT)
def staff_profile_update(request, pk):
    """
    Update a staff member from the Staff Profile.
    """

    staff = get_staff(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = StaffForm(
            request.POST,
            request.FILES,
            instance=staff,
            tenant=request.tenant,
        )

        if form.is_valid():

            update_staff(
                form=form,
            )

            return render_redirect(
                url=reverse(
                    "staff:staff_detail",
                    kwargs={
                        "pk": staff.pk,
                    },
                ),
            )

    else:

        form = StaffForm(
            instance=staff,
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="staff/modals/staff_form.html",
        context={
            "form": form,
            "staff": staff,
            "title": "Edit Staff",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "staff:staff_profile_update",
                kwargs={
                    "pk": staff.pk,
                },
            ),
        },
    )