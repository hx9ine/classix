from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from apps.core.crud import render_success
from apps.core.htmx import (
    render_modal,
    render_partial,
)
from apps.rbac.decorators import permission_required

from ..forms import ClassLevelForm
from ..permissions import class_level as permissions
from ..selectors import (
    get_class_level,
    get_class_levels,
)
from ..services import (
    create_class_level,
    delete_class_level,
    update_class_level,
)


# ============================================================================
# Class Level Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
def class_level_list(request):
    """
    Display all class levels.
    """

    class_levels = get_class_levels(
        tenant=request.tenant,
    )

    template = (
        "academic_structure/partials/class_level_table.html"
        if request.htmx
        else "academic_structure/pages/class_levels.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "class_levels": class_levels,
        },
    )


@login_required
@permission_required(**permissions.CREATE)
def class_level_create(request):
    """
    Create a class level.
    """

    if request.method == "POST":

        form = ClassLevelForm(request.POST)

        if form.is_valid():

            try:

                create_class_level(
                    tenant=request.tenant,
                    name=form.cleaned_data["name"],
                    sort_order=form.cleaned_data["sort_order"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_success(
                    request=request,
                    template="academic_structure/partials/class_level_table.html",
                    context={
                        "class_levels": get_class_levels(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = ClassLevelForm()

    return render_modal(
        request=request,
        template="academic_structure/modals/class_level_form.html",
        context={
            "form": form,
            "title": "New Class Level",
            "submit_label": "Create Class Level",
            "target": "#class-level-table",
        },
    )


@login_required
@permission_required(**permissions.EDIT)
def class_level_update(request, pk):
    """
    Update a class level.
    """

    class_level = get_class_level(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = ClassLevelForm(
            request.POST,
            instance=class_level,
        )

        if form.is_valid():

            try:

                update_class_level(
                    class_level=class_level,
                    name=form.cleaned_data["name"],
                    sort_order=form.cleaned_data["sort_order"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_success(
                    request=request,
                    template="academic_structure/partials/class_level_table.html",
                    context={
                        "class_levels": get_class_levels(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = ClassLevelForm(
            instance=class_level,
        )

    return render_modal(
        request=request,
        template="academic_structure/modals/class_level_form.html",
        context={
            "form": form,
            "title": "Edit Class Level",
            "submit_label": "Save Changes",
            "target": "#class-level-table",
        },
    )


@login_required
@permission_required(**permissions.DELETE)
def class_level_delete(request, pk):
    """
    Delete a class level.
    """

    class_level = get_class_level(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_class_level(
            class_level=class_level,
        )

        return render_success(
            request=request,
            template="academic_structure/partials/class_level_table.html",
            context={
                "class_levels": get_class_levels(
                    tenant=request.tenant,
                ),
            },
            event="modal:close",
        )

    return render_modal(
        request=request,
        template="academic_structure/modals/delete_class_level.html",
        context={
            "class_level": class_level,
            "post_url": request.path,
            "target": "#class-level-table",
        },
    )