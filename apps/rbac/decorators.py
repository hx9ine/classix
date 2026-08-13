from __future__ import annotations

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from apps.rbac.models import RolePermission
from apps.rbac.selectors import has_permission


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

            if user.is_admin:
                return view_func(
                    request,
                    *args,
                    **kwargs,
                )

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


def admin_required(view_func):
    """
    Restrict a view to Tenant Admin users.

    Admin access is determined by the existing User.is_admin
    property and is independent of configurable role permissions.
    """

    @login_required
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):

        if not request.user.is_admin:
            raise PermissionDenied(
                "You must be an administrator to access this resource."
            )

        return view_func(
            request,
            *args,
            **kwargs,
        )

    return wrapped_view