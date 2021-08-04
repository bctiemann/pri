from prettyjson import PrettyJSONWidget

from django.contrib import admin
from django.db.models import JSONField

from fleet.models import Vehicle, VehicleMarketing, VehiclePicture


class VehiclePictureInline(admin.TabularInline):
    model = VehiclePicture
    fk_name = 'vehicle_marketing'


class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year',)


class VehicleMarketingAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'make', 'model', 'year', 'status',)
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }
    inlines = (VehiclePictureInline,)
    prepopulated_fields = {"slug": ("model",)}
    fieldsets = (
        (None, {
            'fields': ('vehicle_id',)
        }),
        ('Redundant with Vehicle - update corresponding record manually', {
            'fields': ('make', 'model', 'year', 'slug', 'vehicle_type', 'status', 'weighting',)
        }),
        ('Images', {
            'fields': (
                'showcase_image', 'showcase_width', 'showcase_height',
                'thumbnail_image', 'thumbnail_width', 'thumbnail_height',
                'mobile_thumbnail_image', 'mobile_thumbnail_width', 'mobile_thumbnail_height',
                'inspection_image', 'inspection_width', 'inspection_height',
            )
        }),
        ('Statistics', {
            'fields': (
                'horsepower', 'torque', 'top_speed', 'transmission_type', 'gears', 'location', 'tight_fit',
                'blurb', 'specs', 'origin_country',
            )
        }),
        ('Price fields', {
            'fields': (
                'price_per_day', 'discount_2_day', 'discount_3_day', 'discount_7_day', 'security_deposit', 'miles_included',
            )
        })
    )


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(VehicleMarketing, VehicleMarketingAdmin)
