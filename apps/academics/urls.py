from django.urls import path

from .views import (
    homework_create,
    homework_delete,
    homework_list,
    homework_update,
    subject_create,
    subject_delete,
    subject_list,
    subject_update,
    timetable_create,
    timetable_delete,
    timetable_list,
    timetable_update,
)


app_name = "academics"


urlpatterns = [
    # =========================================================================
    # Subjects
    # =========================================================================

    path(
        "subjects/",
        subject_list,
        name="subject_list",
    ),

    path(
        "subjects/create/",
        subject_create,
        name="subject_create",
    ),

    path(
        "subjects/<uuid:pk>/update/",
        subject_update,
        name="subject_update",
    ),

    path(
        "subjects/<uuid:pk>/delete/",
        subject_delete,
        name="subject_delete",
    ),

    # =========================================================================
    # Timetable
    # =========================================================================

    path(
        "timetable/",
        timetable_list,
        name="timetable_list",
    ),

    path(
        "timetable/create/",
        timetable_create,
        name="timetable_create",
    ),

    path(
        "timetable/<uuid:pk>/update/",
        timetable_update,
        name="timetable_update",
    ),

    path(
        "timetable/<uuid:pk>/delete/",
        timetable_delete,
        name="timetable_delete",
    ),

    # =========================================================================
    # Homework
    # =========================================================================

    path(
        "homework/",
        homework_list,
        name="homework_list",
    ),

    path(
        "homework/create/",
        homework_create,
        name="homework_create",
    ),

    path(
        "homework/<uuid:pk>/update/",
        homework_update,
        name="homework_update",
    ),

    path(
        "homework/<uuid:pk>/delete/",
        homework_delete,
        name="homework_delete",
    ),
]