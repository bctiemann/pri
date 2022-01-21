import stripe
import logging

from django.conf import settings
from django.utils import timezone

from sales.models import Card

logger = logging.getLogger(__name__)


class Stripe:

    current_year = None

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.current_year = timezone.now().year

    def get_future_year(self, year):
        if settings.CARD_NUMBER_OVERRIDE and int(year) <= self.current_year:
            return self.current_year + 5
        return year

    def add_customer(self, full_name=None, email=None, phone=None):
        customer = stripe.Customer.create(
            description=full_name,
            name=full_name,
            email=email,
            phone=phone,
        )
        return customer.id

    def get_card_token(self, number, exp_month, exp_year, cvc):
        token = stripe.Token.create(
            card={
                "number": settings.CARD_NUMBER_OVERRIDE or number,
                "exp_month": exp_month,
                "exp_year": self.get_future_year(exp_year),
                "cvc": cvc,
            },
        )
        return token

    def add_card_to_customer(self, customer, card_token=None, card=None):
        if not card and not card_token:
            raise Exception('Provide either a card_token or a Card instance.')

        if not card_token:
            card_token = self.get_card_token(card.number, card.exp_month, card.exp_year, card.cvv)

        if not customer.stripe_customer:
            customer.add_to_stripe()

        try:
            stripe_card = stripe.Customer.create_source(
                customer.stripe_customer,
                source=card_token,
                # source='tok_chargeCustomerFail',
            )
        except (stripe.error.CardError, stripe.error.InvalidRequestError) as e:
            body = e.json_body
            err = body.get('error', {})

            logger.info("Status is: %s" % e.http_status)
            logger.info("Type is: %s" % err.get('type'))
            logger.info("Code is: %s" % err.get('code'))
            # param is '' in this case
            logger.info("Param is: %s" % err.get('param'))
            logger.info("Message is: %s" % err.get('message'))

            raise e

        if card:
            card.stripe_card = stripe_card.id
            card.brand = stripe_card.brand
            card.last_4 = stripe_card.last4
            card.exp_month = stripe_card.exp_month
            card.exp_year = stripe_card.exp_year
            card.fingerprint = stripe_card.fingerprint
            card.save()
        else:
            card = Card.objects.create(
                stripe_card=stripe_card.id,
                customer=customer,
                brand=stripe_card.brand,
                last_4=stripe_card.last4,
                exp_month=stripe_card.exp_month,
                exp_year=stripe_card.exp_year,
                fingerprint=stripe_card.fingerprint,
            )
