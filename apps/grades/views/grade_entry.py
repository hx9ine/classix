from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import reverse

from apps.core.crud import render_success
from apps.core.htmx import (
    render_modal,
    render_partial,
)
from apps.rbac.decorators import permission_required
from apps.rbac.models import RolePermission
from apps.rbac.selectors import has_permission

from ..forms import GradeEntryForm
from ..selectors import (
    get_grade_entries,
    get_grade_entry,
)
from ..selectors.teacher_scope import (
    get_teacher_grade_entries,
)
from ..services import (
    create_grade_entry,
    update_grade_entry,
)


# ============================================================================
# Helpers
# ============================================================================

def _get_staff(request):
    return getattr(
        request.user,
        "staff_profile",
        None,
    )


def _is_teacher(staff):
    return (
        staff is not None
        and staff.role is not None
        and staff.role.license_category
        == staff.role.LicenseCategory.FACULTY
    )


def _get_grade_entries_for_request(request):
    """
    Return grade entries according to the current user's
    RBAC/data-scope rules.

    Admin and non-Faculty roles use the tenant-wide queryset
    permitted by their RBAC permission.

    Teacher-category staff are restricted to their timetable
    section/subject assignments.
    """

    staff = _get_staff(request)

    if _is_teacher(staff):
        return get_teacher_grade_entries(
            tenant=request.tenant,
            staff=staff,
        )

    return get_grade_entries(
        tenant=request.tenant,
    )


def _ensure_teacher_scope(
    *,
    request,
    grade_entry,
):
    """
    Ensure a Faculty/Teacher user can access this specific
    grade entry.
    """

    staff = _get_staff(request)

    if not _is_teacher(staff):
        return

    allowed = (
        get_teacher_grade_entries(
            tenant=request.tenant,
            staff=staff,
        )
        .filter(
            pk=grade_entry.pk,
        )
        .exists()
    )

    if not allowed:
        raise PermissionDenied(
            "You do not have access to this grade entry."
        )


# ============================================================================
# List
# ============================================================================

@permission_required(
    module=RolePermission.Module.GRADES,
    action=RolePermission.Action.VIEW,
)
def grade_entry_list(request):
    """
    List grade entries.

    Teacher-category staff are restricted to their assigned
    section/subject combinations.
    """

    grade_entries = _get_grade_entries_for_request(
        request,
    )

    staff_profile = getattr(
        request.user,
        "staff_profile",
        None,
    )

    role = getattr(
        staff_profile,
        "role",
        None,
    )

    can_edit = (
        role is not None
        and has_permission(
            role=role,
            module=RolePermission.Module.GRADES,
            action=RolePermission.Action.EDIT,
        )
    )

    template = (
        "grades/partials/grade_entry_table.html"
        if request.htmx
        else "grades/pages/grade_entries.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "grade_entries": grade_entries,
            "can_edit": can_edit,
        },
    )


# ============================================================================
# Create
# ============================================================================

@permission_required(
    module=RolePermission.Module.GRADES,
    action=RolePermission.Action.CREATE,
)
def grade_entry_create(request):
    """
    Create a grade entry.
    """

    staff = _get_staff(request)

    form_kwargs = {
        "tenant": request.tenant,
    }

    if _is_teacher(staff):
        form_kwargs["staff"] = staff

    if request.method == "POST":

        form = GradeEntryForm(
            request.POST,
            **form_kwargs,
        )

        if form.is_valid():

            try:

                create_grade_entry(
                    tenant=request.tenant,
                    form=form,
                    staff=staff if _is_teacher(staff) else None,
                )

            except ValidationError as error:

                if hasattr(
                    error,
                    "message_dict",
                ):

                    for field, messages in (
                        error.message_dict.items()
                    ):

                        for message in messages:

                            form.add_error(
                                field,
                                message,
                            )

                else:

                    form.add_error(
                        None,
                        error.message,
                    )

            else:

                return render_success(
                    request=request,
                    template=(
                        "grades/partials/"
                        "grade_entry_table.html"
                    ),
                    context={
                        "grade_entries": (
                            _get_grade_entries_for_request(
                                request,
                            )
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = GradeEntryForm(
            **form_kwargs,
        )

    return render_modal(
        request=request,
        template="grades/modals/grade_entry_form.html",
        context={
            "form": form,
            "title": "Enter Grade",
            "submit_label": "Save Grade",
            "post_url": reverse(
                "grades:grade_entry_create",
            ),
            "target": "#grade-entry-table",
        },
    )


# ============================================================================
# Update
# ============================================================================

@permission_required(
    module=RolePermission.Module.GRADES,
    action=RolePermission.Action.EDIT,
)
def grade_entry_update(
    request,
    pk,
):
    """
    Update a grade entry.

    Teacher-category staff can only update entries within
    their timetable section/subject scope.
    """

    grade_entry = get_grade_entry(
        tenant=request.tenant,
        pk=pk,
    )

    _ensure_teacher_scope(
        request=request,
        grade_entry=grade_entry,
    )

    staff = _get_staff(request)

    form_kwargs = {
        "tenant": request.tenant,
        "instance": grade_entry,
    }

    if _is_teacher(staff):
        form_kwargs["staff"] = staff

    if request.method == "POST":

        form = GradeEntryForm(
            request.POST,
            **form_kwargs,
        )

        if form.is_valid():

            try:

                update_grade_entry(
                    grade_entry=grade_entry,
                    form=form,
                    staff=staff if _is_teacher(staff) else None,
                )

            except ValidationError as error:

                if hasattr(
                    error,
                    "message_dict",
                ):

                    for field, messages in (
                        error.message_dict.items()
                    ):

                        for message in messages:

                            form.add_error(
                                field,
                                message,
                            )

                else:

                    form.add_error(
                        None,
                        error.message,
                    )

            else:

                return render_success(
                    request=request,
                    template=(
                        "grades/partials/"
                        "grade_entry_table.html"
                    ),
                    context={
                        "grade_entries": (
                            _get_grade_entries_for_request(
                                request,
                            )
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = GradeEntryForm(
            **form_kwargs,
        )

    return render_modal(
        request=request,
        template="grades/modals/grade_entry_form.html",
        context={
            "form": form,
            "grade_entry": grade_entry,
            "title": "Edit Grade",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "grades:grade_entry_update",
                kwargs={
                    "pk": grade_entry.pk,
                },
            ),
            "target": "#grade-entry-table",
        },
    )