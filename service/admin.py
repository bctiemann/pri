from django.contrib import admin

from service.models import ServiceItem, ScheduledService, IncidentalService


class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


class ScheduledServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'service_item', 'done_at', 'done_mileage',)


class IncidentalServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'done_at', 'mileage',)


admin.site.register(ServiceItem, ServiceItemAdmin)
admin.site.register(ScheduledService, ScheduledServiceAdmin)
admin.site.register(IncidentalService, IncidentalServiceAdmin)
