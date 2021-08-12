from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q

from fleet.models import VehicleType, VehicleStatus, Vehicle, VehicleMarketing, VehiclePicture, VehicleVideo
from users.models import Employee
from backoffice.forms import EmployeeForm


# Template generics-based CRUD views

class EmployeeViewMixin:
    model = Employee
    page_group = 'employees'
    active_only = False
    is_create_view = False

    @property
    def is_unfiltered_list_view(self):
        return not self.kwargs.get('pk') and not self.is_create_view

    def get_queryset(self):
        queryset = super().get_queryset()
        print(self.kwargs)
        if 'vehicle_type' in self.kwargs:
            queryset = queryset.filter(vehicle_type=self.kwargs['vehicle_type'])
        elif self.active_only:
            queryset = queryset.filter(status=VehicleStatus.READY.value)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['vehicle_types'] = VehicleType
        context['active_only'] = self.active_only
        context['is_unfiltered_list_view'] = self.is_unfiltered_list_view
        context['selected_vehicle_type'] = self.kwargs.get('vehicle_type')
        context['page_group'] = self.page_group
        return context


class EmployeeListView(EmployeeViewMixin, ListView):
    template_name = 'backoffice/employee_list.html'
    search_term = None
    default_sort = '-id'
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
        queryset = queryset.order_by(self.request.GET.get('sortby', self.default_sort))
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['search_term'] = self.search_term
        context['sortby'] = self.request.GET.get('sortby', self.default_sort)
        return context


class EmployeeDetailView(EmployeeViewMixin, UpdateView):
    template_name = 'backoffice/employee_detail.html'
    form_class = EmployeeForm

    def post(self, request, *args, **kwargs):
        # marketing_form = VehicleMarketingForm(request.POST)
        # print(marketing_form.data)
        # print(marketing_form.is_valid())
        # print(marketing_form.cleaned_data)
        result = super().post(request, *args, **kwargs)
        # VehicleMarketing.objects.filter(vehicle_id=self.object.id).update(**marketing_form.cleaned_data)
        return result

    # def get_marketing_form_class(self):
    #     return self.marketing_form_class
    #
    # def get_marketing_form_kwargs(self):
    #     kwargs = self.get_form_kwargs()
    #     kwargs['instance'] = kwargs['instance'].vehicle_marketing
    #     return kwargs
    #
    # def get_marketing_form(self, form_class=None):
    #     if form_class is None:
    #         form_class = self.get_marketing_form_class()
    #     return form_class(**self.get_marketing_form_kwargs())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # context['marketing_form'] = self.get_marketing_form()
        return context

    def get_success_url(self):
        return reverse('backoffice:employee-detail', kwargs={'pk': self.object.id})


class EmployeeCreateView(EmployeeViewMixin, CreateView):
    template_name = 'backoffice/employee_detail.html'
    form_class = EmployeeForm

    # def form_valid(self, form):
    #     vehicle = form.save(commit=False)
    #     vehicle.slug = vehicle.get_slug()
    #     vehicle.save()
    #     vehicle_marketing = VehicleMarketing.objects.create(
    #         vehicle_id=vehicle.id,
    #         make=vehicle.make,
    #         model=vehicle.model,
    #         year=vehicle.year,
    #         slug=vehicle.slug,
    #         weighting=vehicle.weighting,
    #     )
    #     self.object = vehicle
    #     return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['is_create_view'] = True
        return context

    def get_success_url(self):
        return reverse('backoffice:employee-detail', kwargs={'pk': self.object.id})
