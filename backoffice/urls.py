from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings

from fleet import views as fleet_views
from backoffice import views
from backoffice.views import vehicles, reservations, employees, customers, coupons


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('landing/', views.LandingView.as_view(), name='landing'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('track_activity/', views.TrackActivityView.as_view(), name='track-activity'),

    path('vehicles/', vehicles.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/active/', vehicles.VehicleListView.as_view(active_only=True), name='vehicle-list-active'),
    path('vehicles/create/', vehicles.VehicleCreateView.as_view(is_create_view=True), name='vehicle-create'),
    path('vehicles/<int:pk>/', vehicles.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicles/<int:pk>/showcase/', vehicles.VehicleShowcaseView.as_view(), name='vehicle-showcase'),
    path('vehicles/<int:pk>/thumbnail/', vehicles.VehicleThumbnailView.as_view(), name='vehicle-thumbnail'),
    path('vehicles/<int:pk>/inspection/', vehicles.VehicleInspectionView.as_view(), name='vehicle-inspection'),
    path('vehicles/<int:pk>/mobile_thumb/', vehicles.VehicleMobileThumbView.as_view(), name='vehicle-mobile-thumb'),
    path('vehicles/<int:pk>/pictures/', vehicles.VehiclePicturesView.as_view(), name='vehicle-pictures'),
    path('vehicles/<int:pk>/videos/', vehicles.VehicleVideosView.as_view(), name='vehicle-videos'),
    path('vehicles/<int:vehicle_id>/<str:media_type>/<int:pk>/promote/', vehicles.VehicleMediaPromoteView.as_view(), name='vehicle-media-promote'),
    path('vehicles/<int:vehicle_id>/<str:media_type>/<int:pk>/delete/', vehicles.VehicleMediaDeleteView.as_view(), name='vehicle-media-delete'),
    path('vehicles/type_<int:vehicle_type>/', vehicles.VehicleListView.as_view(), name='vehicle-list'),

    path('reservations/', reservations.ReservationListView.as_view(), name='reservation-list'),
    path('reservations/create/', reservations.ReservationCreateView.as_view(is_create_view=True), name='reservation-create'),
    path('reservations/<int:pk>/', reservations.ReservationDetailView.as_view(), name='reservation-detail'),
    path('reservations/<int:pk>/delete/', reservations.ReservationDeleteView.as_view(), name='reservation-delete'),

    path('employees/', employees.EmployeeListView.as_view(), name='employee-list'),
    path('employees/create/', employees.EmployeeCreateView.as_view(is_create_view=True), name='employee-create'),
    path('employees/<int:pk>/', employees.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/delete/', employees.EmployeeDeleteView.as_view(), name='employee-delete'),

    path('customers/', customers.CustomerListView.as_view(), name='customer-list'),
    path('customers/create/', customers.CustomerCreateView.as_view(is_create_view=True), name='customer-create'),
    path('customers/<int:pk>/', customers.CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<int:pk>/delete/', customers.CustomerDeleteView.as_view(), name='customer-delete'),

    path('coupons/', coupons.CouponListView.as_view(), name='coupon-list'),
    path('coupons/create/', coupons.CouponCreateView.as_view(is_create_view=True), name='coupon-create'),
    path('coupons/<int:pk>/', coupons.CouponDetailView.as_view(), name='coupon-detail'),
    path('coupons/<int:pk>/delete/', coupons.CouponDeleteView.as_view(), name='coupon-delete'),
]
