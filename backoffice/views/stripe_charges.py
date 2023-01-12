from rest_framework.views import APIView
from rest_framework.response import Response

from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin, AdminViewMixin
from backoffice.forms import StripeChargeForm, CardForm
from sales.models import Charge
from sales.stripe import Stripe


# Template generics-based CRUD views

class StripeChargeViewMixin:
    model = Charge
    page_group = 'stripe_charges'
    default_sort = '-id'


class StripeChargeListView(PermissionRequiredMixin, AdminViewMixin, StripeChargeViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_charge',)
    template_name = 'backoffice/stripe_charge/list.html'
    search_fields = ('full_name', 'email', 'phone',)


class StripeChargeDetailView(AdminViewMixin, StripeChargeViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/stripe_charge/detail.html'
    form_class = StripeChargeForm

    def form_valid(self, form):
        stripe = Stripe()
        charge = form.save()

        # Update primary and secondary card. If any data has changed since the last saved Card object, refresh the
        # Stripe object as well.
        if form.cleaned_data['cc_number']:
            card_data = {
                'number': form.cleaned_data['cc_number'],
                'exp_month': form.cleaned_data['cc_exp_mo'],
                'exp_year': form.cleaned_data['cc_exp_yr'],
                'cvv': form.cleaned_data['cc_cvv'],
            }
            card_changed = charge.card and charge.card.card_is_changed(**card_data)
            card = charge.card
            if card_changed or not charge.card:
                card_form = CardForm(data=card_data, instance=charge.card)
                card = card_form.save()

                card_token = stripe.get_card_token(card.number, card.exp_month, card.exp_year, card.cvv)

                stripe_customer = stripe.add_stripe_customer(
                    full_name=form.cleaned_data['full_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                )
                card = stripe.add_card_to_stripe_customer(stripe_customer, card_token, card)
                charge.card = card
                charge.save()

            if card:
                card.name = charge.full_name
                card.address = form.cleaned_data['cc_address']
                card.city = form.cleaned_data['cc_city']
                card.state = form.cleaned_data['cc_state']
                card.zip = form.cleaned_data['cc_zip']
                card.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:charge-detail', kwargs={'pk': self.object.id})


class StripeChargeCreateView(AdminViewMixin, StripeChargeViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/stripe_charge/detail.html'
    form_class = StripeChargeForm

    def get_success_url(self):
        return reverse('backoffice:charge-detail', kwargs={'pk': self.object.id})


# TODO: Prepopulate with a customer_id/card_id with link from Customer detail page
class StripeChargeChargeView(AdminViewMixin, StripeChargeViewMixin, CreateView):
    template_name = 'backoffice/stripe_charge/charge.html'
    form_class = StripeChargeForm

    def form_invalid(self, form):
        print(form.data)
        print(form.errors)
        return super().form_invalid(form)

    # TODO: actually charge card, and push to success page with link to charge in Stripe dashboard
    def form_valid(self, form):
        print(form.data)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['is_charge_view'] = True
        return context

    def get_success_url(self):
        return reverse('backoffice:charge-list')


class StripeChargeDeleteView(DeleteView):
    model = Charge

    def get_success_url(self):
        return reverse('backoffice:charge-list')
