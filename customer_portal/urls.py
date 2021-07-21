from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings

from fleet import views as fleet_views
from customer_portal import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('confirm_reservation/<str:confirmation_code>/', views.ConfirmReservationView.as_view(), name='confirm-reservation'),
]
