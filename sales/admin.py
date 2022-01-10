from prettyjson import PrettyJSONWidget

from django.contrib import admin
from django.db.models import JSONField

from sales.models import Reservation, Rental, Promotion, Coupon, TaxRate, GuidedDrive


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'customer',)
    autocomplete_fields = ('customer',)


class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'customer',)
    autocomplete_fields = ('customer',)


class GuidedDriveAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_type', 'customer', 'vehicle_choice_1', 'vehicle_choice_2', 'vehicle_choice_3', 'requested_date', 'confirmation_code',)
    autocomplete_fields = ('customer',)
    list_filter = ('event_type',)


class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'percent',)


class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'amount', 'percent',)


class TaxRateAdmin(admin.ModelAdmin):
    list_display = ('postal_code', 'total_rate', 'date_updated',)
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Rental, RentalAdmin)
admin.site.register(GuidedDrive, GuidedDriveAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(TaxRate, TaxRateAdmin)
