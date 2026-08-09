from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
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

from ..forms import TimetablePeriodForm
from ..permissions import timetable as permissions
from ..selectors import (
    get_timetable_period,
    get_timetable_periods,
)
from ..services import (
    create_timetable_period,
    delete_timetable_period,
    update_timetable_period,
)


# ============================================================================
# Timetable Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
def timetable_list(request):
    """
    Timetable listing.
    """

    timetable_periods = get_timetable_periods(
        tenant=request.tenant,
    )

    template = (
        "academics/partials/timetable_table.html"
        if request.htmx
        else "academics/pages/timetable.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "timetable_periods": timetable_periods,
        },
    )


@login_required
@permission_required(**permissions.CREATE)
def timetable_create(request):
    """
    Create a timetable period.
    """

    if request.method == "POST":

        form = TimetablePeriodForm(
            request.POST,
            tenant=request.tenant,
        )

        if form.is_valid():

            try:

                create_timetable_period(
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
                    template="academics/partials/timetable_table.html",
                    context={
                        "timetable_periods": get_timetable_periods(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = TimetablePeriodForm(
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="academics/modals/timetable_form.html",
        context={
            "form": form,
            "title": "Add Timetable Period",
            "submit_label": "Create Period",
            "post_url": reverse(
                "academics:timetable_create",
            ),
            "target": "#timetable-table",
        },
    )


@login_required
@permission_required(**permissions.EDIT)
def timetable_update(request, pk):
    """
    Update a timetable period.
    """

    timetable_period = get_timetable_period(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = TimetablePeriodForm(
            request.POST,
            instance=timetable_period,
            tenant=request.tenant,
        )

        if form.is_valid():

            try:

                update_timetable_period(
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
                    template="academics/partials/timetable_table.html",
                    context={
                        "timetable_periods": get_timetable_periods(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = TimetablePeriodForm(
            instance=timetable_period,
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="academics/modals/timetable_form.html",
        context={
            "form": form,
            "timetable_period": timetable_period,
            "title": "Edit Timetable Period",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "academics:timetable_update",
                kwargs={
                    "pk": timetable_period.pk,
                },
            ),
            "target": "#timetable-table",
        },
    )


@login_required
@permission_required(**permissions.DELETE)
def timetable_delete(request, pk):
    """
    Delete a timetable period.
    """

    timetable_period = get_timetable_period(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_timetable_period(
            timetable_period=timetable_period,
        )

        return render_success(
            request=request,
            template="academics/partials/timetable_table.html",
            context={
                "timetable_periods": get_timetable_periods(
                    tenant=request.tenant,
                ),
            },
            event="modal:close",
        )

    return render_modal(
        request=request,
        template="academics/modals/delete_timetable.html",
        context={
            "timetable_period": timetable_period,
            "title": "Delete Timetable Period",
            "submit_label": "Delete",
            "post_url": reverse(
                "academics:timetable_delete",
                kwargs={
                    "pk": timetable_period.pk,
                },
            ),
            "target": "#timetable-table",
        },
    )