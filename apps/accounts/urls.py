from django.urls import path
from .views import UserLoginView, UserLogoutView, register, profile
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
    path("profile/", views.profile, name="profile"),
    
    path("toggle-mode/", views.toggle_mode, name="toggle_mode"),
]