from datetime import timedelta

from django.db.models.functions import Length
from django.utils import timezone

from users.models import Customer, Employee
from marketing.models import NewsletterSubscription


THREE_DAYS_AGO = timezone.now() - timedelta(days=3)


def get_all_emailable_customers():
    return Customer.objects.annotate(email_length=Length('user__email')).filter(receive_email=True, email_length__gt=6).values('user__email')


def get_all_newsletter_subscribers():
    return NewsletterSubscription.objects.filter(confirmed_at__isnull=False).values('email')


def get_best_customers():
    customers = get_all_emailable_customers()
    return customers.filter(rating__gt=6)


def get_recently_visiting_customers():
    customers = get_all_emailable_customers()
    return customers.filter(user__last_login__gte=THREE_DAYS_AGO)


def get_recently_visiting_newsletter_subscribers():
    subscribers = get_all_newsletter_subscribers()
    return subscribers.filter(confirmed_at__gte=THREE_DAYS_AGO)


def get_all_admin_users():
    return Employee.objects.all().values('user__email')


RECIPIENT_CLASS_METHOD_MAP = {
    'all_customers': get_all_emailable_customers,
    'newsletter_subs': get_all_newsletter_subscribers,
    'best_customers': get_best_customers,
    'recent_customers': get_recently_visiting_customers,
    'recent_newsletter_subs': get_recently_visiting_newsletter_subscribers,
    'admins': get_all_admin_users,
}

RECIPIENT_CLASS_LABEL_MAP = {
    'all_customers': 'Customers',
    'newsletter_subs': 'Newsletter Subs',
    'best_customers': 'Best Customers',
    'recent_customers': 'Recently visiting Customers (3 day)',
    'recent_newsletter_subs': 'Recently visiting News Subs (3 day)',
    'admins': 'Test (Administrators)',
}