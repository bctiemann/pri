import calendar
from dateutil.relativedelta import relativedelta

from django.shortcuts import render
from django.views.generic import TemplateView, FormView, CreateView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.http import Http404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView

from users.views import LogoutView
from fleet.models import Vehicle
from consignment.utils import EventCalendar
from customer_portal.forms import PasswordForm


class VehicleContextMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'slug' in kwargs:
            try:
                context['vehicle'] = Vehicle.objects.get(slug=kwargs['slug'], external_owner=self.request.user.consigner)
            except Vehicle.DoesNotExist:
                raise Http404
        return context


class VehiclePageMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_page'] = 'vehicles'
        return context


class LoginView(LoginView):
    template_name = 'consignment/login.html'
    home_url = reverse_lazy('consignment:home')
    next_page = reverse_lazy('consignment:home')


class LogoutView(LogoutView):
    pass


class CalendarView(VehicleContextMixin, VehiclePageMixin, TemplateView):
    template_name = 'consignment/calendar.html'


class ProceedsView(VehicleContextMixin, VehiclePageMixin, TemplateView):
    template_name = 'consignment/proceeds.html'


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


class PaymentsView(TemplateView):
    template_name = 'consignment/payments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_page'] = 'payments'
        return context


class PasswordView(FormView):
    template_name = 'consignment/password.html'
    selected_page = 'password'
    form_class = PasswordForm

    def form_valid(self, form):
        print(form.cleaned_data)
        self.request.user.set_password(form.cleaned_data['password'])
        self.request.user.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('consignment:password-done')


class PasswordDoneView(TemplateView):
    template_name = 'consignment/password_done.html'
    selected_page = 'password'
