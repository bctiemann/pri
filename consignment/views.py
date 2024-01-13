import calendar
import logging
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from django.shortcuts import render
from django.views.generic import TemplateView, FormView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.http import Http404, JsonResponse
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView

from users.views import LogoutView
from fleet.models import Vehicle, VehicleStatus
from sales.models import Rental
from consignment.utils import EventCalendar
from consignment.models import Consigner, ConsignmentReservation
from consignment.forms import PasswordForm, ConsignerPaymentInfoForm, ConsignmentReservationForm

logger = logging.getLogger(__name__)
auth_logger = logging.getLogger('auth')


class SidebarMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_page'] = getattr(self, 'selected_page', None)
        return context


class VehicleContextMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'slug' in kwargs:
            try:
                context['vehicle'] = Vehicle.objects.get(slug=kwargs['slug'], external_owner=self.request.user.consigner)
            except Vehicle.DoesNotExist:
                raise Http404
        return context


class LoginView(LoginView):
    template_name = 'consignment/login.html'
    home_url = reverse_lazy('consignment:home')
    next_page = reverse_lazy('consignment:home')


class LogoutView(LogoutView):
    pass


class CalendarView(SidebarMixin, VehicleContextMixin, TemplateView):
    template_name = 'consignment/calendar.html'
    selected_page = 'vehicles'


class ProceedsView(SidebarMixin, VehicleContextMixin, TemplateView):
    template_name = 'consignment/proceeds.html'
    selected_page = 'vehicles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['past_rentals'] = Rental.objects.filter(
            vehicle__in=self.request.user.consigner.vehicle_set.all(),
            # vehicle__status=VehicleStatus.READY,
            status=Rental.Status.COMPLETE,
        ).order_by('out_at')
        if 'vehicle' in context:
            context['past_rentals'] = context['past_rentals'].filter(vehicle=context['vehicle'])
        context['total_gross'] = sum([Decimal(x.gross_revenue) for x in context['past_rentals']])
        return context


class CalendarWidgetView(VehicleContextMixin, TemplateView):
    template_name = 'consignment/ajax/calendar_widget.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        try:
            month_offset = int(self.request.GET.get('month_offset'))
        except (TypeError, ValueError):
            month_offset = 0

        focus_date = now + relativedelta(months=month_offset)
        prev_date = focus_date - relativedelta(months=1)
        next_date = focus_date + relativedelta(months=1)

        consigner = self.request.user.consigner
        vehicle = context.get('vehicle')

        focus_cal = EventCalendar(year=focus_date.year, month=focus_date.month, consigner=consigner, vehicle=vehicle, firstweekday=6)
        prev_cal = EventCalendar(year=prev_date.year, month=prev_date.month, consigner=consigner, vehicle=vehicle, firstweekday=6)
        next_cal = EventCalendar(year=next_date.year, month=next_date.month, consigner=consigner, vehicle=vehicle, firstweekday=6)
        day_cssclasses = [
            'mon calendar-date this-month',
            'tue calendar-date this-month',
            'wed calendar-date this-month',
            'thu calendar-date this-month',
            'fri calendar-date this-month',
            'sat calendar-date this-month',
            'sun calendar-date this-month',
        ]
        cssclass_noday = 'calendar-date other-month'
        cssclass_month_head = 'month-head'
        focus_cal.cssclass_month_head = cssclass_month_head
        prev_cal.cssclass_month_head = cssclass_month_head
        next_cal.cssclass_month_head = cssclass_month_head
        focus_cal.cssclasses = day_cssclasses
        prev_cal.cssclasses = day_cssclasses
        next_cal.cssclasses = day_cssclasses
        focus_cal.cssclass_noday = cssclass_noday
        prev_cal.cssclass_noday = cssclass_noday
        next_cal.cssclass_noday = cssclass_noday

        context['prev_month'] = mark_safe(prev_cal.formatmonth())
        context['current_month'] = mark_safe(focus_cal.formatmonth())
        context['next_month'] = mark_safe(next_cal.formatmonth())

        return context


class ReserveView(CreateView):
    form_class = ConsignmentReservationForm
    model = ConsignmentReservation
    vehicle = None

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.consigner = self.request.user.consigner
        self.object.vehicle = self.vehicle
        self.object.save()
        return JsonResponse({'success': True})

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors})

    def post(self, request, *args, **kwargs):
        logger.debug(request.POST)
        try:
            self.vehicle = Vehicle.objects.get(slug=kwargs['slug'])
        except Vehicle.DoesNotExist:
            raise Http404
        return super().post(request, *args, **kwargs)


class ReleaseReservationView(DeleteView):
    model = ConsignmentReservation

    def get_object(self, queryset=None):
        reservation = super().get_object(queryset)
        if reservation.consigner != self.request.user.consigner:
            raise Http404
        return reservation

    def form_valid(self, form):
        self.object.delete()
        return JsonResponse({'success': True})


class PaymentHistoryView(SidebarMixin, TemplateView):
    template_name = 'consignment/payment_history.html'
    selected_page = 'payments'


class PaymentInfoView(SidebarMixin, UpdateView):
    template_name = 'consignment/payment_info.html'
    selected_page = 'payments'
    model = Consigner
    form_class = ConsignerPaymentInfoForm

    # TODO: Mask routing/account numbers in form and allow them to be cleared/re-entered but not edited directly

    def get_object(self, queryset=None):
        return self.request.user.consigner

    def get_success_url(self):
        return reverse('consignment:payment-info')


class PasswordView(SidebarMixin, FormView):
    template_name = 'consignment/password.html'
    selected_page = 'password'
    form_class = PasswordForm

    def form_valid(self, form):
        logger.debug(form.cleaned_data)
        self.request.user.set_password(form.cleaned_data['password'])
        self.request.user.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('consignment:password-done')


class PasswordDoneView(SidebarMixin, TemplateView):
    template_name = 'consignment/password_done.html'
    selected_page = 'password'


# Password recovery

class PasswordResetView(PasswordResetView):
    http_method_names = ['post']
    email_template_name = 'consignment/email/password_recovery.html'
    success_url = reverse_lazy("consignment:password_reset_complete")

    def form_valid(self, form):
        logger.info(f'{form.cleaned_data["email"]} requested a password reset')
        response = super().form_valid(form)
        return JsonResponse({'success': True})


class PasswordResetConfirmView(PasswordResetConfirmView):
    post_reset_login = True
    template_name = 'consignment/account/change_password.html'
    success_url = reverse_lazy("consignment:password_reset_complete")

    def form_valid(self, form):
        # logger.info(f'{self.user} successfully reset their password')
        return super().form_valid(form)
