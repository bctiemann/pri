from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from marketing.models import SurveyResponse


# Template generics-based CRUD views

class SurveyResponseViewMixin:
    model = SurveyResponse
    page_group = 'survey_results'


class SurveyResponseListView(PermissionRequiredMixin, SurveyResponseViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_surveyresponse',)
    template_name = 'backoffice/survey_response/list.html'
    search_fields = ('customer', 'email',)


class SurveyResponseDeleteView(DeleteView):
    model = SurveyResponse

    def get_success_url(self):
        return reverse('backoffice:surveyresponse-list')
