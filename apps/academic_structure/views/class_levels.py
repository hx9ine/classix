from ..forms import ClassLevelForm
from ..selectors import (
    get_class_level,
    get_class_levels,
)
from ..services import (
    create_class_level,
    delete_class_level,
    update_class_level,
)

from apps.core.crud import render_success

from apps.core.htmx import (
    htmx_modal,
    render_partial,
)


# ============================================================================
# Class Level Views
# ============================================================================

def class_level_list(request):
    """
    Class Level listing.
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


def class_level_create(request):
    """
    Create Class Level.
    """

    if request.method == "POST":

        form = ClassLevelForm(request.POST)

        if form.is_valid():

            create_class_level(
                tenant=request.tenant,
                form=form,
            )

            return render_success(
                request=request,
                template="academic_structure/partials/class_level_table.html",
                context={
                    "class_levels": get_class_levels(
                        tenant=request.tenant,
                    ),
                },
            )

    else:

        form = ClassLevelForm()

    return htmx_modal(
        request=request,
        template="academic_structure/modals/class_level_form.html",
        context={
            "form": form,
            "title": "New Class Level",
            "submit_label": "Create Class Level",
        },
    )


def class_level_update(request, pk):
    """
    Update Class Level.
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

            update_class_level(
                form=form,
            )

            return render_success(
                request=request,
                template="academic_structure/partials/class_level_table.html",
                context={
                    "class_levels": get_class_levels(
                        tenant=request.tenant,
                    ),
                },
            )

    else:

        form = ClassLevelForm(
            instance=class_level,
        )

    return htmx_modal(
        request=request,
        template="academic_structure/modals/class_level_form.html",
        context={
            "form": form,
            "title": "Edit Class Level",
            "submit_label": "Save Changes",
            "class_level": class_level,
        },
    )


def class_level_delete(request, pk):
    """
    Delete Class Level.
    """

    class_level = get_class_level(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_class_level(
            instance=class_level,
        )

        return render_success(
            request=request,
            template="academic_structure/partials/class_level_table.html",
            context={
                "class_levels": get_class_levels(
                    tenant=request.tenant,
                ),
            },
        )

    return htmx_modal(
        request=request,
        template="academic_structure/modals/delete_class_level.html",
        context={
            "class_level": class_level,
        },
    )