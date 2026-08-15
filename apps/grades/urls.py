from django.urls import path

from .views import (
    exam_create,
    exam_delete,
    exam_list,
    exam_update,
    grade_entry_create,
    grade_entry_list,
    grade_entry_update,
)


app_name = "grades"


urlpatterns = [
    # Exams
    path(
        "exams/",
        exam_list,
        name="exam_list",
    ),
    path(
        "exams/create/",
        exam_create,
        name="exam_create",
    ),
    path(
        "exams/<uuid:pk>/edit/",
        exam_update,
        name="exam_update",
    ),
    path(
        "exams/<uuid:pk>/delete/",
        exam_delete,
        name="exam_delete",
    ),

    # Grade Entries
    path(
        "entries/",
        grade_entry_list,
        name="grade_entry_list",
    ),
    path(
        "entries/create/",
        grade_entry_create,
        name="grade_entry_create",
    ),
    path(
        "entries/<uuid:pk>/edit/",
        grade_entry_update,
        name="grade_entry_update",
    ),
]