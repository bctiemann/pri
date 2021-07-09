from django.views.generic import TemplateView

from fleet.models import Vehicle, VehicleType, VehicleStatus


class HomeView(TemplateView):
    template_name = 'front_site/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ready_vehicles = Vehicle.objects.filter(status=VehicleStatus.READY.value).order_by('-weighting')
        context['cars'] = ready_vehicles.filter(vehicle_type=VehicleType.CAR.value)
        context['bikes'] = ready_vehicles.filter(vehicle_type=VehicleType.BIKE.value)
        context['showcase_vehicle'] = ready_vehicles.order_by('?').first()
        return context
