from django.urls import path

from .views import LoginView
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("app-preview/", views.app_preview, name="app_preview"),
]