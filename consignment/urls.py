from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings
from django.urls import reverse
from django.views.generic.base import RedirectView

from fleet import views as fleet_views
from consignment import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
]
