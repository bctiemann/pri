from django.contrib import admin

from fleet.models import VehicleMarketing


class VehicleMarketingAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'year', 'status',)


admin.site.register(VehicleMarketing, VehicleMarketingAdmin)
