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
from django.contrib.sitemaps.views import sitemap

from sitemaps import sitemaps
from api import views as api_views
from fleet import views as rentals_views
from marketing import views as marketing_views
from sales import views as sales_views
from sales.forms import (
    ReservationRentalLoginForm, ReservationRentalPaymentForm,
    JoyRideLoginForm, JoyRidePaymentForm,
    PerformanceExperienceLoginForm, PerformanceExperiencePaymentForm,
)
from users import views as users_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Django admin site (generic database backend operations, CRUD, user management, etc)
    path('spork/', admin.site.urls),

    path('sign_out/', users_views.LogoutView.as_view(next_page='home'), name='sign-out'),

    # This is an example of directly registering an app's views in the central site's urls.py. As the site grows,
    # it might be better for each app dir to have its own urls.py and for this file to include that app's urls.py
    # at a specified mount point.
    path('', marketing_views.HomeView.as_view(), name='home'),  # Class-based view version
    # path('', marketing_views.home, name='home'),  # Function-based view version

    # A single view can be resolved by multiple patterns; in this case, one has a kwarg parameter (which is referred to
    # in a template by specifying {% url "fleet" vehicle_type='cars' %}), and the other has none (leave off the
    # vehicle_type param).
    path('fleet/', marketing_views.FleetView.as_view(), name='fleet'),
    path('fleet/<str:vehicle_type>/', marketing_views.FleetView.as_view(), name='fleet'),

    path('vehicle/<str:slug>/', marketing_views.VehicleView.as_view(), name='vehicle'),

    path('vehicle/<str:slug>/reserve/', sales_views.ReserveView.as_view(), name='reserve'),
    path('vehicle/<str:slug>/reserve/form/login/', sales_views.ReserveLoginFormView.as_view(), name='reserve-login-form'),
    path('vehicle/<str:slug>/reserve/form/payment/', sales_views.ReservePaymentFormView.as_view(), name='reserve-payment-form'),
    path('vehicle/<str:slug>/reserve/price_breakdown/', sales_views.ReservePriceBreakdownView.as_view(), name='reserve-price-breakdown'),
    # No-JS flow (honeypot)
    path('vehicle/<str:slug>/reserve/login/', sales_views.ReserveView.as_view(form_class=ReservationRentalLoginForm), name='reserve-login'),
    path('vehicle/<str:slug>/reserve/payment/', sales_views.ReserveView.as_view(form_class=ReservationRentalPaymentForm), name='reserve-payment'),
    path('vehicle/<str:slug>/reserve/complete/', sales_views.ReserveHoneypotView.as_view(), name='reserve-honeypot'),

    path('performance_experience/', sales_views.PerformanceExperienceView.as_view(), name='performance-experience'),
    path('performance_experience/form/login/', sales_views.PerformanceExperienceLoginFormView.as_view(), name='performance-experience-login-form'),
    path('performance_experience/form/payment/', sales_views.PerformanceExperiencePaymentFormView.as_view(), name='performance-experience-payment-form'),
    path('performance_experience/price_breakdown/', sales_views.PerformanceExperiencePriceBreakdownView.as_view(), name='performance-experience-price-breakdown'),
    # No-JS flow (honeypot)
    path('performance_experience/login/', sales_views.PerformanceExperienceView.as_view(form_class=JoyRideLoginForm), name='performance-experience-login'),
    path('performance_experience/payment/', sales_views.PerformanceExperienceView.as_view(form_class=JoyRidePaymentForm), name='performance-experience-payment'),
    path('performance_experience/complete/', sales_views.PerformanceExperienceHoneypotView.as_view(), name='performance-experience-honeypot'),

    path('joy_ride/', sales_views.JoyRideView.as_view(), name='joy-ride'),
    path('joy_ride/form/login/', sales_views.JoyRideLoginFormView.as_view(), name='joy-ride-login-form'),
    path('joy_ride/form/payment/', sales_views.JoyRidePaymentFormView.as_view(), name='joy-ride-payment-form'),
    path('joy_ride/price_breakdown/', sales_views.JoyRidePriceBreakdownView.as_view(), name='joy-ride-price-breakdown'),
    # No-JS flow (honeypot)
    path('joy_ride/login/', sales_views.JoyRideView.as_view(form_class=JoyRideLoginForm), name='joy-ride-login'),
    path('joy_ride/payment/', sales_views.JoyRideView.as_view(form_class=JoyRidePaymentForm), name='joy-ride-payment'),
    path('joy_ride/complete/', sales_views.JoyRideHoneypotView.as_view(), name='joy-ride-honeypot'),

    path('gift_certificate/', sales_views.GiftCertificateView.as_view(), name='gift-certificate'),
    path('gift_certificate/<str:tag>/status/', sales_views.GiftCertificateStatusView.as_view(), name='gift-certificate-status'),
    path('gift_certificate/<str:tag>/pdf/', sales_views.GiftCertificatePDFView.as_view(), name='gift-certificate-pdf'),

    path('payment/<str:confirmation_code>/', sales_views.AdHocPaymentView.as_view(), name='adhoc-payment'),
    path('payment/<str:confirmation_code>/done/', sales_views.AdHocPaymentDoneView.as_view(), name='adhoc-payment-done'),

    path('newsletter/', marketing_views.NewsletterView.as_view(), name='newsletter'),
    path('newsletter/done/', marketing_views.NewsletterDoneView.as_view(), name='newsletter-done'),
    path('newsletter/confirm/<uuid:hash>/', marketing_views.NewsletterSubscribeConfirmView.as_view(), name='newsletter-subscribe-confirm'),
    path('newsletter/unsubscribe/', marketing_views.NewsletterUnsubscribeView.as_view(), name='newsletter-unsubscribe'),
    path('newsletter/unsubscribe/done/', marketing_views.NewsletterUnsubscribeDoneView.as_view(), name='newsletter-unsubscribe-done'),

    path('survey/<str:tag>/', marketing_views.SurveyView.as_view(), name='survey'),
    path('survey/<str:tag>/done/', marketing_views.SurveyDoneView.as_view(), name='survey-done'),

    path('services/', marketing_views.ServicesView.as_view(), name='services'),
    path('specials/', marketing_views.SpecialsView.as_view(), name='specials'),
    path('about/', marketing_views.AboutView.as_view(), name='about'),
    path('policies/', marketing_views.PoliciesView.as_view(), name='policies'),
    path('news/', marketing_views.NewsView.as_view(), name='news'),
    path('news/<int:year>/<int:month>/<int:day>/<str:slug>/', marketing_views.NewsView.as_view(), name='news-item'),
    path('contact/', marketing_views.ContactView.as_view(), name='contact'),

    path('terms/', marketing_views.TermsConditionsView.as_view(), name='terms-and-conditions'),
    path('privacy/', marketing_views.PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('media/', marketing_views.MediaInquiriesView.as_view(), name='media-inquiries'),

    path('api/vehicles/', api_views.GetVehiclesView.as_view(), name='get-vehicles'),
    path('api/vehicles/<int:vehicle_id>/', api_views.GetVehicleView.as_view(), name='get-vehicle'),

    path('api/validate/rental/details/', api_views.ValidateRentalDetailsView.as_view(), name='validate-rental-details'),
    path('api/validate/rental/payment/', api_views.ValidateRentalPaymentView.as_view(), name='validate-rental-payment'),
    path('api/validate/rental/login/', api_views.ValidateRentalLoginView.as_view(), name='validate-rental-login'),
    path('api/validate/rental/confirm/', api_views.ValidateRentalConfirmView.as_view(), name='validate-rental-confirm'),

    path('api/validate/joyride/details/', api_views.ValidateJoyRideDetailsView.as_view(), name='validate-joyride-details'),
    path('api/validate/joyride/payment/', api_views.ValidateJoyRidePaymentView.as_view(), name='validate-joyride-payment'),
    path('api/validate/joyride/login/', api_views.ValidateJoyRideLoginView.as_view(), name='validate-joyride-login'),

    path('api/validate/perfexp/details/', api_views.ValidatePerformanceExperienceDetailsView.as_view(), name='validate-perfexp-details'),
    path('api/validate/perfexp/payment/', api_views.ValidatePerformanceExperiencePaymentView.as_view(), name='validate-perfexp-payment'),
    path('api/validate/perfexp/login/', api_views.ValidatePerformanceExperienceLoginView.as_view(), name='validate-perfexp-login'),

    path('api/validate/newsletter/subscribe/', api_views.ValidateNewsletterSubscriptionView.as_view(), name='validate-newsletter-subscription'),
    path('api/validate/newsletter/unsubscribe/', api_views.ValidateNewsletterUnsubscriptionView.as_view(), name='validate-newsletter-unsubscribe'),

    path('api/validate/gift/payment/', api_views.ValidateGiftCertificateView.as_view(), name='validate-gift-certificate'),

    path('api/validate/adhoc/payment/', api_views.ValidateAdHocPaymentView.as_view(), name='validate-adhoc-payment'),

    # path('api/validate/survey/submit/', api_views.ValidateAdHocPaymentView.as_view(), name='validate-adhoc-payment'),

    path('api/customers/search/', api_views.SearchCustomersView.as_view(), name='search-customers'),
    path('api/tax_rate/', api_views.TaxRateByZipView.as_view(), name='tax-rate-by-zip'),
    path('api/check_schedule_conflict/', api_views.CheckScheduleConflictView.as_view(), name='check-schedule-conflict'),
    path('api/send_insurance_auth/', api_views.SendInsuranceAuthView.as_view(), name='send-insurance-auth'),
    path('api/send_welcome_email/', api_views.SendWelcomeEmailView.as_view(), name='send-welcome-email'),
    path('api/send_gift_cert_email/', api_views.SendGiftCertEmailView.as_view(), name='send-gift-cert-email'),

    # Handle legacy calls from mobile app
    path('ajax_post.cfm', api_views.LegacyPostView.as_view(), name='legacy-post'),
    path('pics/PRI-<int:vehicle_picture_id>.jpg', api_views.LegacyVehiclePicView.as_view(), name='legacy-vehicle-picture'),
    path('images/<int:vehicle_id>-thumb-mobile.png', api_views.LegacyVehicleMobileThumbnailView.as_view(), name='legacy-vehicle-mobile-thumbnail'),

    # This is an example of an app's own namespaced urls.py being included in the main one at a mount point.
    # This app contains the legacy site's administrative/business UI.
    path('backoffice/', include(('backoffice.urls', 'backoffice'), namespace='backoffice')),

    path('customer/', include(('customer_portal.urls', 'customer_portal'), namespace='customer_portal')),
    path('special/', include(('consignment.urls', 'consignment'), namespace='consignment')),

    # SEO
    # Add more patterns as you see fit. Each should have a unique name, and should be added to footer_seo.html and sitemaps.py
    path('exotic-car-rental/', marketing_views.FleetView.as_view(vehicle_type='cars'), name='seo-exotic-car-rental'),
    path('sports-car-rental/', marketing_views.FleetView.as_view(vehicle_type='cars'), name='seo-sports-car-rental'),
    path('motorcycle-rental/', marketing_views.FleetView.as_view(vehicle_type='bikes'), name='seo-motorcycle-rental'),
    path('sport-bike-rental/', marketing_views.FleetView.as_view(vehicle_type='bikes'), name='seo-sport-bike-rental'),
    path('<str:location>/exotic-car-rental/', marketing_views.FleetView.as_view(vehicle_type='cars'), name='seo-location-exotic-car-rental'),
    path('<str:slug>-rental/', marketing_views.VehicleView.as_view(), name='seo-vehicle-rental'),
    path('<str:location>/<str:slug>-rental/', marketing_views.VehicleView.as_view(), name='seo-location-vehicle-rental'),

    # Sitemap: https://return.co.de/blog/articles/sitemaps-static-views-arguments/
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    path('', include(tf_urls, 'two_factor')),
]

# This maps the MEDIA_ROOT url for local development
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
