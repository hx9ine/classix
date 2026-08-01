from django.urls import path

from .views import (
    staff_create,
    staff_delete,
    staff_detail,
    staff_list,
    staff_profile_update,
    staff_update,
)

app_name = "staff"

urlpatterns = [
    path(
        "",
        staff_list,
        name="staff_list",
    ),
    path(
        "create/",
        staff_create,
        name="staff_create",
    ),
    path(
        "<uuid:pk>/",
        staff_detail,
        name="staff_detail",
    ),
    path(
        "<uuid:pk>/edit/",
        staff_update,
        name="staff_update",
    ),
    path(
        "<uuid:pk>/profile/edit/",
        staff_profile_update,
        name="staff_profile_update",
    ),
    path(
        "<uuid:pk>/delete/",
        staff_delete,
        name="staff_delete",
    ),
]