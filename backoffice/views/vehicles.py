from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.http import Http404, HttpResponseRedirect

from . import ListViewMixin
from fleet.models import VehicleType, VehicleStatus, Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo
from backoffice.forms import (
    VehicleForm, VehicleShowcaseForm, VehicleThumbnailForm, VehicleInspectionForm, VehicleMobileThumbForm,
    VehiclePictureForm, VehicleVideoForm, VehicleMarketingForm
)


# Template generics-based CRUD views

class VehicleViewMixin:
    model = Vehicle
    page_group = 'vehicles'
    active_only = False

    @property
    def is_unfiltered_list_view(self):
        return not self.active_only and not self.kwargs.get('vehicle_type') and super().is_unfiltered_list_view

    def get_queryset(self):
        queryset = super().get_queryset()
        if 'vehicle_type' in self.kwargs:
            queryset = queryset.filter(vehicle_type=self.kwargs['vehicle_type'])
        elif self.active_only:
            queryset = queryset.filter(status=VehicleStatus.READY.value)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['vehicle_types'] = VehicleType
        context['active_only'] = self.active_only
        context['selected_vehicle_type'] = self.kwargs.get('vehicle_type')
        return context


class VehicleListView(VehicleViewMixin, ListViewMixin, ListView):
    template_name = 'backoffice/vehicle/list.html'
    search_fields = ('make', 'model', 'year',)
    # Set this to allow pagination
    # paginate_by = 10


class VehicleDetailView(VehicleViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/vehicle/detail.html'
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


class VehicleCreateView(VehicleViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/vehicle/detail.html'
    form_class = VehicleForm

    def form_valid(self, form):
        vehicle = form.save(commit=False)
        vehicle.slug = vehicle.get_slug()
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

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.id})


# Image AJAX subviews for vehicle assets

class VehicleShowcaseView(UpdateView):
    template_name = 'backoffice/ajax/showcase.html'
    model = VehicleMarketing
    form_class = VehicleShowcaseForm

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.id})


class VehicleThumbnailView(UpdateView):
    template_name = 'backoffice/ajax/thumbnail.html'
    model = VehicleMarketing
    form_class = VehicleThumbnailForm

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.id})


class VehicleInspectionView(UpdateView):
    template_name = 'backoffice/ajax/inspection.html'
    model = VehicleMarketing
    form_class = VehicleInspectionForm

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.id})


class VehicleMobileThumbView(UpdateView):
    template_name = 'backoffice/ajax/mobile_thumb.html'
    model = VehicleMarketing
    form_class = VehicleMobileThumbForm

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.object.id})


class VehiclePicturesView(CreateView):
    template_name = 'backoffice/ajax/vehicle_pictures.html'
    model = VehiclePicture
    form_class = VehiclePictureForm
    vehicle_marketing = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.vehicle_marketing = VehicleMarketing.objects.get(id=kwargs['pk'])
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
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.vehicle_marketing.id})


class VehicleVideosView(CreateView):
    template_name = 'backoffice/ajax/vehicle_videos.html'
    model = VehicleVideo
    form_class = VehicleVideoForm
    vehicle_marketing = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.vehicle_marketing = VehicleMarketing.objects.get(id=kwargs['pk'])
        except VehicleMarketing.DoesNotExist:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        vehicle_video = form.save(commit=False)
        vehicle_video.vehicle_marketing = self.vehicle_marketing
        vehicle_video.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['vehicle_marketing'] = self.vehicle_marketing
        return context

    def get_success_url(self):
        return reverse('backoffice:vehicle-detail', kwargs={'pk': self.vehicle_marketing.id})


class VehicleMediaPromoteView(APIView):

    def post(self, request, vehicle_id, media_type, pk):
        try:
            vehicle = VehicleMarketing.objects.get(pk=vehicle_id)
        except VehicleMarketing.DoesNotExist:
            raise Http404
        if media_type == 'picture':
            try:
                vehicle_picture = VehiclePicture.objects.get(pk=pk, vehicle_marketing=vehicle)
            except VehiclePicture.DoesNotExist:
                raise Http404
            vehicle.pics.all().update(is_first=False)
            vehicle_picture.is_first = True
            vehicle_picture.save()
        elif media_type == 'video':
            try:
                vehicle_video = VehicleVideo.objects.get(pk=pk, vehicle_marketing=vehicle)
            except VehicleVideo.DoesNotExist:
                raise Http404
            vehicle.vids.all().update(is_first=False)
            vehicle_video.is_first = True
            vehicle_video.save()
        response = {
            'success': True
        }
        return Response(response)


class VehicleMediaDeleteView(APIView):

    def post(self, request, vehicle_id, media_type, pk):
        try:
            vehicle = VehicleMarketing.objects.get(pk=vehicle_id)
        except VehicleMarketing.DoesNotExist:
            raise Http404
        if media_type == 'picture':
            try:
                vehicle_picture = VehiclePicture.objects.get(pk=pk, vehicle_marketing=vehicle)
            except VehiclePicture.DoesNotExist:
                raise Http404
            vehicle_picture.delete()
        elif media_type == 'video':
            try:
                vehicle_video = VehicleVideo.objects.get(pk=pk, vehicle_marketing=vehicle)
            except VehicleVideo.DoesNotExist:
                raise Http404
            vehicle_video.delete()

        # TODO: delete files from disk

        response = {
            'success': True
        }
        return Response(response)
