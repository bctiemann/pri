from django.contrib import admin

from rentals.models import Vehicle


class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year',)


admin.site.register(Vehicle, VehicleAdmin)
