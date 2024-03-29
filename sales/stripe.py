import stripe
import logging
from typing import Optional

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

    def add_stripe_customer(self, full_name=None, email=None, phone=None):
        stripe_customer = stripe.Customer.create(
            description=full_name,
            name=full_name,
            email=email,
            phone=phone,
        )
        return stripe_customer.id

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

    @staticmethod
    def add_card_to_stripe_customer(stripe_customer, card_token, card=None, is_primary=False):
        stripe_card = stripe.Customer.create_source(
            stripe_customer,
            source=card_token,
        )

        if card:
            card.stripe_card = stripe_card.id
            card.brand = stripe_card.brand
            card.last_4 = stripe_card.last4
            card.exp_month = stripe_card.exp_month
            card.exp_year = stripe_card.exp_year
            card.fingerprint = stripe_card.fingerprint
            card.is_primary = is_primary
            card.save()
        else:
            card = Card.objects.create(
                stripe_card=stripe_card.id,
                brand=stripe_card.brand,
                last_4=stripe_card.last4,
                exp_month=stripe_card.exp_month,
                exp_year=stripe_card.exp_year,
                fingerprint=stripe_card.fingerprint,
                is_primary=is_primary,
            )

        return card

    def add_card_to_customer(self, customer, card_token=None, card=None, is_primary=False, number=None):
        if not card and not card_token:
            raise Exception('Provide either a card_token or a Card instance.')

        if not card_token:
            card_token = self.get_card_token(card.number, card.exp_month, card.exp_year, card.cvv)

        if not customer.stripe_customer:
            customer.add_to_stripe()

        updated_card = self.add_card_to_stripe_customer(customer.stripe_customer, card_token, card=card, is_primary=is_primary)
        updated_card.customer = customer
        if number:
            updated_card.number = number
        updated_card.save()

    @staticmethod
    def charge_card(
        amount: int,
        source: str,
        customer: str,
        capture: bool = False,
        description: Optional[str] = None,
        currency: Optional[str] = 'usd'
    ):
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            source=source,
            customer=customer,
            description=description,
            capture=capture,
        )
        return charge

    @classmethod
    def get_error(cls, exception):
        body = exception.json_body
        err = body.get('error', {})

        logger.info("Status is: %s" % exception.http_status)
        logger.info("Type is: %s" % err.get('type'))
        logger.info("Code is: %s" % err.get('code'))
        # param is '' in this case
        logger.info("Param is: %s" % err.get('param'))
        logger.info("Message is: %s" % err.get('message'))

        if not err:
            return None
        code = err['code']
        decline_code = err.get('decline_code')
        if decline_code:
            return f'{code}/{decline_code}'
        return code
