from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings

from fleet import views as fleet_views
from backoffice import views
from backoffice.views import (
    vehicles, reservations, rentals, guided_drives, employees, customers, coupons, toll_tags, tax_rates, bbs
)


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('post/', views.HomeAddPostView.as_view(), name='home-add-post'),
    path('post/<int:pk>/reply/', views.HomeReplyPostView.as_view(), name='home-reply-post'),
    path('post/<int:pk>/edit/', views.HomeEditPostView.as_view(), name='home-edit-post'),
    path('post/<int:pk>/delete/', views.HomeDeletePostView.as_view(), name='home-delete-post'),

    path('landing/', views.LandingView.as_view(), name='landing'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('track_activity/', views.TrackActivityView.as_view(), name='track-activity'),

    path('vehicles/', vehicles.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/active/', vehicles.VehicleListView.as_view(active_only=True), name='vehicle-list-active'),
    path('vehicles/create/', vehicles.VehicleCreateView.as_view(is_create_view=True), name='vehicle-create'),
    path('vehicles/<int:pk>/', vehicles.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicles/<int:vehicle_id>/<str:media_type>/<int:pk>/promote/', vehicles.VehicleMediaPromoteView.as_view(), name='vehicle-media-promote'),
    path('vehicles/<int:vehicle_id>/<str:media_type>/<int:pk>/delete/', vehicles.VehicleMediaDeleteView.as_view(), name='vehicle-media-delete'),
    path('vehicles/type_<int:vehicle_type>/', vehicles.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/marketing/<int:pk>/showcase/', vehicles.VehicleShowcaseView.as_view(), name='vehicle-showcase'),
    path('vehicles/marketing/<int:pk>/thumbnail/', vehicles.VehicleThumbnailView.as_view(), name='vehicle-thumbnail'),
    path('vehicles/marketing/<int:pk>/inspection/', vehicles.VehicleInspectionView.as_view(), name='vehicle-inspection'),
    path('vehicles/marketing/<int:pk>/mobile_thumb/', vehicles.VehicleMobileThumbView.as_view(), name='vehicle-mobile-thumb'),
    path('vehicles/marketing/<int:pk>/pictures/', vehicles.VehiclePicturesView.as_view(), name='vehicle-pictures'),
    path('vehicles/marketing/<int:pk>/videos/', vehicles.VehicleVideosView.as_view(), name='vehicle-videos'),

    path('reservations/', reservations.ReservationListView.as_view(), name='reservation-list'),
    path('reservations/create/', reservations.ReservationCreateView.as_view(is_create_view=True), name='reservation-create'),
    path('reservations/<int:pk>/', reservations.ReservationDetailView.as_view(), name='reservation-detail'),
    path('reservations/<int:pk>/delete/', reservations.ReservationDeleteView.as_view(), name='reservation-delete'),
    path('reservations/<int:pk>/convert/', reservations.ReservationConvertToRentalView.as_view(), name='reservation-convert'),

    path('rentals/', rentals.RentalListView.as_view(), name='rental-list'),
    path('rentals/create/', rentals.RentalCreateView.as_view(is_create_view=True), name='rental-create'),
    path('rentals/<int:pk>/', rentals.RentalDetailView.as_view(), name='rental-detail'),
    path('rentals/<int:pk>/delete/', rentals.RentalDeleteView.as_view(), name='rental-delete'),
    path('rentals/<int:pk>/drivers/', rentals.RentalDriversView.as_view(), name='rental-drivers'),
    path('rentals/<int:pk>/drivers/add/', rentals.RentalDriverAddView.as_view(), name='rental-drivers-add'),
    path('rentals/<int:pk>/drivers/remove/', rentals.RentalDriverRemoveView.as_view(), name='rental-drivers-remove'),
    path('rentals/<int:pk>/drivers/promote/', rentals.RentalDriverPromoteView.as_view(), name='rental-drivers-promote'),
    path('rentals/<int:pk>/generate_contract/', rentals.RentalGenerateContractView.as_view(), name='rental-generate-contract'),

    path('employees/', employees.EmployeeListView.as_view(), name='employee-list'),
    path('employees/create/', employees.EmployeeCreateView.as_view(is_create_view=True), name='employee-create'),
    path('employees/<int:pk>/', employees.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/delete/', employees.EmployeeDeleteView.as_view(), name='employee-delete'),

    path('customers/', customers.CustomerListView.as_view(), name='customer-list'),
    path('customers/create/', customers.CustomerCreateView.as_view(is_create_view=True), name='customer-create'),
    path('customers/<int:pk>/', customers.CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<int:pk>/delete/', customers.CustomerDeleteView.as_view(), name='customer-delete'),
    path('customers/<int:pk>/clone/', customers.CustomerCloneView.as_view(), name='customer-clone'),

    path('coupons/', coupons.CouponListView.as_view(), name='coupon-list'),
    path('coupons/create/', coupons.CouponCreateView.as_view(is_create_view=True), name='coupon-create'),
    path('coupons/<int:pk>/', coupons.CouponDetailView.as_view(), name='coupon-detail'),
    path('coupons/<int:pk>/delete/', coupons.CouponDeleteView.as_view(), name='coupon-delete'),

    path('toll_tags/', toll_tags.TollTagListView.as_view(), name='tolltag-list'),
    path('toll_tags/create/', toll_tags.TollTagCreateView.as_view(is_create_view=True), name='tolltag-create'),
    path('toll_tags/<int:pk>/', toll_tags.TollTagDetailView.as_view(), name='tolltag-detail'),
    path('toll_tags/<int:pk>/delete/', toll_tags.TollTagDeleteView.as_view(), name='tolltag-delete'),

    path('tax_rates/', tax_rates.TaxRateListView.as_view(), name='taxrate-list'),
    path('tax_rates/create/', tax_rates.TaxRateCreateView.as_view(is_create_view=True), name='taxrate-create'),
    path('tax_rates/<int:pk>/', tax_rates.TaxRateDetailView.as_view(), name='taxrate-detail'),
    path('tax_rates/<int:pk>/delete/', tax_rates.TaxRateDeleteView.as_view(), name='taxrate-delete'),

    path('joy_rides/', guided_drives.JoyRideListView.as_view(), name='joyride-list'),
    path('joy_rides/create/', guided_drives.JoyRideCreateView.as_view(is_create_view=True), name='joyride-create'),
    path('joy_rides/<int:pk>/', guided_drives.JoyRideDetailView.as_view(), name='joyride-detail'),
    path('joy_rides/<int:pk>/delete/', guided_drives.JoyRideDeleteView.as_view(), name='joyride-delete'),
    path('performance_experiences/', guided_drives.PerformanceExperienceListView.as_view(), name='perfexp-list'),
    path('performance_experiences/create/', guided_drives.PerformanceExperienceCreateView.as_view(is_create_view=True), name='perfexp-create'),
    path('performance_experiences/<int:pk>/', guided_drives.PerformanceExperienceDetailView.as_view(), name='perfexp-detail'),
    path('performance_experiences/<int:pk>/delete/', guided_drives.PerformanceExperienceDeleteView.as_view(), name='perfexp-delete'),

    path('bbs/', bbs.BBSListView.as_view(), name='bbs-list'),
    path('bbs/<int:pk>/reply/', bbs.BBSReplyPostView.as_view(), name='bbs-reply'),
    path('bbs/<int:pk>/edit/', bbs.BBSEditPostView.as_view(), name='bbs-edit'),
    path('bbs/<int:pk>/delete/', bbs.BBSDeletePostView.as_view(), name='bbs-delete'),
]
