from django.urls import reverse

from apps.core.crud import (
    redirect_success,
    render_success,
)
from apps.core.htmx import (
    htmx_modal,
    render_partial,
)

from ..forms import StudentForm
from ..selectors import (
    get_student,
    get_students,
)
from ..services import update_student


# ============================================================================
# Student Views
# ============================================================================

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
        else "students/pages/students.html"
    )

    return render_partial(
        request=request,
        template=template,
        context={
            "students": students,
        },
    )


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

            update_student(
                form=form,
            )

            return render_success(
                request=request,
                template="students/partials/student_table.html",
                context={
                    "students": get_students(
                        tenant=request.tenant,
                    ),
                },
            )

    else:

        form = StudentForm(
            instance=student,
            tenant=request.tenant,
        )

    return htmx_modal(
        request=request,
        template="students/modals/student_form.html",
        context={
            "form": form,
            "student": student,
            "title": "Edit Student",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "students:student_update",
                args=[student.pk],
            ),
            "target": "#student-table",
        },
    )


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

            update_student(
                form=form,
            )

            return redirect_success(
                url=reverse(
                    "students:student_detail",
                    args=[student.pk],
                ),
            )

    else:

        form = StudentForm(
            instance=student,
            tenant=request.tenant,
        )

    return htmx_modal(
        request=request,
        template="students/modals/student_form.html",
        context={
            "form": form,
            "student": student,
            "title": "Edit Student",
            "submit_label": "Save Changes",
            "post_url": reverse(
                "students:student_profile_update",
                args=[student.pk],
            ),
        },
    )