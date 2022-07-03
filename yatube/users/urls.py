from django.contrib.auth.views import (
    PasswordResetDoneView, LogoutView, LoginView,
    PasswordResetView, PasswordResetCompleteView,
    PasswordChangeView, PasswordResetConfirmView
)
from django.views.generic import TemplateView
from django.urls import path, reverse_lazy

from . import views


app_name = 'users'


urlpatterns = [
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/', LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
            success_url=reverse_lazy('users:password_change_done')),
        name='password_change_form'
    ),
    path(
        'password_change_done/',
        TemplateView.as_view(
            template_name="users/password_change_done.html"),
        name="password_change_done"
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset_form.html'),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"),
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"),
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"),
    ),
]
