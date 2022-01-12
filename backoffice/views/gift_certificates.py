from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import GiftCertificateForm
from sales.models import GiftCertificate


# Template generics-based CRUD views

class GiftCertificateViewMixin:
    model = GiftCertificate
    page_group = 'gift_certificates'
    default_sort = '-id'
    paginate_by = 25


class GiftCertificateListView(PermissionRequiredMixin, GiftCertificateViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_giftcertificate',)
    template_name = 'backoffice/gift_certificate/list.html'
    search_fields = ('toll_account', 'tag_number', 'vehicle',)


class GiftCertificateDetailView(GiftCertificateViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/gift_certificate/detail.html'
    form_class = GiftCertificateForm

    def get_success_url(self):
        return reverse('backoffice:giftcert-detail', kwargs={'pk': self.object.id})


class GiftCertificateCreateView(GiftCertificateViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/gift_certificate/detail.html'
    form_class = GiftCertificateForm

    def get_success_url(self):
        return reverse('backoffice:giftcert-detail', kwargs={'pk': self.object.id})


class GiftCertificateDeleteView(DeleteView):
    model = GiftCertificate

    def get_success_url(self):
        return reverse('backoffice:giftcert-list')
