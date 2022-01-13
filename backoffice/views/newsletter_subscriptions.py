from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from marketing.models import NewsletterSubscription


# Template generics-based CRUD views

class NewsletterSubscriptionViewMixin:
    model = NewsletterSubscription
    page_group = 'newsletter_subscriptions'


class NewsletterSubscriptionListView(PermissionRequiredMixin, NewsletterSubscriptionViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_newslettersubscription',)
    template_name = 'backoffice/newsletter_subscription/list.html'
    search_fields = ('full_name', 'email',)


class NewsletterSubscriptionDeleteView(DeleteView):
    model = NewsletterSubscription

    def get_success_url(self):
        return reverse('backoffice:subscription-list')
