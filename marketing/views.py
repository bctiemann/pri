from django.views.generic import TemplateView, FormView, CreateView
from django.http import Http404

from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus
from marketing.models import NewsItem


# This mixin allows us to include the common query for cars and bikes into every view, for the nav menu
class NavMenuMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ready_vehicles'] = VehicleMarketing.objects.filter(status=VehicleStatus.READY).order_by('-weighting')
        context['cars'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.CAR)
        context['bikes'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.BIKE)
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

    def get(self, *args, **kwargs):
        print(kwargs)
        return super().get(*args, **kwargs)

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # We filter() rather than get() because vehicle_marketing.slug is not unique (we may have multiple of the
        # same vehicle)
        context['vehicle'] = VehicleMarketing.objects.filter(slug=slug, status=VehicleStatus.READY).first()
        if not context['vehicle']:
            raise Http404
        return context


class ServicesView(NavMenuMixin, TemplateView):
    template_name = 'front_site/services.html'


class SpecialsView(NavMenuMixin, TemplateView):
    template_name = 'front_site/specials.html'


class AboutView(NavMenuMixin, TemplateView):
    template_name = 'front_site/about.html'


class PoliciesView(NavMenuMixin, TemplateView):
    template_name = 'front_site/policies.html'


class NewsView(NavMenuMixin, TemplateView):
    template_name = 'front_site/news.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        if slug:
            context['news_items'] = NewsItem.objects.filter(
                slug=self.kwargs.get('slug'),
                created_at__year=self.kwargs['year'],
                created_at__month=self.kwargs['month'],
                created_at__day=self.kwargs['day'],
            )
        else:
            context['news_items'] = NewsItem.objects.all()[0:10]
        return context


class ContactView(NavMenuMixin, TemplateView):
    template_name = 'front_site/contact.html'


class TermsConditionsView(NavMenuMixin, TemplateView):
    template_name = 'front_site/terms.html'


class PrivacyPolicyView(NavMenuMixin, TemplateView):
    template_name = 'front_site/privacy.html'


class MediaInquiriesView(NavMenuMixin, TemplateView):
    template_name = 'front_site/media.html'
