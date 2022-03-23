import logging
from stripe.error import CardError

from django.views.generic import TemplateView, FormView, CreateView, UpdateView
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth import login

from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus
from sales.models import BaseReservation, Reservation, Rental, GuidedDrive, JoyRide, PerformanceExperience
from sales.enums import CC_ERROR_PARAM_MAP, CC2_ERROR_PARAM_MAP
from users.models import Customer, User
from users.views import LogoutView
from customer_portal.forms import (
    PasswordForm, ReservationCustomerInfoForm, ReservationNotesForm, ReservationDetailsForm,
    JoyRideDetailsForm, JoyRideNotesForm,
    PerformanceExperienceDetailsForm, PerformanceExperienceNotesForm,
    AccountDriverInfoForm, AccountInsuranceForm, AccountMusicPrefsForm,
    CustomerCardPrimaryForm, CustomerCardSecondaryForm,
)

logger = logging.getLogger(__name__)
auth_logger = logging.getLogger('auth')


class SidebarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_reservations'] = self.request.user.customer.basereservation_set.filter(out_at__gt=now())
        context['past_rentals'] = Rental.objects.filter(customer=self.request.user.customer, out_at__lt=now(), status=Rental.Status.COMPLETE)
        context['upcoming_joy_rides'] = self.request.user.customer.joyride_set.filter(requested_date__gt=now())
        context['past_joy_rides'] = self.request.user.customer.joyride_set.filter(requested_date__lt=now(), status=GuidedDrive.Status.COMPLETE)
        context['upcoming_performance_experiences'] = self.request.user.customer.performanceexperience_set.filter(requested_date__gt=now())
        context['past_performance_experiences'] = self.request.user.customer.performanceexperience_set.filter(requested_date__lt=now(), status=GuidedDrive.Status.COMPLETE)
        context['selected_page'] = getattr(self, 'selected_page', None)
        return context


class LoginView(LoginView):
    template_name = 'customer_portal/login.html'
    home_url = reverse_lazy('customer_portal:home')
    next_page = reverse_lazy('customer_portal:home')

    # form_list = (
    #     ('auth', UserLoginForm),
        # ('token', AuthenticationTokenForm),
        # ('backup', BackupTokenForm),
    # )


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


class MakeReservationView(SidebarMixin, CreateView):
    template_name = 'customer_portal/reservations/new.html'
    selected_page = 'reservations'
    model = Reservation
    form_class = ReservationDetailsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle'] = VehicleMarketing.objects.get(slug=self.kwargs['slug'])
        return context


class ConfirmReservationView(SidebarMixin, UpdateView):
    template_name = 'customer_portal/reservations/confirm.html'
    selected_page = 'reservations'
    model = BaseReservation

    def get_object(self, queryset=None):
        try:
            return BaseReservation.objects.get(confirmation_code=self.kwargs['confirmation_code'], customer=self.request.user.customer)
        except BaseReservation.DoesNotExist:
            raise Http404

    def get_form_class(self):
        if self.request.user.customer.info_is_complete:
            return ReservationNotesForm
        return ReservationCustomerInfoForm

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if not self.request.user.customer.info_is_complete and hasattr(self, 'object'):
            kwargs.update({'instance': self.object.customer, 'confirmation_code': self.object.confirmation_code})
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.customer.info_is_complete:
            reservation_form = ReservationNotesForm(instance=self.get_object(), data=form.data)
            reservation_form.save()
        return response

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


class JoyRideReserveView(SidebarMixin, CreateView):
    template_name = 'customer_portal/joy_ride/reserve.html'
    selected_page = 'joy_ride'
    model = JoyRide
    form_class = JoyRideDetailsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ready_vehicles'] = VehicleMarketing.objects.filter(status=VehicleStatus.READY).order_by('-weighting')
        context['cars'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.CAR)
        context['bikes'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.BIKE)
        return context


class JoyRideConfirmView(SidebarMixin, UpdateView):
    template_name = 'customer_portal/joy_ride/confirm.html'
    selected_page = 'joy_ride'
    model = JoyRide
    form_class = JoyRideNotesForm

    def get_object(self, queryset=None):
        try:
            return JoyRide.objects.get(confirmation_code=self.kwargs['confirmation_code'], customer=self.request.user.customer)
        except JoyRide.DoesNotExist:
            raise Http404

    def get_success_url(self):
        return reverse('customer_portal:joyride-confirm', kwargs={'confirmation_code': self.kwargs['confirmation_code']})


# Performance Experience

class PerformanceExperienceUpcomingView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/performance_experience/upcoming.html'
    selected_page = 'performance_experience'


class PerformanceExperiencePastView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/performance_experience/past.html'
    selected_page = 'performance_experience'


class PerformanceExperienceReserveView(SidebarMixin, CreateView):
    template_name = 'customer_portal/performance_experience/reserve.html'
    selected_page = 'performance_experience'
    model = PerformanceExperience
    form_class = PerformanceExperienceDetailsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ready_vehicles'] = VehicleMarketing.objects.filter(status=VehicleStatus.READY).order_by('-weighting')
        context['cars'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.CAR)
        context['bikes'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.BIKE)
        return context


class PerformanceExperienceConfirmView(SidebarMixin, UpdateView):
    template_name = 'customer_portal/performance_experience/confirm.html'
    selected_page = 'performance_experience'
    model = PerformanceExperience
    form_class = PerformanceExperienceNotesForm

    def get_object(self, queryset=None):
        try:
            return PerformanceExperience.objects.get(confirmation_code=self.kwargs['confirmation_code'], customer=self.request.user.customer)
        except PerformanceExperience.DoesNotExist:
            raise Http404

    def get_success_url(self):
        return reverse('customer_portal:perfexp-confirm', kwargs={'confirmation_code': self.kwargs['confirmation_code']})


# Account Info

class AccountInfoView(SidebarMixin, FormView):
    template_name = 'customer_portal/account/base.html'
    selected_page = 'account_info'
    form_class = PasswordForm


class AccountDriverInfoView(SidebarMixin, UpdateView):
    template_name = 'customer_portal/account/driver_info.html'
    selected_page = 'account_info'
    form_class = AccountDriverInfoForm
    model = Customer

    def get_object(self, queryset=None):
        return self.request.user.customer

    def get_success_url(self):
        return reverse('customer_portal:account-driver-info')


class AccountInsuranceView(SidebarMixin, UpdateView):
    template_name = 'customer_portal/account/insurance.html'
    selected_page = 'account_info'
    form_class = AccountInsuranceForm
    model = Customer

    def get_object(self, queryset=None):
        return self.request.user.customer

    def get_success_url(self):
        return reverse('customer_portal:account-insurance')


class AccountMusicView(SidebarMixin, UpdateView):
    template_name = 'customer_portal/account/music.html'
    selected_page = 'account_info'
    form_class = AccountMusicPrefsForm
    model = Customer

    def get_object(self, queryset=None):
        return self.request.user.customer

    def get_success_url(self):
        return reverse('customer_portal:account-music')


# Payment Methods

# class PaymentInfoView(SidebarMixin, FormView):
#     template_name = 'customer_portal/payment/base.html'
#     selected_page = 'payment_info'
#     form_class = PasswordForm


class PaymentCardPrimaryView(SidebarMixin, UpdateView):
    template_name = 'customer_portal/payment/card_primary.html'
    selected_page = 'payment_info'
    form_class = CustomerCardPrimaryForm
    model = Customer

    def get_object(self, queryset=None):
        return self.request.user.customer

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except CardError as e:
            form.add_error(CC_ERROR_PARAM_MAP.get(e.param), e.user_message)
            return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('customer_portal:payment-card-primary')


class PaymentCardPrimaryClearView(PaymentCardPrimaryView):

    def post(self, request, *args, **kwargs):
        customer = self.get_object()
        if customer.card_1:
            customer.card_1.delete()
        customer.cc_number = ''
        customer.cc_exp_mo = ''
        customer.cc_exp_yr = ''
        customer.cc_cvv = ''
        customer.cc_phone = ''
        customer.save()
        return HttpResponseRedirect(self.get_success_url())


class PaymentCardSecondaryView(SidebarMixin, UpdateView):
    template_name = 'customer_portal/payment/card_secondary.html'
    selected_page = 'payment_info'
    form_class = CustomerCardSecondaryForm
    model = Customer

    def get_object(self, queryset=None):
        return self.request.user.customer

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except CardError as e:
            form.add_error(CC2_ERROR_PARAM_MAP.get(e.param), e.user_message)
            return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('customer_portal:payment-card-secondary')


class PaymentCardSecondaryClearView(PaymentCardSecondaryView):

    def post(self, request, *args, **kwargs):
        customer = self.get_object()
        if customer.card_2:
            customer.card_2.delete()
        customer.cc2_number = ''
        customer.cc2_exp_mo = ''
        customer.cc2_exp_yr = ''
        customer.cc2_cvv = ''
        customer.cc2_phone = ''
        customer.save()
        return HttpResponseRedirect(self.get_success_url())


# Other pages/functions

class PasswordView(SidebarMixin, FormView):
    template_name = 'customer_portal/password.html'
    selected_page = 'password'
    form_class = PasswordForm

    def form_valid(self, form):
        print(form.cleaned_data)
        self.request.user.set_password(form.cleaned_data['password'])
        self.request.user.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('customer_portal:password-done')


class PasswordDoneView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/password_done.html'
    selected_page = 'password'


class FindUsView(SidebarMixin, TemplateView):
    template_name = 'customer_portal/find_us.html'
    selected_page = 'find_us'


# Password recovery

class PasswordResetView(PasswordResetView):
    email_template_name = 'customer_portal/email/password_recovery.html'
    success_url = reverse_lazy("customer_portal:password_reset_complete")

    def form_valid(self, form):
        logger.info(f'{form.cleaned_data["email"]} requested a password reset')
        response = super().form_valid(form)
        return JsonResponse({'success': True})


class PasswordResetConfirmView(PasswordResetConfirmView):
    post_reset_login = True
    template_name = 'customer_portal/account/change_password.html'
    success_url = reverse_lazy("customer_portal:password_reset_complete")

    def form_valid(self, form):
        # logger.info(f'{self.user} successfully reset their password')
        return super().form_valid(form)
