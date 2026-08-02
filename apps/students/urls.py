from django.urls import path

from .views import (
    student_detail,
    student_list,
    student_profile_update,
    student_update,
)

app_name = "students"

urlpatterns = [
    path(
        "",
        student_list,
        name="student_list",
    ),
    path(
        "<uuid:pk>/edit/",
        student_update,
        name="student_update",
    ),
    path(
        "<uuid:pk>/",
        student_detail,
        name="student_detail",
    ),
    path(
        "<uuid:pk>/profile/edit/",
        student_profile_update,
        name="student_profile_update",
    ),
]