from django.urls import path

from .views import (
    subject_create,
    subject_delete,
    subject_list,
    subject_update,
)

app_name = "academics"

urlpatterns = [
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
]