from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import MassEmailForm, EmailImageForm
from marketing.models import EmailImage


# Template generics-based CRUD views

class MassEmailViewMixin:
    page_group = 'mass_email'
    is_plain_text = False
    is_rich_text = False
    # default_sort = '-id'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['is_plain_text'] = self.is_plain_text
        context['is_rich_text'] = self.is_rich_text
        return context


class MassEmailComposeView(MassEmailViewMixin, TemplateView):
    template_name = 'backoffice/mass_email/compose.html'
    form_class = MassEmailForm

    # def form_valid(self, form):
    #     tax_rate = form.save(commit=False)
    #     tax_rate.total_rate = form.cleaned_data['total_rate_as_percent'] / 100
    #     tax_rate.save()
    #     return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:massemail-done')


class MassEmailImageListView(MassEmailViewMixin, ListViewMixin, ListView):
    template_name = 'backoffice/mass_email/image_list.html'
    model = EmailImage


class MassEmailImageCreateView(MassEmailViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/mass_email/image_create.html'
    form_class = EmailImageForm

    def get_success_url(self):
        return reverse('backoffice:massemail-image-list')


# class RedFlagCreateView(RedFlagViewMixin, ListViewMixin, CreateView):
#     template_name = 'backoffice/red_flag/detail.html'
#     form_class = RedFlagForm
#
#     def get_success_url(self):
#         return reverse('backoffice:redflag-detail', kwargs={'pk': self.object.id})
#
#
class MassEmailImageDeleteView(DeleteView):
    model = EmailImage

    def get_success_url(self):
        return reverse('backoffice:massemail-image-list')
