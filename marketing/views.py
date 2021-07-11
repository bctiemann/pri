from django.views.generic import TemplateView
from django.http import Http404

from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus


# This mixin allows us to include the common query for cars and bikes into every view, for the nav menu
class NavMenuMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ready_vehicles'] = VehicleMarketing.objects.filter(status=VehicleStatus.READY.value).order_by('-weighting')
        context['cars'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.CAR.value)
        context['bikes'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.BIKE.value)
        return context


class HomeView(NavMenuMixin, TemplateView):
    template_name = 'front_site/home.html'

    # Note that get_context_data calls super() which overrides the NavMenuMixin method rather than the one defined in
    # TemplateView, because NavMenuMixin takes precedence in inheritance order. NavMenuMixin.get_context_data calls
    # super() in turn which does invoke TemplateView.get_context_data to build the initial context object.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['showcase_vehicle'] = context['ready_vehicles'].order_by('?').first()
        return context


class FleetView(NavMenuMixin, TemplateView):
    template_name = 'front_site/fleet.html'

    # If this view is called with a vehicle_type param, we validate that it is an acceptable value, then pass it
    # through to the super() method. If there is no vehicle_type, it is None by default.
    def get(self, request, *args, vehicle_type=None, **kwargs):
        if vehicle_type and vehicle_type not in ['cars', 'bikes']:
            raise Http404
        return super().get(request, *args, vehicle_type=vehicle_type, **kwargs)

    def get_context_data(self, vehicle_type=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicles'] = context['ready_vehicles']
        if vehicle_type:
            context['vehicles'] = context.get(vehicle_type)
        context['vehicle_type'] = vehicle_type
        return context


class VehicleView(NavMenuMixin, TemplateView):
    template_name = 'front_site/vehicle.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['vehicle'] = VehicleMarketing.objects.get(slug=slug)
        except VehicleMarketing.DoesNotExist:
            raise Http404
        return context
