from django.views.generic import TemplateView, FormView, CreateView, UpdateView
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now

from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus
from sales.models import BaseReservation, Reservation, Rental, GuidedDrive
from users.views import LoginView, LogoutView
from customer_portal.forms import PasswordForm, ReservationCustomerInfoForm


class SidebarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_reservations'] = self.request.user.customer.basereservation_set.filter(out_at__gt=now())
        context['upcoming_joy_rides'] = self.request.user.customer.joyride_set.filter(requested_date__gt=now())
        context['upcoming_performance_experiences'] = self.request.user.customer.performanceexperience_set.filter(requested_date__gt=now())
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


# Reservations/Rentals

class UpcomingReservationsView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/reservations/upcoming.html'
    selected_page = 'reservations'


class PastRentalsView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/reservations/past.html'
    selected_page = 'reservations'


class SelectVehicleView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/reservations/select_vehicle.html'
    selected_page = 'reservations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ready_vehicles'] = VehicleMarketing.objects.filter(status=VehicleStatus.READY).order_by('-weighting')
        context['cars'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.CAR)
        context['bikes'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.BIKE)
        return context


class MakeReservationView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/reservations/new.html'
    selected_page = 'reservations'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle'] = VehicleMarketing.objects.get(slug=self.kwargs['slug'])
        return context


class ConfirmReservationView(SidebarMixin, UpdateView):
    template_name = 'customer_portal/reservations/confirm.html'
    selected_page = 'reservations'
    model = BaseReservation
    form_class = ReservationCustomerInfoForm

    def get_object(self, queryset=None):
        try:
            return BaseReservation.objects.get(confirmation_code=self.kwargs['confirmation_code'], customer=self.request.user.customer)
        except BaseReservation.DoesNotExist:
            raise Http404

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object.customer, 'reservation': self.object})
        return kwargs

    def get_success_url(self):
        return reverse('customer_portal:confirm-reservation', kwargs={'confirmation_code': self.kwargs['confirmation_code']})

    # def get_context_data(self, confirmation_code=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     try:
    #         context['reservation'] = BaseReservation.objects.get(confirmation_code=confirmation_code, customer=self.request.user.customer)
    #     except Reservation.DoesNotExist:
    #         raise Http404
    #     return context


# Joy Ride

class JoyRideUpcomingView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/joy_ride/upcoming.html'
    selected_page = 'joy_ride'


class JoyRidePastView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/joy_ride/past.html'
    selected_page = 'joy_ride'


class JoyRideReserveView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/joy_ride/reserve.html'
    selected_page = 'joy_ride'


# Performance Experience

class PerformanceExperienceUpcomingView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/performance_experience/upcoming.html'
    selected_page = 'performance_experience'


class PerformanceExperiencePastView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/performance_experience/past.html'
    selected_page = 'performance_experience'


class PerformanceExperienceReserveView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/performance_experience/reserve.html'
    selected_page = 'performance_experience'


# Account Info

class AccountInfoView(SidebarMixin, FormView):
    template_name = 'customer_portal/account/base.html'
    selected_page = 'account_info'
    form_class = PasswordForm


class AccountDriverInfoView(SidebarMixin, FormView):
    template_name = 'customer_portal/account/driver_info.html'
    selected_page = 'account_info'
    form_class = PasswordForm


class AccountInsuranceView(SidebarMixin, FormView):
    template_name = 'customer_portal/account/insurance.html'
    selected_page = 'account_info'
    form_class = PasswordForm


class AccountMusicView(SidebarMixin, FormView):
    template_name = 'customer_portal/account/music.html'
    selected_page = 'account_info'
    form_class = PasswordForm


# Payment Methods

class PaymentInfoView(SidebarMixin, FormView):
    template_name = 'customer_portal/payment/base.html'
    selected_page = 'payment_info'
    form_class = PasswordForm


class PaymentCardPrimaryView(SidebarMixin, FormView):
    template_name = 'customer_portal/payment/card_primary.html'
    selected_page = 'payment_info'
    form_class = PasswordForm


class PaymentCardSecondaryView(SidebarMixin, FormView):
    template_name = 'customer_portal/payment/card_secondary.html'
    selected_page = 'payment_info'
    form_class = PasswordForm


# Other pages/functions

class PasswordView(SidebarMixin, FormView):
    template_name = 'customer_portal/password.html'
    selected_page = 'password'
    form_class = PasswordForm


class FindUsView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/find_us.html'
    selected_page = 'find_us'
