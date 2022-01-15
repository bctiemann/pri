import logging
from stripe.error import CardError

from django.conf import settings
from django.core.management.base import BaseCommand

from sales.stripe import Stripe
from users.models import Customer

logger = logging.getLogger(__name__)
stripe = Stripe()


class Command(BaseCommand):

    def handle(self, *args, **options):
        for customer in Customer.objects.all():
            if not customer.stripe_customer:
                customer.stripe_customer = stripe.add_customer(customer.full_name, customer.email, customer.phone)

            if not customer.card_1 and customer.cc_number:
                cc_number = settings.CARD_NUMBER_OVERRIDE or customer.cc_number
                try:
                    card_token = stripe.get_card_token(
                        cc_number,
                        customer.cc_exp_mo,
                        customer.cc_exp_yr,
                        customer.cc_cvv,
                    )
                    card_1 = stripe.add_card_to_customer(customer, card_token)
                    card_1.number = cc_number
                    card_1.exp_month = customer.cc_exp_mo
                    card_1.exp_year = customer.cc_exp_yr
                    card_1.cvv = customer.cc_cvv
                    card_1.save()
                    customer.card_1 = card_1
                except CardError as e:
                    print(e)

            if not customer.card_2 and customer.cc_number:
                cc2_number = settings.CARD_NUMBER_OVERRIDE or customer.cc2_number
                try:
                    card_token = stripe.get_card_token(
                        cc2_number,
                        customer.cc2_exp_mo,
                        customer.cc2_exp_yr,
                        customer.cc2_cvv,
                    )
                    card_2 = stripe.add_card_to_customer(customer, card_token)
                    card_2.number = cc2_number
                    card_2.exp_month = customer.cc_exp_mo
                    card_2.exp_year = customer.cc_exp_yr
                    card_2.cvv = customer.cc_cvv
                    card_2.save()
                    customer.card_2 = card_2
                except CardError as e:
                    print(e)

            customer.save()
