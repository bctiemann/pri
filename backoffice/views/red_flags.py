from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin, AdminViewMixin
from backoffice.forms import RedFlagForm
from sales.models import RedFlag


# Template generics-based CRUD views

class RedFlagViewMixin:
    model = RedFlag
    page_group = 'red_flags'
    default_sort = '-id'


class RedFlagListView(PermissionRequiredMixin, AdminViewMixin, RedFlagViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_redflag',)
    template_name = 'backoffice/red_flag/list.html'
    search_fields = ('full_name', 'email', 'home_phone', 'mobile_phone',)


class RedFlagDetailView(AdminViewMixin, RedFlagViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/red_flag/detail.html'
    form_class = RedFlagForm

    # def form_valid(self, form):
    #     tax_rate = form.save(commit=False)
    #     tax_rate.total_rate = form.cleaned_data['total_rate_as_percent'] / 100
    #     tax_rate.save()
    #     return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:redflag-detail', kwargs={'pk': self.object.id})


class RedFlagCreateView(AdminViewMixin, RedFlagViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/red_flag/detail.html'
    form_class = RedFlagForm

    def get_success_url(self):
        return reverse('backoffice:redflag-detail', kwargs={'pk': self.object.id})


class RedFlagDeleteView(DeleteView):
    model = RedFlag

    def get_success_url(self):
        return reverse('backoffice:redflag-list')
