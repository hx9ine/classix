from django.urls import path

from .views import (
    role_create,
    role_create_inline,
    role_list,
    role_update,
)

app_name = "rbac"

urlpatterns = [
    path(
        "roles/",
        role_list,
        name="role_list",
    ),
    path(
        "roles/create/",
        role_create,
        name="role_create",
    ),
    path(
        "roles/<uuid:pk>/edit/",
        role_update,
        name="role_update",
    ),
    path(
        "roles/inline/create/",
        role_create_inline,
        name="role_create_inline",
    ),
]