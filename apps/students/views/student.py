from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.core.crud import (
    render_redirect,
    render_success,
)
from apps.core.htmx import (
    render_modal,
    render_partial,
)
from apps.rbac.decorators import permission_required

from ..forms import StudentForm
from ..permissions import student as permissions
from ..selectors import (
    get_student,
    get_students,
)
from ..services import update_student


# ============================================================================
# Student Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
def student_list(request):
    """
    Student listing.
    """

    students = get_students(
        tenant=request.tenant,
    )

    template = (
        "students/partials/student_table.html"
        if request.htmx
        else "students/pages/student.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "students": students,
        },
    )


@login_required
@permission_required(**permissions.EDIT)
def student_update(request, pk):
    """
    Update a student from the Students list.
    """

    student = get_student(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = StudentForm(
            request.POST,
            instance=student,
            tenant=request.tenant,
        )

        if form.is_valid():

            try:

                update_student(
                    student=student,
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    dob=form.cleaned_data["dob"],
                    gender=form.cleaned_data["gender"],
                    academic_session=form.cleaned_data["academic_session"],
                    section=form.cleaned_data["section"],
                    roll_number=form.cleaned_data["roll_number"],
                    blood_group=form.cleaned_data["blood_group"],
                    address=form.cleaned_data["address"],
                    previous_school=form.cleaned_data["previous_school"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_success(
                    request=request,
                    template="students/partials/student_table.html",
                    context={
                        "students": get_students(
                            tenant=request.tenant,
                        ),
                    },
                    event="modal:close",
                )

    else:

        form = StudentForm(
            instance=student,
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="students/modals/student_form.html",
        context={
            "form": form,
            "student": student,
            "title": "Edit Student",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "students:student_update",
                kwargs={
                    "pk": student.pk,
                },
            ),
            "target": "#student-table",
        },
    )


@login_required
@permission_required(**permissions.EDIT)
def student_profile_update(request, pk):
    """
    Update a student from the Student Profile.
    """

    student = get_student(
        tenant=request.tenant,
        pk=pk,
    )

    if request.method == "POST":

        form = StudentForm(
            request.POST,
            instance=student,
            tenant=request.tenant,
        )

        if form.is_valid():

            try:

                update_student(
                    student=student,
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    dob=form.cleaned_data["dob"],
                    gender=form.cleaned_data["gender"],
                    academic_session=form.cleaned_data["academic_session"],
                    section=form.cleaned_data["section"],
                    roll_number=form.cleaned_data["roll_number"],
                    blood_group=form.cleaned_data["blood_group"],
                    address=form.cleaned_data["address"],
                    previous_school=form.cleaned_data["previous_school"],
                )

            except ValidationError as e:

                form.add_error(
                    None,
                    e.message,
                )

            else:

                return render_redirect(
                    url=reverse(
                        "students:student_detail",
                        kwargs={
                            "pk": student.pk,
                        },
                    ),
                )

    else:

        form = StudentForm(
            instance=student,
            tenant=request.tenant,
        )

    return render_modal(
        request=request,
        template="students/modals/student_form.html",
        context={
            "form": form,
            "student": student,
            "title": "Edit Student",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "students:student_profile_update",
                kwargs={
                    "pk": student.pk,
                },
            ),
        },
    )