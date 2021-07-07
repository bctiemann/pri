from django.contrib import admin

from fleet.models import VehicleMarketing


class VehicleMarketingAdmin(admin.ModelAdmin):
    list_display = ('id',)


admin.site.register(VehicleMarketing, VehicleMarketingAdmin)
