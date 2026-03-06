from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("captcha/", views.captcha_image, name="captcha_image"),
    path("login/", views.EmailLoginView.as_view(), name="login"),
    path("face-login/", views.face_login, name="face_login"),
    path("face-enroll/", views.face_enroll_page, name="face_enroll_page"),
    path("face-enroll/save/", views.face_enroll, name="face_enroll"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/forgot_password.html",
            email_template_name="registration/password_reset_email.txt",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_forgot",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_verify.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path("profile/", views.profile, name="profile"),
    path("personal/", views.personal_page, name="personal_page"),
    path("merchant/dashboard/", views.merchant_dashboard, name="merchant_dashboard"),
]
