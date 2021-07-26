from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings

from fleet import views as fleet_views
from backoffice import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('track_activity/', views.TrackActivityView.as_view(), name='track-activity'),

    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/create/', views.VehicleCreateView.as_view(), name='vehicle-create'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicles/<str:vehicle_type>/', views.VehicleListView.as_view(), name='vehicle-list'),
]
