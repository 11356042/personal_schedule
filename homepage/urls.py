from django.urls import path
from . import views

app_name="homepage"

urlpatterns = [
    path("", views.schedule, name="schedule"),
    path("logout/", views.logout_view, name="logout"),
]