from django.db import transaction

from ..models import AcademicSession


# ============================================================================
# Academic Session Services
# ============================================================================

@transaction.atomic
def create_academic_session(*, tenant, form):
    """
    Create a new academic session.
    """
    session = form.save(commit=False)
    session.tenant = tenant

    if session.is_current:
        AcademicSession.objects.filter(
            tenant=tenant,
            is_current=True,
        ).update(is_current=False)

    session.save()

    return session


@transaction.atomic
def update_academic_session(*, tenant, instance, form):
    """
    Update an academic session.
    """
    session = form.save(commit=False)

    if session.is_current:
        AcademicSession.objects.filter(
            tenant=tenant,
            is_current=True,
        ).exclude(pk=instance.pk).update(is_current=False)

    session.save()

    return session


@transaction.atomic
def delete_academic_session(*, instance):
    """
    Delete an academic session.
    """
    instance.delete()


@transaction.atomic
def set_current_academic_session(*, tenant, session):
    """
    Set one academic session as current.
    """
    AcademicSession.objects.filter(
        tenant=tenant,
        is_current=True,
    ).update(is_current=False)

    session.is_current = True
    session.save(update_fields=["is_current"])


