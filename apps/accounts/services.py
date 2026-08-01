from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout,
)
from django.http import HttpRequest

from apps.accounts.models import User


class AuthenticationService:
    """
    Handles user authentication and session management.
    """

    @staticmethod
    def login(
        request: HttpRequest,
        email: str,
        password: str,
    ) -> User | None:
        """
        Authenticate a user within the current tenant and
        establish an authenticated session.

        Returns:
            User: The authenticated user.
            None: If authentication fails.
        """
        user = authenticate(
            request=request,
            email=email,
            password=password,
        )

        if user is None:
            return None

        django_login(request, user)
        request.session.cycle_key()

        return user

    @staticmethod
    def logout(request: HttpRequest) -> None:
        """
        End the current authenticated session.
        """
        django_logout(request)