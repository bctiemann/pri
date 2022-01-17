from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings
from django.views.generic.base import RedirectView

from fleet import views as fleet_views
from backoffice import views
from backoffice.views import (
    vehicles, reservations, rentals, guided_drives, employees, customers, coupons, toll_tags, tax_rates, bbs,
    consigners, consignment_payments, news, site_content, gift_certificates, adhoc_payments, newsletter_subscriptions,
    stripe_charges, red_flags, survey_responses, damage, service,
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

    path('gift_certificates/', gift_certificates.GiftCertificateListView.as_view(), name='giftcert-list'),
    path('gift_certificates/create/', gift_certificates.GiftCertificateCreateView.as_view(is_create_view=True), name='giftcert-create'),
    path('gift_certificates/<int:pk>/', gift_certificates.GiftCertificateDetailView.as_view(), name='giftcert-detail'),
    path('gift_certificates/<int:pk>/delete/', gift_certificates.GiftCertificateDeleteView.as_view(), name='giftcert-delete'),

    path('adhoc_payments/', adhoc_payments.AdHocPaymentListView.as_view(), name='adhocpayment-list'),
    path('adhoc_payments/create/', adhoc_payments.AdHocPaymentCreateView.as_view(is_create_view=True), name='adhocpayment-create'),
    path('adhoc_payments/<int:pk>/', adhoc_payments.AdHocPaymentDetailView.as_view(), name='adhocpayment-detail'),
    path('adhoc_payments/<int:pk>/delete/', adhoc_payments.AdHocPaymentDeleteView.as_view(), name='adhocpayment-delete'),

    path('stripe_charges/', stripe_charges.StripeChargeListView.as_view(), name='charge-list'),
    path('stripe_charges/charge/', stripe_charges.StripeChargeChargeView.as_view(), name='charge-charge'),
    path('stripe_charges/create/', stripe_charges.StripeChargeCreateView.as_view(is_create_view=True), name='charge-create'),
    path('stripe_charges/<int:pk>/', stripe_charges.StripeChargeDetailView.as_view(), name='charge-detail'),
    path('stripe_charges/<int:pk>/delete/', stripe_charges.StripeChargeDeleteView.as_view(), name='charge-delete'),

    path('red_flags/', red_flags.RedFlagListView.as_view(), name='redflag-list'),
    path('red_flags/create/', red_flags.RedFlagCreateView.as_view(is_create_view=True), name='redflag-create'),
    path('red_flags/<int:pk>/', red_flags.RedFlagDetailView.as_view(), name='redflag-detail'),
    path('red_flags/<int:pk>/delete/', red_flags.RedFlagDeleteView.as_view(), name='redflag-delete'),

    path('bbs/', bbs.BBSListView.as_view(), name='bbs-list'),
    path('bbs/<int:pk>/reply/', bbs.BBSReplyPostView.as_view(), name='bbs-reply'),
    path('bbs/<int:pk>/edit/', bbs.BBSEditPostView.as_view(), name='bbs-edit'),
    path('bbs/<int:pk>/delete/', bbs.BBSDeletePostView.as_view(), name='bbs-delete'),

    path('consigners/', consigners.ConsignerListView.as_view(), name='consigner-list'),
    path('consigners/create/', consigners.ConsignerCreateView.as_view(is_create_view=True), name='consigner-create'),
    path('consigners/<int:pk>/', consigners.ConsignerDetailView.as_view(), name='consigner-detail'),
    path('consigners/<int:pk>/delete/', consigners.ConsignerDeleteView.as_view(), name='consigner-delete'),

    path('consignment_payments/', consignment_payments.ConsignmentPaymentListView.as_view(), name='consignmentpayment-list'),
    path('consignment_payments/create/', consignment_payments.ConsignmentPaymentCreateView.as_view(is_create_view=True), name='consignmentpayment-create'),
    path('consignment_payments/<int:pk>/', consignment_payments.ConsignmentPaymentDetailView.as_view(), name='consignmentpayment-detail'),
    path('consignment_payments/<int:pk>/delete/', consignment_payments.ConsignmentPaymentDeleteView.as_view(), name='consignmentpayment-delete'),

    path('news/', news.NewsItemListView.as_view(), name='news-list'),
    path('news/create/', news.NewsItemCreateView.as_view(is_create_view=True), name='news-create'),
    path('news/<int:pk>/', news.NewsItemDetailView.as_view(), name='news-detail'),
    path('news/<int:pk>/delete/', news.NewsItemDeleteView.as_view(), name='news-delete'),

    path('newsletter_subscriptions/', newsletter_subscriptions.NewsletterSubscriptionListView.as_view(), name='subscription-list'),
    path('newsletter_subscriptions/<int:pk>/delete/', newsletter_subscriptions.NewsletterSubscriptionDeleteView.as_view(), name='subscription-delete'),

    path('survey_responses/', survey_responses.SurveyResponseListView.as_view(), name='surveyresponse-list'),
    path('survey_responses/<int:pk>/delete/', survey_responses.SurveyResponseDeleteView.as_view(), name='surveyresponse-delete'),

    path('site_content/', site_content.SiteContentListView.as_view(), name='sitecontent-list'),
    path('site_content/<str:page>/', site_content.SiteContentDetailView.as_view(), name='sitecontent-detail'),

    path('damage/', damage.DamageListView.as_view(), name='damage-list'),
    path('damage/unrepaired/', damage.DamageListView.as_view(unrepaired_only=True), name='damage-list-unrepaired'),
    path('damage/repaired/', damage.DamageListView.as_view(repaired_only=True), name='damage-list-repaired'),
    path('damage/create/', damage.DamageCreateView.as_view(is_create_view=True), name='damage-create'),
    path('damage/<int:pk>/', damage.DamageDetailView.as_view(), name='damage-detail'),
    path('damage/<int:pk>/delete/', damage.DamageDeleteView.as_view(), name='damage-delete'),

    path('service/', RedirectView.as_view(url='/service/due/'), name='service-list-redirect'),
    path('service/due/', service.ScheduledServiceListView.as_view(due_only=True), name='service-list-due'),
    path('service/upcoming/', service.ScheduledServiceListView.as_view(upcoming_only=True), name='service-list-upcoming'),
    path('service/history/', service.ServiceHistoryListView.as_view(history_only=True), name='service-list-history'),
    path('service/create/scheduled/', service.ScheduledServiceCreateView.as_view(is_create_view=True), name='service-create-scheduled'),
    path('service/create/incidental/', service.IncidentalServiceCreateView.as_view(is_create_view=True), name='service-create-incidental'),
    path('service/scheduled/<int:pk>/', service.ScheduledServiceDetailView.as_view(), name='service-detail-scheduled'),
    path('service/scheduled/<int:pk>/delete/', service.ScheduledServiceDeleteView.as_view(), name='service-delete-scheduled'),
    path('service/incidental/<int:pk>/delete/', service.IncidentalServiceDeleteView.as_view(), name='service-delete-incidental'),
]
