from __future__ import annotations

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import RolePermission
from .selectors import has_permission


def permission_required(
    *,
    module: RolePermission.Module,
    action: RolePermission.Action,
):
    """
    Enforce RBAC permissions on a view.

    Example:

        @permission_required(
            module=RolePermission.Module.STAFF,
            action=RolePermission.Action.VIEW,
        )
        def staff_list(request):
            ...
    """

    def decorator(view_func):

        @login_required
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):

            user = request.user

            staff_profile = getattr(user, "staff_profile", None)

            if staff_profile is None or staff_profile.role is None:
                raise PermissionDenied(
                    "You do not have permission to access this resource."
                )

            role = staff_profile.role

            if not has_permission(
                role=role,
                module=module,
                action=action,
            ):
                raise PermissionDenied(
                    "You do not have permission to perform this action."
                )

            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator