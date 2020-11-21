from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings
from rentals import views as rentals_views

from backoffice import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
]
