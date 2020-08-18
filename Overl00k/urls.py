from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

from hotel import views as hotel_views


urlpatterns = [
    path('hotel/', include('hotel.urls', namespace='hotel')),
    path('admin/', admin.site.urls),
    path('profile/<str:username>/', hotel_views.profile, name='profile'),
    path('register/', hotel_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='hotel/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='hotel/auth/logout.html'), name='logout'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='hotel/auth/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='hotel/auth/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='hotel/auth/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='hotel/auth/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)