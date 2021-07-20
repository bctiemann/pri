from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings

from fleet import views as fleet_views
from customer_portal import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]
