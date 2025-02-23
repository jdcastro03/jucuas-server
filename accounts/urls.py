from django.urls import path
from django.contrib.auth import views as django_views
from . import views

urlpatterns = [
    # AUTH
    path('login/', views.token),
    path('token/refresh/', views.refresh_token),
    path('logout/', views.revoke_token),

    # USER CURRENT
    path('users/current/', views.UserProfile.as_view(), name='users'),

    # PASSWORD CHANGE
    path('password/change/', views.update_user_password),
    path('password/change/token/', views.change_password_with_token),
    path('password/recovery/', views.recovery_password),
    path('password/change/admin/notify/<int:user_id>/', views.change_user_password_with_notification, name='change_password_with_notification'),  # Nueva ruta

    # DEBUGGIN'
    path('resetpwd/', django_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', django_views.PasswordResetDoneView.as_view(), name='password_reset_sent'),
    path('reset/<uidb64>/token', django_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete', django_views.PasswordResetConfirmView.as_view(), name='password_reset_complete'),

    # ACTUALIZAR DATOS DEL USUARIO X
    path('update_name/', views.update_name),
    path('update_email/', views.update_email),
    path('update_gender/', views.update_gender),
    path('update_phone/', views.update_phone),
    path('validate_token/<email>/<token>', views.validate_token),
    path('check_token/<email>/<token>', views.check_token),
    path('check_token/<email>', views.verificar_token),
    path('my_gender/', views.get_gender, name='my_gender'),

    path('register_mail/', views.register_mail, name='my_gender'),
]