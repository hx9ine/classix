from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class TenantAuthenticationBackend(ModelBackend):
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

        try:
            email = User.objects.normalize_email(email)
            user = User.objects.get(
                tenant=tenant,
                email=email,
            )
        except User.DoesNotExist:
            return None

        if not user.check_password(password):
            return None

        if not self.user_can_authenticate(user):
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None