from django.urls import reverse

from apps.core.htmx import htmx_modal
from apps.core.oob import render_select_oob

from ..forms import RoleForm
from ..selectors import get_roles
from ..services import create_role


# ============================================================================
# Inline Views
# ============================================================================

def role_create_inline(request):
    """
    Create a role from a dependent select.
    """

    if request.method == "POST":

        form = RoleForm(
            request.POST,
            tenant=request.tenant,
        )

        if form.is_valid():

            role = create_role(
                tenant=request.tenant,
                form=form,
            )

            return render_select_oob(
                request=request,
                field_id="id_role",
                field_name="role",
                options=get_roles(
                    tenant=request.tenant,
                ),
                selected=role.pk,
            )

    if request.method != "POST":

        form = RoleForm(
            tenant=request.tenant,
        )

    return htmx_modal(
        request=request,
        template="rbac/modals/role_form.html",
        context={
            "form": form,
            "title": "Create Role",
            "submit_label": "Create Role",
            "post_url": reverse(
                "rbac:role_create_inline",
            ),
        },
    )