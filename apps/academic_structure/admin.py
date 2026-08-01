from django.contrib import admin

from .models import AcademicSession, ClassLevel, Section


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date",
        "is_current",
    )
    list_filter = (
        "is_current",
    )
    search_fields = (
        "name",
    )
    ordering = (
        "-start_date",
    )


@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sort_order",
    )
    list_editable = (
        "sort_order",
    )
    search_fields = (
        "name",
    )
    ordering = (
        "sort_order",
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "class_level",
        "academic_session",
    )
    list_filter = (
        "academic_session",
        "class_level",
    )
    search_fields = (
        "name",
        "class_level__name",
    )
    ordering = (
        "class_level__sort_order",
        "name",
    )