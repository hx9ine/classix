from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import permission_required

from .forms import StaffCreateForm, StaffUpdateForm
from .models import Staff
from .services import (
    activate_staff,
    create_staff,
    deactivate_staff,
    update_staff,
)


@login_required
@permission_required("staff", "view")
def staff_list(request):
    staff = (
        Staff.objects
        .filter(tenant=request.tenant)
        .select_related("role", "user")
        .order_by("first_name", "last_name")
    )

    return render(
        request,
        "staff/list.html",
        {
            "staff_list": staff,
        },
    )


@login_required
@permission_required("staff", "create")
def staff_create(request):

    if request.method == "POST":

        form = StaffCreateForm(
            request.POST,
            request.FILES,
            tenant=request.tenant,
        )

        if form.is_valid():

            create_staff(
                tenant=request.tenant,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                role=form.cleaned_data["role"],
                joining_date=form.cleaned_data["joining_date"],
                phone=form.cleaned_data["phone"],
                photo=form.cleaned_data["photo"],
                user=form.cleaned_data["user"],
            )

            messages.success(
                request,
                "Staff member created successfully.",
            )

            return redirect("staff:list")

    else:

        form = StaffCreateForm(
            tenant=request.tenant,
        )

    return render(
        request,
        "staff/form.html",
        {
            "form": form,
            "title": "Add Staff",
        },
    )


@login_required
@permission_required("staff", "edit")
def staff_update(request, pk):

    staff = get_object_or_404(
        Staff,
        pk=pk,
        tenant=request.tenant,
    )

    if request.method == "POST":

        form = StaffUpdateForm(
            request.POST,
            request.FILES,
            instance=staff,
            tenant=request.tenant,
        )

        if form.is_valid():

            update_staff(
                staff=staff,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                role=form.cleaned_data["role"],
                joining_date=form.cleaned_data["joining_date"],
                phone=form.cleaned_data["phone"],
                photo=form.cleaned_data["photo"],
            )

            messages.success(
                request,
                "Staff updated successfully.",
            )

            return redirect(
                "staff:detail",
                pk=staff.pk,
            )

    else:

        form = StaffUpdateForm(
            instance=staff,
            tenant=request.tenant,
        )

    return render(
        request,
        "staff/form.html",
        {
            "form": form,
            "staff": staff,
            "title": "Edit Staff",
        },
    )


@login_required
@permission_required("staff", "edit")
def staff_activate(request, pk):

    staff = get_object_or_404(
        Staff,
        pk=pk,
        tenant=request.tenant,
    )

    activate_staff(staff=staff)

    messages.success(
        request,
        "Staff activated successfully.",
    )

    return redirect(
        "staff:detail",
        pk=staff.pk,
    )


@login_required
@permission_required("staff", "edit")
def staff_deactivate(request, pk):

    staff = get_object_or_404(
        Staff,
        pk=pk,
        tenant=request.tenant,
    )

    deactivate_staff(staff=staff)

    messages.success(
        request,
        "Staff deactivated successfully.",
    )

    return redirect(
        "staff:detail",
        pk=staff.pk,
    )


@login_required
@permission_required("staff", "view")
def staff_detail(request, pk):

    staff = get_object_or_404(
        Staff.objects.select_related(
            "role",
            "user",
        ),
        pk=pk,
        tenant=request.tenant,
    )

    return render(
        request,
        "staff/detail.html",
        {
            "staff": staff,
        },
    )