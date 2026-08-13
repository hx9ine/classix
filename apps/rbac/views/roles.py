from django.urls import reverse

from apps.core.crud import (
    render_redirect,
    render_success,
)
from apps.core.htmx import (
    render_modal,
    render_partial,
)

from ..forms import RoleForm
from ..selectors import (
    get_role,
    get_roles,
)
from ..services import (
    create_role,
    update_role,
)
from ..decorators import admin_required


# ============================================================================
# Role Views
# ============================================================================

@admin_required
def role_list(request):
    """
    List all roles available to the tenant.
    """

    roles = get_roles(
        tenant=request.tenant,
    )

    template = (
        "rbac/partials/role_table.html"
        if request.htmx
        else "rbac/pages/roles.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "roles": roles,
        },
    )


@admin_required
def role_create(request):
    """
    Create a new role.
    """

    if request.method == "POST":

        form = RoleForm(
            request.POST,
            tenant=request.tenant,
        )

        if form.is_valid():

            create_role(
                tenant=request.tenant,
                form=form,
            )

            return render_success(
                request=request,
                template="rbac/partials/role_table.html",
                context={
                    "roles": get_roles(
                        tenant=request.tenant,
                    ),
                },
            )

    else:

        form = RoleForm(
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="rbac/modals/role_form.html",
        context={
            "form": form,
            "title": "Create Role",
            "submit_label": "Create Role",
            "post_url": reverse(
                "rbac:role_create",
            ),
            "target": "#role-table",
        },
    )


@admin_required
def role_update(request, pk):
    """
    Update a role.
    """

    role = get_role(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = RoleForm(
            request.POST,
            instance=role,
            tenant=request.tenant,
        )

        if form.is_valid():

            update_role(
                form=form,
            )

            return render_redirect(
                url=reverse(
                    "rbac:role_list",
                ),
            )

    else:

        form = RoleForm(
            instance=role,
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="rbac/modals/role_form.html",
        context={
            "form": form,
            "role": role,
            "title": "Edit Role",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "rbac:role_update",
                args=[role.pk],
            ),
        },
    )