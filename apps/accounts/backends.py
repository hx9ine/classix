from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class TenantAuthenticationBackend(BaseBackend):
    """
    Authenticates a user within the current tenant.
    """

    def authenticate(
        self,
        request,
        username=None,
        password=None,
        email=None,
        **kwargs,
    ):
        if request is None:
            return None

        tenant = getattr(request, "tenant", None)

        if tenant is None:
            return None

        email = email or username

        if not email or not password:
            return None

        user = User.objects.filter(
            tenant=tenant,
            email__iexact=email,
        ).first()

        if user is None:
            return None

        if not user.check_password(password):
            return None

        if not user.is_active:
            return None

        if not user.is_email_verified:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None