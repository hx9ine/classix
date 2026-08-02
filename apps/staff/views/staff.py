from django.urls import reverse

from apps.core.crud import render_success, render_redirect
from apps.core.htmx import (
    render_modal,
    render_partial,
)

from ..forms import StaffForm
from ..selectors import (
    get_staff,
    get_staff_members,
)
from ..services import (
    create_staff,
    delete_staff,
    update_staff,
)


# ============================================================================
# Staff Views
# ============================================================================

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


def staff_update(request, pk):
    """
    Update a staff member.
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
                args=[staff.pk],
            ),
            "target": "#staff-table",
        },
    )


def staff_delete(request, pk):
    """
    Delete a staff member.
    """

    staff = get_staff(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_staff(
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
        )

    return render_modal(
        request=request,
        template="staff/modals/delete_staff.html",
        context={
            "staff": staff,
            "title": "Delete Staff",
            "submit_label": "Delete",
            "post_url": reverse(
                "staff:staff_delete",
                args=[staff.pk],
            ),
            "target": "#staff-table",
        },
    )


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
                    args=[staff.pk],
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
                args=[staff.pk],
            ),
        },
    )