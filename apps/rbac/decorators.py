from __future__ import annotations

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from apps.accounts.models import AccountCategory

from .models import RolePermission
from .selectors import has_permission


def permission_required(
    *,
    module: RolePermission.Module,
    action: RolePermission.Action,
):
    """
    Enforce RBAC permissions on a view.

    Tenant administrators have unrestricted access.
    All other users are evaluated through the RBAC system.
    """

    def decorator(view_func):

        @login_required
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):

            user = request.user

            # ==========================================================
            # Hardcoded Administrator Access
            # ==========================================================

            if user.account_category == AccountCategory.ADMIN:
                return view_func(request, *args, **kwargs)

            # ==========================================================
            # RBAC Permission Check
            # ==========================================================

            staff_profile = getattr(
                user,
                "staff_profile",
                None,
            )

            if (
                staff_profile is None
                or staff_profile.role is None
            ):
                raise PermissionDenied(
                    "You do not have permission to access this resource."
                )

            if not has_permission(
                role=staff_profile.role,
                module=module,
                action=action,
            ):
                raise PermissionDenied(
                    "You do not have permission to perform this action."
                )

            return view_func(
                request,
                *args,
                **kwargs,
            )

        return wrapped_view

    return decorator