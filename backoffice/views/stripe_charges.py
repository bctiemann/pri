from stripe.error import CardError
from rest_framework.views import APIView
from rest_framework.response import Response
from decimal import Decimal, DecimalException

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone

from . import ListViewMixin, AdminViewMixin
from backoffice.forms import StripeChargeForm, CardForm
from users.models import Customer
from sales.models import Charge
from sales.stripe import Stripe


# Template generics-based CRUD views

class StripeChargeViewMixin:
    model = Charge
    page_group = 'stripe_charges'
    default_sort = '-id'
    stripe = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stripe = Stripe()

    def register_stripe_card(self, charge):
        # Update card. If any data has changed since the last saved Card object, refresh the Stripe object as well.
        if charge.cc_number:
            card_data = {
                'number': charge.cc_number,
                'exp_month': charge.cc_exp_mo,
                'exp_year': charge.cc_exp_yr,
                'cvv': charge.cc_cvv,
            }
            card = charge.card
            card_changed = card and card.card_is_changed(**card_data)
            if card_changed or not card:
                card_form = CardForm(data=card_data, instance=card)
                card = card_form.save()

                try:
                    card_token = self.stripe.get_card_token(card.number, card.exp_month, card.exp_year, card.cvv)
                    stripe_customer = self.stripe.add_stripe_customer(
                        full_name=charge.full_name,
                        email=charge.email,
                        phone=charge.phone,
                    )
                    card = self.stripe.add_card_to_stripe_customer(stripe_customer, card_token, card)
                    charge.card = card
                    charge.stripe_customer = stripe_customer
                    charge.card_status = 'valid'
                except CardError as e:
                    charge.card_status = Stripe.get_error(e)
                charge.save()

            if card:
                card.name = charge.full_name
                card.address = charge.cc_address
                card.city = charge.cc_city
                card.state = charge.cc_state
                card.zip = charge.cc_zip
                card.save()


class StripeChargeListView(PermissionRequiredMixin, AdminViewMixin, StripeChargeViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_charge',)
    template_name = 'backoffice/stripe_charge/list.html'
    search_fields = ('full_name', 'email', 'phone',)


class StripeChargeDetailView(AdminViewMixin, StripeChargeViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/stripe_charge/detail.html'
    form_class = StripeChargeForm

    def form_valid(self, form):
        charge = form.save()
        self.register_stripe_card(charge)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:charge-detail', kwargs={'pk': self.object.id})


class StripeChargeCreateView(AdminViewMixin, StripeChargeViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/stripe_charge/detail.html'
    form_class = StripeChargeForm

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        customer_id = self.request.GET.get('customer_id')
        amount = self.request.GET.get('amount')
        card = self.request.GET.get('card')
        if customer_id:
            try:
                kwargs['initial']['customer'] = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                pass
        if amount:
            try:
                kwargs['initial']['amount'] = Decimal(amount)
            except DecimalException:
                pass
        kwargs['initial']['card'] = card
        return kwargs

    def form_valid(self, form):
        charge = form.save()
        self.object = charge
        if form.cleaned_data['customer'] and form.cleaned_data['card_obj']:
            charge.card = form.cleaned_data['card_obj']
            charge.stripe_customer = form.cleaned_data['customer'].stripe_customer
            charge.save()
        else:
            self.register_stripe_card(charge)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:charge-detail', kwargs={'pk': self.object.id})


class StripeChargeChargeView(AdminViewMixin, StripeChargeViewMixin, UpdateView):
    template_name = 'backoffice/stripe_charge/detail.html'
    fields = ()

    def form_invalid(self, form):
        print(form.data)
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        charge = self.object
        charge_result = self.stripe.charge_card(
            amount=charge.amount_int,
            source=charge.card.stripe_card,
            customer=charge.stripe_customer,
            capture=charge.capture,
            description=f'Charge id {charge.id}',
        )
        charge.processor_charge_id = charge_result.id
        charge.charged_at = timezone.now()
        charge.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['is_charge_view'] = True
        return context

    def get_success_url(self):
        return reverse('backoffice:charge-detail', kwargs={'pk': self.object.id})


class StripeChargeDeleteView(DeleteView):
    model = Charge

    def get_success_url(self):
        return reverse('backoffice:charge-list')
