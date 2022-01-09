from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from users.models import User, Customer, generate_password
from backoffice.forms import CustomerForm, CloneCustomerForm


# Template generics-based CRUD views

class CustomerViewMixin:
    model = Customer
    page_group = 'customers'
    default_sort = '-id'
    paginate_by = 25


class CustomerListView(PermissionRequiredMixin, CustomerViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_customer',)
    template_name = 'backoffice/customer/list.html'
    search_fields = ('first_name', 'last_name', 'user__email',)


class CustomerDetailView(CustomerViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/customer/detail.html'
    form_class = CustomerForm

    # def post(self, request, *args, **kwargs):
    #     result = super().post(request, *args, **kwargs)
    #     return result

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['clone_form'] = CloneCustomerForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('backoffice:customer-detail', kwargs={'pk': self.object.id})


class CustomerCreateView(CustomerViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/customer/detail.html'
    form_class = CustomerForm

    # def form_valid(self, form):
    #     user = User.objects.create_user(form.cleaned_data['email'], form.cleaned_data['password'])
    #     self.object = form.save(commit=False)
    #     self.object.user = user
    #     self.object.save()
    #     return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:customer-detail', kwargs={'pk': self.object.id})


class CustomerDeleteView(DeleteView):
    model = Customer

    def get_success_url(self):
        return reverse('backoffice:customer-list')


class CustomerCloneView(PermissionRequiredMixin, APIView):
    permission_required = ('users.edit_customer',)

    def post(self, request, pk=None):
        form = CloneCustomerForm(request.POST)
        if not form.is_valid():
            return Response({'success': False, 'errors': form.errors})

        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            raise Http404

        password = generate_password()
        user = User.objects.create_user(email=form.cleaned_data['clone_email'], password=password)

        new_customer = customer
        new_customer.id = None
        new_customer.first_name = form.cleaned_data['clone_first_name']
        new_customer.last_name = form.cleaned_data['clone_last_name']
        if not form.cleaned_data['clone_duplicate_license']:
            new_customer.license_number = ''
        new_customer.user = user
        new_customer.save()

        return Response({
            'success': True,
            'customer_id': new_customer.id,
            'email': user.email,
            'password': password,
        })

