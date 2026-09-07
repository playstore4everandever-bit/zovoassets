from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_step1, name="register"),
    path("register/plan/", views.register_step2, name="register_step2"),
    path("register/invest/", views.register_step3, name="register_step3"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    path("careers/", views.careers, name="careers"),
]
