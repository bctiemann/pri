from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.http import Http404, HttpResponseRedirect

from . import ListViewMixin
from users.models import Employee
from backoffice.forms import EmployeeForm


# Template generics-based CRUD views

class EmployeeViewMixin:
    model = Employee
    page_group = 'employees'


class EmployeeListView(EmployeeViewMixin, ListViewMixin, ListView):
    template_name = 'backoffice/employee_list.html'
    search_fields = ('first_name', 'last_name', 'user__email',)


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
