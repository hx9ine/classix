from ..forms import SectionForm
from ..selectors import (
    get_section,
    get_sections,
)
from ..services import (
    create_section,
    delete_section,
    update_section,
)

from apps.core.crud import crud_success
from apps.core.htmx import (
    htmx_modal,
    render_partial,
)


# ============================================================================
# Section Views
# ============================================================================

def section_list(request):
    """
    Section listing.
    """

    sections = get_sections(
        tenant=request.tenant,
    )

    template = (
        "academic_structure/partials/section_table.html"
        if request.htmx
        else "academic_structure/pages/sections.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "sections": sections,
        },
    )


def section_create(request):
    """
    Create Section.
    """

    if request.method == "POST":

        form = SectionForm(
            request.POST,
            tenant=request.tenant,
        )

        if form.is_valid():

            create_section(
                tenant=request.tenant,
                form=form,
            )

            return crud_success(
                request=request,
                template="academic_structure/partials/section_table.html",
                context={
                    "sections": get_sections(
                        tenant=request.tenant,
                    ),
                },
            )

    else:

        form = SectionForm(
            tenant=request.tenant,
        )

    return htmx_modal(
        request=request,
        template="academic_structure/modals/section_form.html",
        context={
            "form": form,
            "title": "New Section",
            "submit_label": "Create Section",
        },
    )


def section_update(request, pk):
    """
    Update Section.
    """

    section = get_section(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = SectionForm(
            request.POST,
            instance=section,
            tenant=request.tenant,
        )

        if form.is_valid():

            update_section(
                form=form,
            )

            return crud_success(
                request=request,
                template="academic_structure/partials/section_table.html",
                context={
                    "sections": get_sections(
                        tenant=request.tenant,
                    ),
                },
            )

    else:

        form = SectionForm(
            instance=section,
            tenant=request.tenant,
        )

    return htmx_modal(
        request=request,
        template="academic_structure/modals/section_form.html",
        context={
            "form": form,
            "title": "Edit Section",
            "submit_label": "Save Changes",
            "section": section,
        },
    )


def section_delete(request, pk):
    """
    Delete Section.
    """

    section = get_section(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_section(
            instance=section,
        )

        return crud_success(
            request=request,
            template="academic_structure/partials/section_table.html",
            context={
                "sections": get_sections(
                    tenant=request.tenant,
                ),
            },
        )

    return htmx_modal(
        request=request,
        template="academic_structure/modals/delete_section.html",
        context={
            "section": section,
        },
    )