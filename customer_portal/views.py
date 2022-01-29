from django.views.generic import TemplateView, FormView, CreateView
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.timezone import now

from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus
from sales.models import BaseReservation, Reservation, Rental, GuidedDrive
from users.views import LoginView, LogoutView
from customer_portal.forms import PasswordForm


class SidebarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_reservations'] = self.request.user.customer.basereservation_set.filter(out_at__gt=now())
        context['selected_page'] = getattr(self, 'selected_page', None)
        return context


class LoginView(LoginView):
    template_name = 'customer_portal/login.html'
    home_url = reverse_lazy('customer_portal:home')


class LogoutView(LogoutView):
    pass


# class HomeView(SidebarMixin, TemplateView):
#     template_name = 'customer_portal/reservations/upcoming.html'
#     selected_page = 'home'


class UpcomingReservationsView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/reservations/upcoming.html'
    selected_page = 'reservations'


class PastRentalsView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/reservations/past.html'
    selected_page = 'reservations'


class MakeReservationView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/reservations/new.html'
    selected_page = 'reservations'


class ConfirmReservationView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/confirm_reservation.html'
    selected_page = 'reservations'

    def get_context_data(self, confirmation_code=None, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['reservation'] = BaseReservation.objects.get(confirmation_code=confirmation_code, customer=self.request.user.customer)
        except Reservation.DoesNotExist:
            raise Http404
        return context


class AccountInfoView(SidebarMixin, FormView):
    template_name = 'customer_portal/account_info.html'
    selected_page = 'account_info'
    form_class = PasswordForm


class PaymentInfoView(SidebarMixin, FormView):
    template_name = 'customer_portal/payment_info.html'
    selected_page = 'payment_info'
    form_class = PasswordForm


class PasswordView(SidebarMixin, FormView):
    template_name = 'customer_portal/password.html'
    selected_page = 'password'
    form_class = PasswordForm
