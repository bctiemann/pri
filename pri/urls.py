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
from api import views as api_views
from fleet import views as rentals_views
from marketing import views as marketing_views
from sales import views as sales_views
from users import views as users_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Django admin site (generic database backend operations, CRUD, user management, etc)
    path('spork/', admin.site.urls),

    path('sign_out/', users_views.LogoutView.as_view(next_page='home'), name='sign-out'),

    path('recovery/password_reset/',
         users_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             from_email=settings.SUPPORT_EMAIL,
             extra_email_context={
                 'site_name': settings.COMPANY_NAME
             },
         ),
         name='password_reset',
         ),
    path('recovery/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'
         ),
    path('recovery/reset/<uidb64>/<token>/',
         users_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'
         ),
    path('recovery/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'
         ),

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

    path('performance_experience/', sales_views.PerformanceExperienceView.as_view(), name='performance-experience'),

    path('newsletter/', marketing_views.NewsletterView.as_view(), name='newsletter'),
    path('newsletter/done/', marketing_views.NewsletterDoneView.as_view(), name='newsletter-done'),
    path('newsletter/confirm/', marketing_views.NewsletterConfirmView.as_view(), name='newsletter-confirm'),

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
    path('api/validate/rental/payment/', api_views.ValidateRentalPaymentView.as_view(form_type='payment'), name='validate-rental-payment'),
    path('api/validate/rental/login/', api_views.ValidateRentalPaymentView.as_view(form_type='login'), name='validate-rental-login'),
    path('api/validate/newsletter/subscribe/', api_views.ValidateNewsletterSubscriptionView.as_view(), name='validate-newsletter-subscription'),

    path('api/customers/search/', api_views.SearchCustomersView.as_view(), name='search-customers'),
    path('api/tax_rate/', api_views.TaxRateByZipView.as_view(), name='tax-rate-by-zip'),

    # Handle legacy calls from mobile app
    path('ajax_post.cfm', api_views.LegacyPostView.as_view(), name='legacy-post'),
    path('pics/PRI-<int:vehicle_picture_id>.jpg', api_views.LegacyVehiclePicView.as_view(), name='legacy-vehicle-picture'),
    path('images/<int:vehicle_id>-thumb-mobile.png', api_views.LegacyVehicleMobileThumbnailView.as_view(), name='legacy-vehicle-mobile-thumbnail'),

    # This is an example of an app's own namespaced urls.py being included in the main one at a mount point.
    # This app contains the legacy site's administrative/business UI.
    path('backoffice/', include(('backoffice.urls', 'backoffice'), namespace='backoffice')),

    path('customer/', include(('customer_portal.urls', 'customer_portal'), namespace='customer_portal')),
    path('special/', include(('consignment.urls', 'consignment'), namespace='consignment')),

    path('', include(tf_urls, 'two_factor')),
]

# This maps the MEDIA_ROOT url for local development
if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
