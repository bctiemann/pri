from stripe.error import CardError
from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings
from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin, AdminViewMixin
from backoffice.forms import AdHocPaymentForm, AdHocPaymentCreateForm, CardForm
from sales.models import AdHocPayment
from sales.stripe import Stripe
from sales.tasks import send_email


# Template generics-based CRUD views

class AdHocPaymentViewMixin:
    model = AdHocPayment
    page_group = 'adhoc_payments'
    default_sort = '-id'


class AdHocPaymentListView(PermissionRequiredMixin, AdminViewMixin, AdHocPaymentViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_adhocpayment',)
    template_name = 'backoffice/adhoc_payment/list.html'
    search_fields = ('item', 'full_name', 'phone',)


class AdHocPaymentDetailView(AdminViewMixin, AdHocPaymentViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/adhoc_payment/detail.html'
    form_class = AdHocPaymentForm

    def form_valid(self, form):
        stripe = Stripe()
        adhoc_payment_orig = self.get_object()
        adhoc_payment = form.save()

        # Update card. If any data has changed since the last saved Card object, refresh the Stripe object as well.
        if form.cleaned_data['cc_number'] and settings.STRIPE_ENABLED and settings.STRIPE_CUSTOMER_ENABLED:
            card_data = {
                'number': form.cleaned_data['cc_number'],
                'exp_month': form.cleaned_data['cc_exp_mo'],
                'exp_year': form.cleaned_data['cc_exp_yr'],
                'cvv': form.cleaned_data['cc_cvv'],
            }
            card_changed = adhoc_payment.card and adhoc_payment.card.card_is_changed(**card_data)
            card = adhoc_payment.card
            if card_changed or not adhoc_payment.card:
                card_form = CardForm(data=card_data, instance=adhoc_payment.card)
                card = card_form.save()

                try:
                    card_token = stripe.get_card_token(card.number, card.exp_month, card.exp_year, card.cvv)
                    stripe_customer = stripe.add_stripe_customer(
                        full_name=form.cleaned_data['full_name'],
                        email=form.cleaned_data['email'],
                        phone=form.cleaned_data['phone'],
                    )
                    card = stripe.add_card_to_stripe_customer(stripe_customer, card_token, card)
                    adhoc_payment.card = card
                    adhoc_payment.stripe_customer = stripe_customer
                    adhoc_payment.card_status = 'valid'
                except CardError as e:
                    adhoc_payment.card_status = Stripe.get_error(e)
                adhoc_payment.save()

            if card:
                card.name = adhoc_payment.full_name
                card.address = form.cleaned_data['cc_address']
                card.city = form.cleaned_data['cc_city']
                card.state = form.cleaned_data['cc_state']
                card.zip = form.cleaned_data['cc_zip']
                card.save()

        # If is_paid is changing from False to True, send adhoc_payment_complete.txt email
        if adhoc_payment.is_paid and not adhoc_payment_orig.is_paid:
            email_subject = 'Performance Rentals Substitute Payment - Processed'
            email_context = {
                'adhoc_payment': adhoc_payment,
                'company_phone': settings.COMPANY_PHONE,
                'company_email': settings.SITE_EMAIL,
            }
            send_email(
                [form.cleaned_data['email']], email_subject, email_context,
                text_template='email/adhoc_payment_complete.txt',
                html_template='email/adhoc_payment_complete.html',
                from_address=settings.SALES_EMAIL,
            )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:adhocpayment-detail', kwargs={'pk': self.object.id})


class AdHocPaymentCreateView(AdminViewMixin, AdHocPaymentViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/adhoc_payment/detail.html'
    form_class = AdHocPaymentCreateForm

    def form_valid(self, form):
        adhoc_payment = form.save()
        self.object = adhoc_payment
        email_subject = 'Performance Rentals Substitute Payment Request'
        email_context = {
            'adhoc_payment': adhoc_payment,
            'company_phone': settings.COMPANY_PHONE,
            'company_email': settings.SITE_EMAIL,
            'site_url': settings.SERVER_BASE_URL,
        }
        send_email(
            [form.cleaned_data['email']], email_subject, email_context,
            text_template='email/adhoc_payment_request.txt',
            html_template='email/adhoc_payment_request.html',
            from_address=settings.SALES_EMAIL,
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:adhocpayment-detail', kwargs={'pk': self.object.id})


class AdHocPaymentDeleteView(DeleteView):
    model = AdHocPayment

    def get_success_url(self):
        return reverse('backoffice:adhocpayment-list')
