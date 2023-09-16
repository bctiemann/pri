import logging

from django.core.management.base import BaseCommand

from sales.stripe import Stripe
from users.models import Customer

logger = logging.getLogger(__name__)
stripe = Stripe()


class Command(BaseCommand):

    # If last activity is more than this number of days ago, clear all locally stored card information.
    DAYS_SINCE_LAST_ACTIVITY = 30

    def add_arguments(self, parser):
        parser.add_argument('--days', dest='days', default=self.DAYS_SINCE_LAST_ACTIVITY,)
        parser.add_argument('--dry_run', dest='dry_run', default=False, action='store_true',)

    def handle(self, *args, **options):
        days_threshold = options.get('days')
        dry_run = options.get('dry_run')

        for customer in Customer.objects.all():
            if customer.days_since_last_activity and customer.days_since_last_activity > days_threshold:
                if not dry_run:
                    print(customer, customer.days_since_last_activity)
                    customer.clear_cards()
