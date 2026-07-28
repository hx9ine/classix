from django.contrib.auth import authenticate, login, logout


class AuthenticationService:
    @staticmethod
    def login(request, email, password):
        user = authenticate(
            request=request,
            email=email,
            password=password,
        )

        if user is None:
            return None

        login(request, user)
        return user

    @staticmethod
    def logout(request):
        logout(request)