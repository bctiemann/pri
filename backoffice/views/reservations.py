from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from sales.models import Reservation
from backoffice.forms import ReservationForm


# Template generics-based CRUD views

class ReservationViewMixin:
    model = Reservation
    page_group = 'reservations'
    default_sort = '-id'


class ReservationListView(PermissionRequiredMixin, ReservationViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_reservation',)
    template_name = 'backoffice/reservation/list.html'
    search_fields = ('customer__first_name', 'customer__last_name', 'customer__user__email', 'vehicle__make', 'confirmation_code',)


class ReservationDetailView(ReservationViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/reservation/detail.html'
    form_class = ReservationForm

    # def post(self, request, *args, **kwargs):
    #     result = super().post(request, *args, **kwargs)
    #     return result

    def get_success_url(self):
        return reverse('backoffice:reservation-detail', kwargs={'pk': self.object.id})


class ReservationCreateView(ReservationViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/reservation/detail.html'
    form_class = ReservationForm

    def form_valid(self, form):
        user = User.objects.create_user(form.cleaned_data['email'], form.cleaned_data['password'])
        self.object = form.save(commit=False)
        self.object.user = user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:reservation-detail', kwargs={'pk': self.object.id})


class ReservationDeleteView(DeleteView):
    model = Reservation

    def get_success_url(self):
        return reverse('backoffice:reservation-list')
