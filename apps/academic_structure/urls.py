from django.urls import path

from .views import (
    academic_session_create,
    academic_session_delete,
    academic_session_list,
    academic_session_update,
    class_level_create,
    class_level_delete,
    class_level_list,
    class_level_update,
    section_create,
    section_delete,
    section_list,
    section_update,
)

app_name = "academic_structure"

urlpatterns = [

    # =========================================================================
    # Academic Sessions
    # =========================================================================

    path(
        "sessions/",
        academic_session_list,
        name="academic_session_list",
    ),
    path(
        "sessions/create/",
        academic_session_create,
        name="academic_session_create",
    ),
    path(
        "sessions/<uuid:pk>/update/",
        academic_session_update,
        name="academic_session_update",
    ),
    path(
        "sessions/<uuid:pk>/delete/",
        academic_session_delete,
        name="academic_session_delete",
    ),

    # =========================================================================
    # Class Levels
    # =========================================================================

    path(
        "class-levels/",
        class_level_list,
        name="class_level_list",
    ),
    path(
        "class-levels/create/",
        class_level_create,
        name="class_level_create",
    ),
    path(
        "class-levels/<uuid:pk>/update/",
        class_level_update,
        name="class_level_update",
    ),
    path(
        "class-levels/<uuid:pk>/delete/",
        class_level_delete,
        name="class_level_delete",
    ),

    # =========================================================================
    # Sections
    # =========================================================================

    path(
        "sections/",
        section_list,
        name="section_list",
    ),
    path(
        "sections/create/",
        section_create,
        name="section_create",
    ),
    path(
        "sections/<uuid:pk>/update/",
        section_update,
        name="section_update",
    ),
    path(
        "sections/<uuid:pk>/delete/",
        section_delete,
        name="section_delete",
    ),
]