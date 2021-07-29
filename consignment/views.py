import calendar
from dateutil.relativedelta import relativedelta

from django.shortcuts import render
from django.views.generic import TemplateView, FormView, CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.http import Http404

from users.views import LoginView
from fleet.models import Vehicle
from consignment.utils import EventCalendar


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
