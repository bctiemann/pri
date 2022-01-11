from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import ConsignerForm
from consignment.models import Consigner


# Template generics-based CRUD views

class ConsignerViewMixin:
    model = Consigner
    page_group = 'consigners'
    default_sort = '-id'


class ConsignerListView(PermissionRequiredMixin, ConsignerViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_consigner',)
    template_name = 'backoffice/consigner/list.html'
    search_fields = ('first_name', 'last_name', 'user__email',)


class ConsignerDetailView(ConsignerViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/consigner/detail.html'
    form_class = ConsignerForm

    def get_success_url(self):
        return reverse('backoffice:consigner-detail', kwargs={'pk': self.object.id})


class ConsignerCreateView(ConsignerViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/consigner/detail.html'
    form_class = ConsignerForm

    def get_success_url(self):
        return reverse('backoffice:consigner-detail', kwargs={'pk': self.object.id})


class ConsignerDeleteView(DeleteView):
    model = Consigner

    def get_success_url(self):
        return reverse('backoffice:consigner-list')
