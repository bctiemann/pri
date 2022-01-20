import logging
from stripe.error import CardError

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from sales.stripe import Stripe
from users.models import Customer
from sales.models import Card, AdHocPayment, Charge, GiftCertificate

logger = logging.getLogger(__name__)
stripe = Stripe()


class Command(BaseCommand):

    enabled = {
        'do_customers': True,
        # 'do_adhocpayments': True,
        # 'do_giftcertificates': True,
        # 'do_stripecharges': True,
    }
    current_year = None

    def add_arguments(self, parser):
        parser.add_argument('--register_stripe', dest='register_stripe', default=False, action='store_true',)
        parser.add_argument('--clear_existing', dest='clear_existing', default=False, action='store_true',)

    def get_future_year(self, year):
        if int(year) <= self.current_year:
            return self.current_year + 5
        return year

    def handle(self, *args, **options):
        register_stripe = options.get('register_stripe')
        clear_existing = options.get('clear_existing')

        self.current_year = timezone.now().year

        if clear_existing:
            Card.objects.all().delete()

        if 'do_customers' in self.enabled:
            customers = Customer.objects.all()
            customers = customers.filter(pk=123)

            for customer in customers:
                print(customer)

                if register_stripe and not customer.stripe_customer:
                    customer.stripe_customer = stripe.add_customer(customer.full_name, customer.email, customer.phone)
                    customer.save()

                if customer.cc_number:
                    if not customer.card_1:
                        customer.card_1 = Card.objects.create(
                            customer=customer,
                            number=customer.cc_number,
                            exp_year=customer.cc_exp_yr,
                            exp_month=customer.cc_exp_mo,
                            cvv=customer.cc_cvv,
                            phone=customer.cc_phone,
                            is_primary=True,
                        )
                        customer.save()
                    if register_stripe:
                        cc_number = settings.CARD_NUMBER_OVERRIDE or customer.cc_number
                        try:
                            card_token = stripe.get_card_token(
                                cc_number,
                                customer.cc_exp_mo,
                                self.get_future_year(customer.cc_exp_yr),
                                customer.cc_cvv,
                            )
                            stripe.add_card_to_customer(customer, card_token, card=customer.card_1)
                        except CardError as e:
                            print(e)

                if customer.cc2_number:
                    if not customer.card_2:
                        customer.card_2 = Card.objects.create(
                            customer=customer,
                            number=customer.cc2_number,
                            exp_year=customer.cc2_exp_yr,
                            exp_month=customer.cc2_exp_mo,
                            cvv=customer.cc2_cvv,
                            phone=customer.cc2_phone,
                            is_primary=False,
                        )
                        customer.save()
                    if register_stripe:
                        cc2_number = settings.CARD_NUMBER_OVERRIDE or customer.cc2_number
                        try:
                            card_token = stripe.get_card_token(
                                cc2_number,
                                customer.cc2_exp_mo,
                                self.get_future_year(customer.cc2_exp_yr),
                                customer.cc2_cvv,
                            )
                            stripe.add_card_to_customer(customer, card_token, card=card_2)
                        except CardError as e:
                            print(e)

        if 'do_adhocpayments' in self.enabled:
            for payment in AdHocPayment.objects.all():
                print(payment)
                if not payment.card:
                    payment.card = Card.objects.create(
                        number=payment.cc_number,
                        exp_year=payment.cc_exp_yr,
                        exp_month=payment.cc_exp_mo,
                        cvv=payment.cc_cvv,
                        is_primary=True,
                    )
                    payment.save()

        if 'do_giftcertificates' in self.enabled:
            for gift_cert in GiftCertificate.objects.all():
                print(gift_cert)
                if not gift_cert.card:
                    gift_cert.card = Card.objects.create(
                        number=gift_cert.cc_number,
                        exp_year=gift_cert.cc_exp_yr,
                        exp_month=gift_cert.cc_exp_mo,
                        cvv=gift_cert.cc_cvv,
                        is_primary=True,
                    )
                    gift_cert.save()

        if 'do_stripecharges' in self.enabled:
            for charge in Charge.objects.all():
                print(charge)
                if not charge.card:
                    charge.card = Card.objects.create(
                        number=charge.cc_number,
                        exp_year=charge.cc_exp_yr,
                        exp_month=charge.cc_exp_mo,
                        cvv=charge.cc_cvv,
                        is_primary=True,
                    )
                    charge.save()
