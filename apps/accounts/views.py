from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views import View

from .forms import LoginForm
from .services import AuthenticationService

# Create your views here.

class LoginView(AccessMixin, View):
    template_name = "accounts/login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = LoginForm()
        return render(
            request,
            self.template_name,
            {"form": form},
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
                # return redirect("dashboard:index")
                return HttpResponse("Login successful")

            messages.error(request, "Invalid email or password.")

        return render(
            request,
            self.template_name,
            {"form": form},
        )



from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Temporary for UI verification only
# @login_required
def app_preview(request):
    navigation = [
        {
            "title": "Home",
            "items": [
                {
                    "label": "Dashboard",
                    "url": "#",
                    "icon": "",
                }
            ],
        },
        {
            "title": "Academics",
            "items": [
                {
                    "label": "Students",
                    "url": "#",
                    "icon": "",
                },
                {
                    "label": "Attendance",
                    "url": "#",
                    "icon": "",
                },
                {
                    "label": "Grades",
                    "children": [
                        {
                            "label": "Exam Grades",
                            "url": "#",
                        },
                        {
                            "label": "Report Cards",
                            "url": "#",
                        },
                    ],
                    "icon": "",
                },
            ],
        },
    ]

    return render(
        request,
        "dashboard/index.html",
    )