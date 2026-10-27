from django.urls import path
from . import views

app_name="login"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("me/", views.me_view, name="me"),
]