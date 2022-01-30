from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings
from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin

from . import ListViewMixin
from backoffice.forms import GiftCertificateForm, CardForm
from sales.models import GiftCertificate
from sales.stripe import Stripe
from pri.pdf import PDFView


# Template generics-based CRUD views

class GiftCertificateViewMixin:
    model = GiftCertificate
    page_group = 'gift_certificates'
    default_sort = '-id'
    paginate_by = 25


class GiftCertificateListView(PermissionRequiredMixin, GiftCertificateViewMixin, ListViewMixin, ListView):
    # PermissionRequiredMixin allows us to specify permission_required (all must be true) for specific models
    permission_required = ('users.view_giftcertificate',)
    template_name = 'backoffice/gift_certificate/list.html'
    search_fields = ('toll_account', 'tag_number', 'vehicle',)


class GiftCertificateDetailView(GiftCertificateViewMixin, ListViewMixin, UpdateView):
    template_name = 'backoffice/gift_certificate/detail.html'
    form_class = GiftCertificateForm

    def form_valid(self, form):
        stripe = Stripe()
        gift_certificate = form.save()

        # Update primary and secondary card. If any data has changed since the last saved Card object, refresh the
        # Stripe object as well.
        if form.cleaned_data['cc_number']:
            card_data = {
                'number': form.cleaned_data['cc_number'],
                'exp_month': form.cleaned_data['cc_exp_mo'],
                'exp_year': form.cleaned_data['cc_exp_yr'],
                'cvv': form.cleaned_data['cc_cvv'],
            }
            card_changed = gift_certificate.card and gift_certificate.card.card_is_changed(**card_data)
            card = gift_certificate.card
            if card_changed or not gift_certificate.card:
                card_form = CardForm(data=card_data, instance=gift_certificate.card)
                card = card_form.save()

                card_token = stripe.get_card_token(card.number, card.exp_month, card.exp_year, card.cvv)

                stripe_customer = stripe.add_stripe_customer(
                    full_name=form.cleaned_data['cc_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                )
                card = stripe.add_card_to_stripe_customer(stripe_customer, card_token, card)
                gift_certificate.card = card
                gift_certificate.save()

            if card:
                card.name = gift_certificate.cc_name
                card.phone = form.cleaned_data['cc_phone']
                card.address = form.cleaned_data['cc_address']
                card.city = form.cleaned_data['cc_city']
                card.state = form.cleaned_data['cc_state']
                card.zip = form.cleaned_data['cc_zip']
                card.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:giftcert-detail', kwargs={'pk': self.object.id})


class GiftCertificateCreateView(GiftCertificateViewMixin, ListViewMixin, CreateView):
    template_name = 'backoffice/gift_certificate/detail.html'
    form_class = GiftCertificateForm

    def get_success_url(self):
        return reverse('backoffice:giftcert-detail', kwargs={'pk': self.object.id})


class GiftCertificateDeleteView(DeleteView):
    model = GiftCertificate

    def get_success_url(self):
        return reverse('backoffice:giftcert-list')


class GiftCertificatePDFView(PDFView):
    # model = GiftCertificate
    template_name = 'pdf/gift_certificate.html'

    # def get_success_url(self):
    #     return reverse('backoffice:giftcert-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['gift_certificate'] = GiftCertificate.objects.get(tag=self.kwargs['tag'])
        except GiftCertificate.DoesNotExist:
            raise Http404
        context['company_phone'] = settings.COMPANY_PHONE
        return context
