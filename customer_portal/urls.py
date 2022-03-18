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
    path('reservations/new/', views.SelectVehicleView.as_view(), name='select-vehicle'),
    path('reservations/new/<str:slug>/', views.MakeReservationView.as_view(), name='make-reservation'),
    path('reservations/<str:confirmation_code>/', views.ConfirmReservationView.as_view(), name='confirm-reservation'),

    path('joy_ride/', RedirectView.as_view(url=reverse_lazy('customer_portal:joyride-upcoming')), name='joyride'),
    path('joy_ride/upcoming/', views.JoyRideUpcomingView.as_view(), name='joyride-upcoming'),
    path('joy_ride/past/', views.JoyRidePastView.as_view(), name='joyride-past'),
    path('joy_ride/reserve/', views.JoyRideReserveView.as_view(), name='joyride-reserve'),
    path('joy_ride/<str:confirmation_code>/', views.JoyRideConfirmView.as_view(), name='joyride-confirm'),

    path('performance_experience/', RedirectView.as_view(url=reverse_lazy('customer_portal:perfexp-upcoming')), name='perfexp'),
    path('performance_experience/upcoming/', views.PerformanceExperienceUpcomingView.as_view(), name='perfexp-upcoming'),
    path('performance_experience/past/', views.PerformanceExperiencePastView.as_view(), name='perfexp-past'),
    path('performance_experience/reserve/', views.PerformanceExperienceReserveView.as_view(), name='perfexp-reserve'),
    path('performance_experience/<str:confirmation_code>/', views.PerformanceExperienceConfirmView.as_view(), name='perfexp-confirm'),

    path('account/', RedirectView.as_view(url=reverse_lazy('customer_portal:account-driver-info')), name='account-info'),
    path('account/driver/', views.AccountDriverInfoView.as_view(), name='account-driver-info'),
    path('account/insurance/', views.AccountInsuranceView.as_view(), name='account-insurance'),
    path('account/music/', views.AccountMusicView.as_view(), name='account-music'),

    path('payment/', RedirectView.as_view(url=reverse_lazy('customer_portal:payment-card-primary')), name='payment-info'),
    path('payment/primary/', views.PaymentCardPrimaryView.as_view(), name='payment-card-primary'),
    path('payment/primary/clear/', views.PaymentCardPrimaryClearView.as_view(), name='payment-card-primary-clear'),
    path('payment/secondary/', views.PaymentCardSecondaryView.as_view(), name='payment-card-secondary'),
    path('payment/secondary/clear/', views.PaymentCardSecondaryClearView.as_view(), name='payment-card-secondary-clear'),

    path('password/', views.PasswordView.as_view(), name='password'),
    path('password/done/', views.PasswordDoneView.as_view(), name='password-done'),

    path('find_us/', views.FindUsView.as_view(), name='find-us'),
]
