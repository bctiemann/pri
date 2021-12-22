from django.conf import settings

from fleet.models import VehicleType, VehicleStatus

def settings_constants(request):

    context = {
        'title_bar_line_1': settings.TITLE_BAR_LINE_1,
        'title_bar_line_2': settings.TITLE_BAR_LINE_2,
        'vehicle_type': VehicleType,
        'vehicle_status': VehicleStatus,
    }
    return context

