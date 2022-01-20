import stripe
import logging

from django.conf import settings

from sales.models import Card

logger = logging.getLogger(__name__)


class Stripe:

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

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
                "number": number,
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvc,
            },
        )
        return token

    def add_card_to_customer(self, customer, card_token, card=None):
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
