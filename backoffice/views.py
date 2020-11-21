from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from rentals.models import Vehicle


class HomeView(TemplateView):
    template_name = 'backoffice/home.html'


class VehicleListView(ListView):
    model = Vehicle
    template_name = 'backoffice/vehicle_list.html'
