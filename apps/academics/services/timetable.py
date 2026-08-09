from django.db import transaction

from ..models import TimetablePeriod


# ============================================================================
# Timetable Period Services
# ============================================================================

@transaction.atomic
def create_timetable_period(
    *,
    tenant,
    form,
):
    """
    Create a timetable period.
    """

    timetable_period = form.save(
        commit=False,
    )

    timetable_period.tenant = tenant

    timetable_period.full_clean()
    timetable_period.save()

    return timetable_period


@transaction.atomic
def update_timetable_period(
    *,
    form,
):
    """
    Update a timetable period.
    """

    timetable_period = form.save(
        commit=False,
    )

    timetable_period.full_clean()
    timetable_period.save()

    return timetable_period


@transaction.atomic
def delete_timetable_period(
    *,
    timetable_period,
):
    """
    Delete a timetable period.
    """

    timetable_period.delete()