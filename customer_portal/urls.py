from django.contrib import admin
from django.urls import path, reverse_lazy
from django.conf.urls import static
from django.conf import settings
from django.urls import reverse
from django.views.generic.base import RedirectView

from fleet import views as fleet_views
from customer_portal import views


urlpatterns = [
    # path('', views.HomeView.as_view(), name='home'),
    path('', RedirectView.as_view(url=reverse_lazy('customer_portal:upcoming-reservations')), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(next_page=reverse_lazy('customer_portal:login')), name='logout'),

    path('reservations/upcoming/', views.UpcomingReservationsView.as_view(), name='upcoming-reservations'),
    path('reservations/past/', views.PastRentalsView.as_view(), name='past-rentals'),
    path('reservations/new/', views.MakeReservationView.as_view(), name='make-reservation'),
    path('reservations/<str:confirmation_code>/', views.ConfirmReservationView.as_view(), name='confirm-reservation'),

    path('account/', RedirectView.as_view(url=reverse_lazy('customer_portal:account-driver-info')), name='account-info'),
    path('account/driver/', views.AccountDriverInfoView.as_view(), name='account-driver-info'),
    path('account/insurance/', views.AccountInsuranceView.as_view(), name='account-insurance'),
    path('account/music/', views.AccountMusicView.as_view(), name='account-music'),

    path('payment/', RedirectView.as_view(url=reverse_lazy('customer_portal:payment-card-primary')), name='payment-info'),
    path('payment/primary/', views.PaymentCardPrimaryView.as_view(), name='payment-card-primary'),
    path('payment/secondary/', views.PaymentCardSecondaryView.as_view(), name='payment-card-secondary'),

    path('password/', views.PasswordView.as_view(), name='password'),
]
