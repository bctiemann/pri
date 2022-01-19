from django.conf import settings

from fleet.models import VehicleType, VehicleStatus

def settings_constants(request):

    context = {
        'title_bar_line_1': settings.TITLE_BAR_LINE_1,
        'title_bar_line_2': settings.TITLE_BAR_LINE_2,
        'vehicle_type': VehicleType,
        'vehicle_status': VehicleStatus,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'tinymce_api_key': settings.TINYMCE_API_KEY,
        'extend_threshold_hours': settings.EXTEND_THRESHOLD_HOURS,
        'company_name': settings.COMPANY_NAME,
        'company_phone': settings.COMPANY_PHONE,
        'stripe_publishable_key': settings.STRIPE_PUBLIC_KEY,
        'server_base_url': settings.SERVER_BASE_URL,
        'site_email': settings.SITE_EMAIL,
    }
    return context

