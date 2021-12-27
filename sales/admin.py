from prettyjson import PrettyJSONWidget

from django.contrib import admin
from django.db.models import JSONField

from sales.models import Reservation, Rental, Promotion, Coupon, TaxRate


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'customer',)


class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'customer',)


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
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(TaxRate, TaxRateAdmin)
