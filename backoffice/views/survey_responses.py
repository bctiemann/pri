from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.db.models import Avg, Count
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin, AdminViewMixin
from marketing.models import SurveyResponse


# Template generics-based CRUD views

class SurveyResponseViewMixin:
    model = SurveyResponse
    page_group = 'survey_results'


class SurveyResponseListView(PermissionRequiredMixin, AdminViewMixin, SurveyResponseViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_surveyresponse',)
    template_name = 'backoffice/survey_response/list.html'
    search_fields = ('customer', 'email',)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        averages = SurveyResponse.objects.all().aggregate(
            general_rating=Avg('general_rating'),
            rental_frequency=Avg('rental_frequency'),
            vehicle_rating=Avg('vehicle_rating'),
            would_recommend=Avg('would_recommend'),
            pricing=Avg('pricing'),
            email_frequency=Avg('email_frequency'),
        )
        context['averages'] = averages
        context['average_labels'] = {
            'general_rating': getattr(SurveyResponse.GeneralRating, f'RATING_{int(averages["general_rating"])}'),
            'rental_frequency': getattr(SurveyResponse.RentalFrequency, f'FREQUENCY_{int(averages["rental_frequency"])}'),
            'vehicle_rating': getattr(SurveyResponse.VehicleRating, f'RATING_{int(averages["vehicle_rating"])}'),
            'would_recommend': getattr(SurveyResponse.Recommendation, f'RECOMMEND_{int(averages["would_recommend"])}'),
            'pricing': getattr(SurveyResponse.Pricing, f'PRICING_{int(averages["pricing"])}'),
            'email_frequency': getattr(SurveyResponse.EmailFrequency, f'EMAIL_{int(averages["email_frequency"])}'),
        }
        vehicle_type_map = {vt.value: vt.label for vt in SurveyResponse.VehicleTypes}
        vehicle_types = SurveyResponse.objects.all().values('vehicle_types').annotate(vehicle_type_count=Count('vehicle_types'))
        for vehicle_type in vehicle_types:
            vehicle_type['label'] = vehicle_type_map[vehicle_type['vehicle_types']]
        context['vehicle_types'] = vehicle_types
        return context


class SurveyResponseDeleteView(DeleteView):
    model = SurveyResponse

    def get_success_url(self):
        return reverse('backoffice:surveyresponse-list')
