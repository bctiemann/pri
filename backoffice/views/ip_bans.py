from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin, AdminViewMixin
from backoffice.forms import IPBanForm
from sales.models import IPBan


# Template generics-based CRUD views

class IPBanViewMixin:
    model = IPBan
    page_group = 'ip_bans'
    default_sort = '-id'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['global_kill_switch'] = self.model.global_kill_switch
        return context


class IPBanListView(PermissionRequiredMixin, AdminViewMixin, IPBanViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_ipban',)
    template_name = 'backoffice/ip_ban/list.html'
    search_fields = ('ip_address',)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(id__in=self.model.global_ban_objects.values('id'))


class IPBanDetailView(AdminViewMixin, IPBanViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/ip_ban/detail.html'
    form_class = IPBanForm

    def get_success_url(self):
        return reverse('backoffice:ipban-detail', kwargs={'pk': self.object.id})


class IPBanCreateView(AdminViewMixin, IPBanViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/ip_ban/detail.html'
    form_class = IPBanForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:ipban-detail', kwargs={'pk': self.object.id})


class IPBanDeleteView(DeleteView):
    model = IPBan

    def get_success_url(self):
        return reverse('backoffice:ipban-list')


class IPBanKillSwitchToggleView(CreateView):
    model = IPBan
    fields = ()

    def form_valid(self, form):
        IPBan.toggle_global_kill_switch()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:ipban-list')
