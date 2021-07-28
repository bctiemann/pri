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

        cal = calendar.HTMLCalendar(firstweekday=6)

        focus_date = now + relativedelta(months=month_offset)
        prev_date = focus_date - relativedelta(months=1)
        next_date = focus_date + relativedelta(months=1)

        # TODO: Override HTMLCalendar to format with css classes and ConsignmentReservations

        context['prev_month'] = mark_safe(cal.formatmonth(prev_date.year, prev_date.month))
        context['current_month'] = mark_safe(cal.formatmonth(focus_date.year, focus_date.month))
        context['next_month'] = mark_safe(cal.formatmonth(next_date.year, next_date.month))

        return context
