from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q

from . import ListViewMixin
from users.models import Employee
from backoffice.forms import EmployeeForm


# Template generics-based CRUD views

class EmployeeViewMixin:
    model = Employee
    page_group = 'employees'


class EmployeeListView(EmployeeViewMixin, ListViewMixin, ListView):
    template_name = 'backoffice/employee_list.html'
    # TODO: search_fields in mixin
    # search_fields = ('first_name', 'last_name', 'user__email',)
    # Set this to allow pagination
    # paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.search_term = self.request.GET.get('query')
        if self.search_term:
            queryset = queryset.filter(
                Q(first_name__icontains=self.search_term) |
                Q(last_name__icontains=self.search_term) |
                Q(user__email__icontains=self.search_term)
            )
        queryset = queryset.order_by(self.request.GET.get('sortby', self.default_sort))
        return queryset


class EmployeeDetailView(EmployeeViewMixin, ListViewMixin, UpdateView):
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

    def get_success_url(self):
        return reverse('backoffice:employee-detail', kwargs={'pk': self.object.id})


class EmployeeCreateView(EmployeeViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/employee_detail.html'
    form_class = EmployeeForm

    def get_success_url(self):
        return reverse('backoffice:employee-detail', kwargs={'pk': self.object.id})
