from prettyjson import PrettyJSONWidget

from django.contrib import admin
from django.db.models import JSONField

from fleet.models import Vehicle, VehicleMarketing, VehiclePicture


class VehiclePictureInline(admin.TabularInline):
    model = VehiclePicture
    fk_name = 'vehicle'


class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year',)
    inlines = (VehiclePictureInline,)


class VehicleMarketingAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'year', 'status',)
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }

admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(VehicleMarketing, VehicleMarketingAdmin)
