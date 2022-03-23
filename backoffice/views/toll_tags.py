from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin, AdminViewMixin
from backoffice.forms import TollTagForm
from fleet.models import TollTag


# Template generics-based CRUD views

class TollTagViewMixin:
    model = TollTag
    page_group = 'toll_tags'
    default_sort = '-id'


class TollTagListView(PermissionRequiredMixin, AdminViewMixin, TollTagViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_tolltag',)
    template_name = 'backoffice/toll_tag/list.html'
    search_fields = ('toll_account', 'tag_number', 'vehicle',)


class TollTagDetailView(AdminViewMixin, TollTagViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/toll_tag/detail.html'
    form_class = TollTagForm

    def get_success_url(self):
        return reverse('backoffice:tolltag-detail', kwargs={'pk': self.object.id})


class TollTagCreateView(AdminViewMixin, TollTagViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/toll_tag/detail.html'
    form_class = TollTagForm

    def get_success_url(self):
        return reverse('backoffice:tolltag-detail', kwargs={'pk': self.object.id})


class TollTagDeleteView(DeleteView):
    model = TollTag

    def get_success_url(self):
        return reverse('backoffice:tolltag-list')
