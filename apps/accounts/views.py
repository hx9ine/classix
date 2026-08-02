from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from .forms import LoginForm
from .services import AuthenticationService


class LoginView(View):
    template_name = "accounts/login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("academic_structure:academic_session_list")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = LoginForm()

        return render(
            request,
            self.template_name,
            {
                "form": form,
            },
        )

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            user = AuthenticationService.login(
                request=request,
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )

            if user:
                return redirect("academic_structure:academic_session_list")

            messages.error(
                request,
                "Invalid email or password.",
            )

        return render(
            request,
            self.template_name,
            {
                "form": form,
            },
        )


from django.contrib.auth.mixins import LoginRequiredMixin

class LogoutView(LoginRequiredMixin, View):
    def post(self, request):
        AuthenticationService.logout(request)
        return redirect("accounts:login")