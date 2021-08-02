from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings

from fleet import views as fleet_views
from backoffice import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('landing/', views.LandingView.as_view(), name='landing'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('track_activity/', views.TrackActivityView.as_view(), name='track-activity'),

    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/active/', views.VehicleListView.as_view(active_only=True), name='vehicle-list-active'),
    path('vehicles/create/', views.VehicleCreateView.as_view(is_create_view=True), name='vehicle-create'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicles/<int:pk>/showcase/', views.VehicleShowcaseView.as_view(), name='vehicle-showcase'),
    path('vehicles/<int:pk>/thumbnail/', views.VehicleThumbnailView.as_view(), name='vehicle-thumbnail'),
    path('vehicles/<int:pk>/inspection/', views.VehicleInspectionlView.as_view(), name='vehicle-inspection'),
    path('vehicles/<int:pk>/pictures/', views.VehiclePicturesView.as_view(), name='vehicle-pictures'),
    path('vehicles/<int:vehicle_id>/<str:media_type>/<int:pk>/promote/', views.VehicleMediaPromoteView.as_view(), name='vehicle-media-promote'),
    path('vehicles/<str:vehicle_type>/', views.VehicleListView.as_view(), name='vehicle-list'),
]
