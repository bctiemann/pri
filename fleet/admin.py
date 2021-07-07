from django.contrib import admin

from fleet.models import Vehicle, VehicleMarketing


class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year',)


class VehicleMarketingAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'year', 'status',)


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(VehicleMarketing, VehicleMarketingAdmin)
