from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import NewsItemForm
from marketing.models import NewsItem


# Template generics-based CRUD views

class NewsItemViewMixin:
    model = NewsItem
    page_group = 'news'
    default_sort = '-created_at'


class NewsItemListView(PermissionRequiredMixin, NewsItemViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_newsitem',)
    template_name = 'backoffice/news/list.html'
    search_fields = ('subject', 'body',)


class NewsItemDetailView(NewsItemViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/news/detail.html'
    form_class = NewsItemForm

    def get_success_url(self):
        return reverse('backoffice:news-detail', kwargs={'pk': self.object.id})


class NewsItemCreateView(NewsItemViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/news/detail.html'
    form_class = NewsItemForm

    def get_success_url(self):
        return reverse('backoffice:news-detail', kwargs={'pk': self.object.id})


class NewsItemDeleteView(DeleteView):
    model = NewsItem

    def get_success_url(self):
        return reverse('backoffice:news-list')
