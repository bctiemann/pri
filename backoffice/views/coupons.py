from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import CouponForm
from sales.models import Coupon


# Template generics-based CRUD views

class CouponViewMixin:
    model = Coupon
    page_group = 'coupons'


class CouponListView(PermissionRequiredMixin, CouponViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_coupon',)
    template_name = 'backoffice/coupon/list.html'
    search_fields = ('code', 'amount',)


class CouponDetailView(CouponViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/coupon/detail.html'
    form_class = CouponForm

    def get_success_url(self):
        return reverse('backoffice:coupon-detail', kwargs={'pk': self.object.id})


class CouponCreateView(CouponViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/coupon/detail.html'
    form_class = CouponForm

    def get_success_url(self):
        return reverse('backoffice:coupon-detail', kwargs={'pk': self.object.id})


class CouponDeleteView(DeleteView):
    model = Coupon

    def get_success_url(self):
        return reverse('backoffice:coupon-list')
