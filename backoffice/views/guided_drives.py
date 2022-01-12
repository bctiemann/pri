from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import JoyRideForm, PerformanceExperienceForm
from sales.models import GuidedDrive, JoyRide, PerformanceExperience


# Template generics-based CRUD views

class GuidedDriveContextMixin:

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['event_list'] = self.get_queryset()
        context['event_type'] = self.event_type
        context['event_types'] = self.event_types
        return context


class JoyRideViewMixin:
    model = JoyRide
    page_group = 'joy_rides'
    default_sort = '-id'
    event_types = JoyRide.EventType
    event_type = JoyRide.EventType.JOY_RIDE


class PerformanceExperienceViewMixin:
    model = PerformanceExperience
    page_group = 'performance_experiences'
    default_sort = '-id'
    event_types = PerformanceExperience.EventType
    event_type = PerformanceExperience.EventType.PERFORMANCE_EXPERIENCE


class GuidedEventListView(PermissionRequiredMixin, GuidedDriveContextMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_guideddrive',)
    template_name = 'backoffice/guided_drive/list.html'
    search_fields = ('customer',)


class JoyRideListView(JoyRideViewMixin, GuidedEventListView):
    pass


class PerformanceExperienceListView(PerformanceExperienceViewMixin, GuidedEventListView):
    pass


class GuidedDriveDetailView(GuidedDriveContextMixin, ListViewMixin, UpdateView):

    def form_valid(self, form):
        event = form.save(commit=False)
        if not event.confirmation_code:
            event.confirmation_code = event.get_confirmation_code()
        event.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['event'] = self.get_object()
        context['price_data'] = self.object.get_price_data()
        return context


class JoyRideDetailView(JoyRideViewMixin, GuidedDriveDetailView):
    template_name = 'backoffice/guided_drive/detail.html'
    form_class = JoyRideForm

    def get_success_url(self):
        return reverse('backoffice:joyride-detail', kwargs={'pk': self.object.id})


class PerformanceExperienceDetailView(PerformanceExperienceViewMixin, GuidedDriveDetailView):
    template_name = 'backoffice/guided_drive/detail.html'
    form_class = PerformanceExperienceForm

    def get_success_url(self):
        return reverse('backoffice:perfexp-detail', kwargs={'pk': self.object.id})


class JoyRideCreateView(GuidedDriveContextMixin, JoyRideViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/guided_drive/detail.html'
    form_class = JoyRideForm

    def get_success_url(self):
        return reverse('backoffice:joyride-detail', kwargs={'pk': self.object.id})


class PerformanceExperienceCreateView(GuidedDriveContextMixin, PerformanceExperienceViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/guided_drive/detail.html'
    form_class = PerformanceExperienceForm

    def get_success_url(self):
        return reverse('backoffice:perfexp-detail', kwargs={'pk': self.object.id})


class JoyRideDeleteView(DeleteView):
    model = JoyRide

    def get_success_url(self):
        return reverse('backoffice:joyride-list')


class PerformanceExperienceDeleteView(DeleteView):
    model = PerformanceExperience

    def get_success_url(self):
        return reverse('backoffice:perfexp-list')
