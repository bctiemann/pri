"""pri URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from two_factor.urls import urlpatterns as tf_urls

from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings
from fleet import views as rentals_views
from users import views as users_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Django admin site (generic database backend operations, CRUD, user management, etc)
    path('spork/', admin.site.urls),

    path('sign_out/', users_views.LogoutView.as_view(next_page='home'), name='sign-out'),

    path('recovery/password_reset/',
         users_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             from_email=settings.SUPPORT_EMAIL,
             extra_email_context={
                 'site_name': settings.COMPANY_NAME
             },
         ),
         name='password_reset',
         ),
    path('recovery/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'
         ),
    path('recovery/reset/<uidb64>/<token>/',
         users_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'
         ),
    path('recovery/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'
         ),

    # This is an example of directly registering an app's views in the central site's urls.py. As the site grows,
    # it might be better for each app dir to have its own urls.py and for this file to include that app's urls.py
    # at a specified mount point.
    path('', rentals_views.HomeView.as_view(), name='home'), # Class-based view version
    # path('', rentals_views.home, name='home'), # Function-based view version

    # This is an example of an app's own namespaced urls.py being included in the main one at a mount point.
    # This app contains the legacy site's administrative/business UI.
    path('backoffice/', include(('backoffice.urls', 'backoffice'), namespace='backoffice')),

    path('', include(tf_urls, 'two_factor')),
]

# This maps the MEDIA_ROOT url for local development
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
