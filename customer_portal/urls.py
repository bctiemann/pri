from django.contrib import admin
from django.urls import path, include
from django.conf.urls import static
from django.conf import settings
from django.urls import reverse
from django.views.generic.base import RedirectView

from fleet import views as fleet_views
from customer_portal import views


urlpatterns = [
    # path('', views.HomeView.as_view(), name='home'),
    path('', RedirectView.as_view(url='/customer/upcoming_reservations'), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('upcoming_reservations/', views.UpcomingReservationsView.as_view(), name='upcoming-reservations'),
    path('past_rentals/', views.PastRentalsView.as_view(), name='past-rentals'),
    path('make_reservation/', views.MakeReservationView.as_view(), name='make-reservation'),
    path('confirm_reservation/<str:confirmation_code>/', views.ConfirmReservationView.as_view(), name='confirm-reservation'),
]
