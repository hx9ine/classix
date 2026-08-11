from django.urls import path

from .views import (
    attendance_list,
    attendance_mark,
)


app_name = "attendance"


urlpatterns = [
    path(
        "",
        attendance_list,
        name="attendance_list",
    ),
    path(
        "mark/",
        attendance_mark,
        name="attendance_mark",
    ),
]