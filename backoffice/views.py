from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication

from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, LogoutView, INTERNAL_RESET_SESSION_TOKEN
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q

from fleet.models import VehicleType, VehicleStatus, Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo
from backoffice.forms import (
    VehicleForm, VehicleShowcaseForm, VehicleThumbnailForm, VehicleInspectionForm, VehiclePictureForm,
    VehicleMarketingForm
)
from users.views import LoginView
from users.models import User


# Home and login/logout views

class AdminViewMixin:

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['admin_users'] = User.objects.filter(is_admin=True)
        return context


class LandingView(AdminViewMixin, TemplateView):
    template_name = 'backoffice/landing.html'


class HomeView(AdminViewMixin, TemplateView):
    template_name = 'backoffice/home.html'


class LoginView(LoginView):
    template_name = 'backoffice/login.html'
    home_url = reverse_lazy('backoffice:home')


class LogoutView(LogoutView):
    pass


# API view to track admin activity

class TrackActivityView(APIView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def post(self, request):
        request.user.admin_last_activity = parse_datetime(request.POST.get('last_activity'))
        request.user.save()
        return Response({
            'is_sleeping': request.user.is_sleeping,
        })


# Template generics-based CRUD views

class VehicleViewMixin:
    model = Vehicle
    active_only = False
    is_create_view = False

    @property
    def is_unfiltered_list_view(self):
        return not self.active_only and not self.kwargs.get('vehicle_type') and not self.is_create_view

    def get_queryset(self):
        queryset = super().get_queryset()
        if 'vehicle_type' in self.kwargs:
            queryset = queryset.filter(vehicle_type=self.kwargs['vehicle_type'])
        elif self.active_only:
            queryset = queryset.filter(status=VehicleStatus.READY.value)

        # TODO: ordering

        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['vehicle_types'] = VehicleType
        context['active_only'] = self.active_only
        context['is_unfiltered_list_view'] = self.is_unfiltered_list_view
        context['selected_vehicle_type'] = self.kwargs.get('vehicle_type')
        return context


class VehicleListView(VehicleViewMixin, ListView):
    template_name = 'backoffice/vehicle_list.html'
    search_term = None
    # Set this to allow pagination
    # paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.search_term = self.request.GET.get('query')
        if self.search_term:
            queryset = queryset.filter(
                Q(make__icontains=self.search_term) |
                Q(model__icontains=self.search_term) |
                Q(year__icontains=self.search_term)
            )
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_term'] = self.search_term
        return context


class VehicleDetailView(VehicleViewMixin, UpdateView):
    template_name = 'backoffice/vehicle_detail.html'
    form_class = VehicleForm
    marketing_form_class = VehicleMarketingForm

    def post(self, request, *args, **kwargs):
        marketing_form = VehicleMarketingForm(request.POST)
        print(marketing_form.data)
        print(marketing_form.is_valid())
        print(marketing_form.cleaned_data)
        result = super().post(request, *args, **kwargs)
        VehicleMarketing.objects.filter(vehicle_id=self.object.id).update(**marketing_form.cleaned_data)
        return result

    def get_marketing_form_class(self):
        return self.marketing_form_class

    def get_marketing_form_kwargs(self):
        kwargs = self.get_form_kwargs()
        kwargs['instance'] = kwargs['instance'].vehicle_marketing
        return kwargs

    def get_marketing_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_marketing_form_class()
        return form_class(**self.get_marketing_form_kwargs())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['marketing_form'] = self.get_marketing_form()
        return context

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.id})


class VehicleCreateView(VehicleViewMixin, CreateView):
    template_name = 'backoffice/vehicle_detail.html'
    form_class = VehicleForm

    def form_valid(self, form):
        vehicle = form.save(commit=False)
        vehicle.slug = slugify(f'{vehicle.make} {vehicle.model}')
        vehicle.save()
        vehicle_marketing = VehicleMarketing.objects.create(
            vehicle_id=vehicle.id,
            make=vehicle.make,
            model=vehicle.model,
            year=vehicle.year,
            slug=vehicle.slug,
            weighting=vehicle.weighting,
        )
        self.object = vehicle
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['is_create_view'] = True
        return context

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.id})


class VehicleShowcaseView(UpdateView):
    template_name = 'backoffice/ajax/showcase.html'
    model = VehicleMarketing
    form_class = VehicleShowcaseForm

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.vehicle_id})


class VehicleThumbnailView(UpdateView):
    template_name = 'backoffice/ajax/thumbnail.html'
    model = VehicleMarketing
    form_class = VehicleThumbnailForm

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.vehicle_id})


class VehicleInspectionView(UpdateView):
    template_name = 'backoffice/ajax/inspection.html'
    model = VehicleMarketing
    form_class = VehicleInspectionForm

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.vehicle_id})


class VehiclePicturesView(CreateView):
    template_name = 'backoffice/ajax/vehicle_pictures.html'
    model = VehiclePicture
    form_class = VehiclePictureForm
    vehicle_marketing = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.vehicle_marketing = VehicleMarketing.objects.get(pk=kwargs['pk'])
        except VehicleMarketing.DoesNotExist:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        vehicle_picture = form.save(commit=False)
        vehicle_picture.vehicle_marketing = self.vehicle_marketing
        vehicle_picture.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['vehicle_marketing'] = self.vehicle_marketing
        return context

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.vehicle_marketing.vehicle_id})


class VehicleMediaPromoteView(APIView):

    def post(self, request, vehicle_id, media_type, pk):
        response = {
            'success': True
        }
        return Response(response)
