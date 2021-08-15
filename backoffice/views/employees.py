from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from users.models import Employee
from backoffice.forms import EmployeeForm


# Template generics-based CRUD views

class EmployeeViewMixin:
    model = Employee
    page_group = 'employees'


class EmployeeListView(PermissionRequiredMixin, EmployeeViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_employee',)
    template_name = 'backoffice/employee_list.html'
    search_fields = ('first_name', 'last_name', 'user__email',)


class EmployeeDetailView(EmployeeViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/employee_detail.html'
    form_class = EmployeeForm

    # def post(self, request, *args, **kwargs):
    #     result = super().post(request, *args, **kwargs)
    #     return result

    def get_success_url(self):
        return reverse('backoffice:employee-detail', kwargs={'pk': self.object.id})


class EmployeeCreateView(EmployeeViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/employee_detail.html'
    form_class = EmployeeForm

    def get_success_url(self):
        return reverse('backoffice:employee-detail', kwargs={'pk': self.object.id})


class EmployeeDeleteView(DeleteView):
    model = Employee

    def get_success_url(self):
        return reverse('backoffice:employee-list')
