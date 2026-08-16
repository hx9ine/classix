from django.urls import path

from .views import billing_dashboard


app_name = "billing"


urlpatterns = [
    path(
        "",
        billing_dashboard,
        name="dashboard",
    ),
]