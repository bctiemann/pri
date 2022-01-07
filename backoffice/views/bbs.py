from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta

from django.shortcuts import render, reverse
from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import CouponForm
from backoffice.models import BBSPost
from backoffice.views import HomeView, HomeEditPostView, HomeReplyPostView, HomeDeletePostView


# Template generics-based CRUD views

class BBSViewMixin:
    model = BBSPost
    page_group = 'bbs'


class BBSListView(BBSViewMixin, ListViewMixin, HomeView):
    template_name = 'backoffice/bbs/list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        six_hours_ago = timezone.now() - timedelta(seconds=3600 * 6)
        context['bbs_posts'] = BBSPost.objects.all()
        context['bbs_posts_new'] = BBSPost.objects.filter(created_at__gte=six_hours_ago)
        context['short_bbs'] = False
        return context


# class BBSAddPostView(HomeAddPostView):
#     template_name = 'backoffice/bbs/list.html'
#
#     def get_success_url(self):
#         return reverse('backoffice:bbs-list')


class BBSEditPostView(BBSViewMixin, HomeEditPostView):
    template_name = 'backoffice/bbs/edit.html'

    def get_object(self, queryset=None):
        queryset = self.get_queryset().filter(author=self.request.user)
        return super().get_object(queryset)

    def get_success_url(self):
        return reverse('backoffice:bbs-list')


class BBSReplyPostView(BBSViewMixin, HomeReplyPostView):
    template_name = 'backoffice/bbs/reply.html'

    def get_success_url(self):
        return reverse('backoffice:bbs-list')


class BBSDeletePostView(BBSViewMixin, HomeDeletePostView):
    template_name = 'backoffice/bbs/delete.html'

    def get_success_url(self):
        return reverse('backoffice:bbs-list')
