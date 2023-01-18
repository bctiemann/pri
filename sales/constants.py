from django.conf import settings

BANK_PHONE_HELP_TEXT = '''We need the customer service contact phone number shown on the back of your card so that
we can verify the card if necessary, and to refund the security deposit after the rental is over.'''

GIFT_CERTIFICATE_TEXT = '''toward any vehicle rental from PRI's sports car{} fleet, or any service including the
PRI Performance Experience or Joy Ride."'''.format(" or bike" if settings.BIKES_ENABLED else "")
