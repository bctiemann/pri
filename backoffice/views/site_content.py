from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin, AdminViewMixin
from backoffice.forms import SiteContentForm
from marketing.models import SiteContent


# Template generics-based CRUD views

class SiteContentViewMixin:
    model = SiteContent
    page_group = 'site_content'


class SiteContentListView(PermissionRequiredMixin, AdminViewMixin, SiteContentViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_sitecontent',)
    template_name = 'backoffice/site_content/list.html'
    search_fields = ('page', 'content',)


class SiteContentDetailView(AdminViewMixin, SiteContentViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/site_content/detail.html'
    form_class = SiteContentForm
    pk_url_kwarg = 'page'

    def get_success_url(self):
        return reverse('backoffice:sitecontent-detail', kwargs={'page': self.object.page})
