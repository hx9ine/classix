from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models import TimetablePeriod


# ============================================================================
# List
# ============================================================================

def get_timetable_periods(
    *,
    tenant,
) -> QuerySet[TimetablePeriod]:
    """
    Return all timetable periods for a tenant.
    """

    return (
        TimetablePeriod.objects
        .filter(
            tenant=tenant,
        )
        .select_related(
            "section",
            "section__academic_session",
            "section__class_level",
            "subject",
            "staff",
        )
        .order_by(
            "day_of_week",
            "start_time",
        )
    )


def get_timetable_periods_by_section(
    *,
    tenant,
    section,
) -> QuerySet[TimetablePeriod]:
    """
    Return timetable periods for a section.
    """

    return (
        get_timetable_periods(
            tenant=tenant,
        )
        .filter(
            section=section,
        )
        .order_by(
            "day_of_week",
            "start_time",
        )
    )


def get_timetable_periods_by_staff(
    *,
    tenant,
    staff,
) -> QuerySet[TimetablePeriod]:
    """
    Return timetable periods assigned to a staff member.
    """

    return (
        get_timetable_periods(
            tenant=tenant,
        )
        .filter(
            staff=staff,
        )
        .order_by(
            "day_of_week",
            "start_time",
        )
    )


# ============================================================================
# Retrieve
# ============================================================================

def get_timetable_period(
    *,
    tenant,
    pk,
) -> TimetablePeriod:
    """
    Return a single timetable period.
    """

    return get_object_or_404(
        TimetablePeriod.objects.select_related(
            "section",
            "section__academic_session",
            "section__class_level",
            "subject",
            "staff",
        ),
        tenant=tenant,
        pk=pk,
    )


# ============================================================================
# Day
# ============================================================================

def get_timetable_periods_by_day(
    *,
    tenant,
    day_of_week,
) -> QuerySet[TimetablePeriod]:
    """
    Return timetable periods for a tenant on a specific day.
    """

    return (
        get_timetable_periods(
            tenant=tenant,
        )
        .filter(
            day_of_week=day_of_week,
        )
        .order_by(
            "start_time",
        )
    )