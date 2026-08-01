from django.urls import path

from .views import (
    applicant_create,
    applicant_delete,
    applicant_enroll,
    applicant_list,
    applicant_update,
)

app_name = "admissions"

urlpatterns = [
    # =========================================================================
    # Applicants
    # =========================================================================

    path(
        "applicants/",
        applicant_list,
        name="applicant_list",
    ),

    path(
        "applicants/create/",
        applicant_create,
        name="applicant_create",
    ),

    path(
        "applicants/<uuid:pk>/edit/",
        applicant_update,
        name="applicant_update",
    ),

    path(
        "applicants/<uuid:pk>/enroll/",
        applicant_enroll,
        name="applicant_enroll",
    ),

    path(
        "applicants/<uuid:pk>/delete/",
        applicant_delete,
        name="applicant_delete",
    ),
]