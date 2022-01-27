from django.views.generic import TemplateView, FormView, CreateView
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.timezone import now

from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus
from sales.models import Reservation, Rental, GuidedDrive
from users.views import LoginView, LogoutView


class SidebarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_reservations'] = self.request.user.customer.basereservation_set.filter(out_at__gt=now())
        return context


class HomeView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_page'] = 'home'
        return context


class UpcomingReservationsView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/upcoming_reservations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_page'] = 'upcoming_reservations'
        return context


class PastRentalsView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/past_rentals.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_page'] = 'past_rentals'
        return context


class MakeReservationView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/make_reservation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_page'] = 'make_reservation'
        return context


class LoginView(LoginView):
    template_name = 'customer_portal/login.html'
    home_url = reverse_lazy('customer_portal:home')


class LogoutView(LogoutView):
    pass


class ConfirmReservationView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/confirm_reservation.html'

    def get_context_data(self, confirmation_code=None, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['reservation'] = Reservation.objects.get(confirmation_code=confirmation_code, customer=self.request.user.customer)
        except Reservation.DoesNotExist:
            raise Http404
        return context
