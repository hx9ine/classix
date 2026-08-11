from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render

from apps.core.crud import render_success

from ..forms import AttendanceMarkingForm
from ..permissions import attendance as permissions
from ..selectors import (
    get_attendance_roster,
    get_attendance_sections,
)
from ..services import mark_attendance

from apps.rbac.decorators import permission_required


def _build_attendance_students(
    *,
    form,
    students,
):
    """
    Prepare dynamic attendance form fields for template rendering.
    """

    return [
        {
            "student": student,
            "status_field": form[
                form.status_field_name(student)
            ],
            "note_field": form[
                form.note_field_name(student)
            ],
        }
        for student in students
    ]


# ============================================================================
# Attendance Views
# ============================================================================

@login_required
@permission_required(**permissions.VIEW)
def attendance_list(request):
    """
    Display the attendance marking screen.
    """

    staff = getattr(
        request.user,
        "staff_profile",
        None,
    )

    sections = get_attendance_sections(
        tenant=request.tenant,
        staff=staff,
    )

    section = None

    section_pk = request.GET.get("section")

    if section_pk:
        section = sections.filter(
            pk=section_pk,
        ).first()

    students = (
        get_attendance_roster(
            tenant=request.tenant,
            section=section,
        )
        if section is not None
        else []
    )

    form = AttendanceMarkingForm(
        tenant=request.tenant,
        students=students,
        initial={
            "section": section,
        },
    )

    attendance_students = _build_attendance_students(
        form=form,
        students=students,
    )

    template = (
        "attendance/partials/attendance_roster.html"
        if request.htmx and section is not None
        else "attendance/pages/attendance.html"
    )

    return render(
        request,
        template,
        {
            "form": form,
            "sections": sections,
            "section": section,
            "students": students,
            "attendance_students": attendance_students,
        },
    )


@login_required
@permission_required(**permissions.CREATE)
def attendance_mark(request):
    """
    Mark attendance for a section roster.
    """

    if request.method != "POST":
        return render(
            request,
            "attendance/pages/attendance.html",
            {
                "form": AttendanceMarkingForm(
                    tenant=request.tenant,
                ),
                "sections": get_attendance_sections(
                    tenant=request.tenant,
                    staff=getattr(
                        request.user,
                        "staff_profile",
                        None,
                    ),
                ),
            },
        )

    staff = getattr(
        request.user,
        "staff_profile",
        None,
    )

    if staff is None:

        return render(
            request,
            "attendance/pages/attendance.html",
            {
                "form": AttendanceMarkingForm(
                    request.POST,
                    tenant=request.tenant,
                ),
                "sections": get_attendance_sections(
                    tenant=request.tenant,
                    staff=None,
                ),
                "error": (
                    "The current user is not linked to a staff profile "
                    "and cannot mark attendance."
                ),
            },
        )

    section_pk = request.POST.get("section")

    sections = get_attendance_sections(
        tenant=request.tenant,
        staff=staff,
    )

    section = sections.filter(
        pk=section_pk,
    ).first()

    if section is None:

        form = AttendanceMarkingForm(
            request.POST,
            tenant=request.tenant,
        )

        form.add_error(
            "section",
            "Select a valid section.",
        )

        return render(
            request,
            "attendance/pages/attendance.html",
            {
                "form": form,
                "sections": sections,
            },
        )

    students = get_attendance_roster(
        tenant=request.tenant,
        section=section,
    )

    form = AttendanceMarkingForm(
        request.POST,
        tenant=request.tenant,
        students=students,
    )

    attendance_students = _build_attendance_students(
        form=form,
        students=students,
    )

    print("ATTENDANCE FORM DATA:", request.POST)
    print("ATTENDANCE FORM ERRORS:", form.errors)

    if form.is_valid():

        attendance = [
            {
                "student": student,
                "status": form.get_student_status(student),
                "note": form.get_student_note(student),
            }
            for student in students
        ]

        try:

            mark_attendance(
                tenant=request.tenant,
                section=section,
                date=form.cleaned_data["date"],
                period=form.cleaned_data["period"],
                academic_session=section.academic_session,
                marked_by=staff,
                attendance=attendance,
            )

        except ValidationError as e:

            if hasattr(e, "message_dict"):

                for field, messages in e.message_dict.items():

                    for message in messages:
                        form.add_error(
                            field,
                            message,
                        )

            else:

                form.add_error(
                    None,
                    e.message,
                )

        else:

            return render_success(
                request=request,
                template="attendance/partials/attendance_success.html",
                context={
                    "section": section,
                    "date": form.cleaned_data["date"],
                    "period": form.cleaned_data["period"],
                },
            )

    return render(
        request,
        "attendance/pages/attendance.html",
        {
            "form": form,
            "sections": sections,
            "section": section,
            "students": students,
            "attendance_students": attendance_students,
        },
    )