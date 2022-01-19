from django.views.generic import TemplateView, FormView, CreateView
from django.http import Http404

from sales.forms import ReservationRentalDetailsForm, ReservationRentalPaymentForm, ReservationRentalLoginForm
from marketing.views import NavMenuMixin
from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus


# This template is rendered with three forms: details (phase 1), payment (phase 2 for new user), and login (phase 2 for
# returning user. All three forms have different validation needs and field sets
class ReserveView(NavMenuMixin, FormView):
    template_name = 'front_site/reserve.html'
    form_class = ReservationRentalDetailsForm
    payment_form_class = ReservationRentalPaymentForm
    login_form_class = ReservationRentalLoginForm

    def get(self, request, *args, **kwargs):
        """Handle GET requests: instantiate a blank version of the form."""
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form, **kwargs):
        """If the form is invalid, render the invalid form."""
        for field in form.errors:
            form[field].field.widget.attrs.setdefault('class', '')
            form[field].field.widget.attrs['class'] += ' field-error'
        return self.render_to_response(self.get_context_data(form=form, **kwargs))

    def get_payment_form_class(self):
        return self.payment_form_class

    def get_payment_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_payment_form_class()
        return form_class(**self.get_form_kwargs())

    def get_login_form_class(self):
        return self.login_form_class

    def get_login_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_login_form_class()
        return form_class(**self.get_form_kwargs())

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # We filter() rather than get() because vehicle_marketing.slug is not unique (we may have multiple of the
        # same vehicle)
        context['vehicle'] = VehicleMarketing.objects.filter(slug=slug, status=VehicleStatus.READY).first()
        if not context['vehicle']:
            raise Http404
        context['payment_form'] = self.get_payment_form()
        context['login_form'] = self.get_login_form()
        return context


class PerformanceExperienceView(NavMenuMixin, TemplateView):
    template_name = 'front_site/performance_experience.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle_type'] = VehicleType
        return context


class JoyRideView(NavMenuMixin, TemplateView):
    template_name = 'front_site/joy_ride.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicle_type'] = VehicleType
        return context
