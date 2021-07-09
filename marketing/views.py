from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'front_site/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['foo'] = 'bar'
        # context['cars'] = Vehicle.objects.filter(vehicle_type=VehicleType.CAR.value)
        return context
