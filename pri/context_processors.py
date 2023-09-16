from django.conf import settings

from fleet.models import VehicleType, VehicleStatus


def settings_constants(request):

    context = {
        'title_bar_line_1': settings.TITLE_BAR_LINE_1,
        'title_bar_line_2': settings.TITLE_BAR_LINE_2,
        'twitter_enabled': settings.TWITTER_ENABLED,
        'vehicle_type': VehicleType,
        'vehicle_status': VehicleStatus,
        'bikes_enabled': settings.BIKES_ENABLED,
        'recaptcha_enabled': settings.RECAPTCHA_ENABLED,
        'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'tinymce_api_key': settings.TINYMCE_API_KEY,
        'extend_threshold_hours': settings.EXTEND_THRESHOLD_HOURS,
        'company_name': settings.COMPANY_NAME,
        'company_phone': settings.COMPANY_PHONE,
        'company_address': settings.COMPANY_ADDRESS,
        'company_address_one_line': ', '.join(settings.COMPANY_ADDRESS.splitlines()),
        'stripe_publishable_key': settings.STRIPE_PUBLIC_KEY,
        'server_base_url': settings.SERVER_BASE_URL,
        'company_email': settings.SITE_EMAIL,
        'joy_ride_prices': settings.JOY_RIDE_PRICES,
        'performance_experience_prices': settings.PERFORMANCE_EXPERIENCE_PRICES,
        'survey_discount_pct': settings.SURVEY_DISCOUNT_PCT,
        'admin_enabled': settings.ADMIN_ENABLED,
    }
    return context

