from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from apps.core.crud import render_success
from apps.core.htmx import (
    render_modal,
    render_partial,
)
from apps.rbac.decorators import permission_required

from ..forms import SectionForm
from ..permissions import section as permissions
from ..selectors import (
    get_section,
    get_sections,
)
from ..services import (
    create_section,
    delete_section,
    update_section,
)


# ============================================================================
# Section Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
def section_list(request):
    """
    Display all sections.
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


@login_required
@permission_required(**permissions.CREATE)
def section_create(request):
    """
    Create a section.
    """

    if request.method == "POST":

        form = SectionForm(
            request.POST,
            tenant=request.tenant,
        )

        if form.is_valid():

            try:

                create_section(
                    tenant=request.tenant,
                    academic_session=form.cleaned_data["academic_session"],
                    class_level=form.cleaned_data["class_level"],
                    name=form.cleaned_data["name"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_success(
                    request=request,
                    template="academic_structure/partials/section_table.html",
                    context={
                        "sections": get_sections(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = SectionForm(
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="academic_structure/modals/section_form.html",
        context={
            "form": form,
            "title": "New Section",
            "submit_label": "Create Section",
            "target": "#section-table",
        },
    )


@login_required
@permission_required(**permissions.EDIT)
def section_update(request, pk):
    """
    Update a section.
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

            try:

                update_section(
                    section=section,
                    academic_session=form.cleaned_data["academic_session"],
                    class_level=form.cleaned_data["class_level"],
                    name=form.cleaned_data["name"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_success(
                    request=request,
                    template="academic_structure/partials/section_table.html",
                    context={
                        "sections": get_sections(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = SectionForm(
            instance=section,
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="academic_structure/modals/section_form.html",
        context={
            "form": form,
            "title": "Edit Section",
            "submit_label": "Save Changes",
            "target": "#section-table",
        },
    )


@login_required
@permission_required(**permissions.DELETE)
def section_delete(request, pk):
    """
    Delete a section.
    """

    section = get_section(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        delete_section(
            section=section,
        )

        return render_success(
            request=request,
            template="academic_structure/partials/section_table.html",
            context={
                "sections": get_sections(
                    tenant=request.tenant,
                ),
            },
            event="modal:close",
        )

    return render_modal(
        request=request,
        template="academic_structure/modals/delete_section.html",
        context={
            "section": section,
            "post_url": request.path,
            "target": "#section-table",
        },
    )