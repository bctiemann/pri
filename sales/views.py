from django.views.generic import TemplateView, FormView, CreateView

from sales.forms import ReservationRentalDetailsForm, ReservationRentalPaymentForm
from marketing.views import NavMenuMixin
from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus


class ReserveView(NavMenuMixin, FormView):
    template_name = 'front_site/reserve.html'
    form_class = ReservationRentalDetailsForm
    payment_form_class = ReservationRentalPaymentForm

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
        """Return the form class to use."""
        return self.payment_form_class

    def get_payment_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_payment_form_class()
        return form_class(**self.get_form_kwargs())

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['vehicle'] = VehicleMarketing.objects.get(slug=slug, status=VehicleStatus.READY)
        except VehicleMarketing.DoesNotExist:
            raise Http404
        context['payment_form'] = self.get_payment_form()
        return context
