from prettyjson import PrettyJSONWidget

from django.contrib import admin
from django.db.models import JSONField

from sales.models import (
    Reservation, Rental, Promotion, Coupon, TaxRate, JoyRide, PerformanceExperience, GiftCertificate, AdHocPayment, Card
)


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'customer',)
    autocomplete_fields = ('customer',)


class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'customer',)
    autocomplete_fields = ('customer',)


class JoyRideAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'vehicle_choice_1', 'vehicle_choice_2', 'vehicle_choice_3', 'requested_date', 'confirmation_code',)
    autocomplete_fields = ('customer',)


class PerformanceExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'vehicle_choice_1', 'vehicle_choice_2', 'vehicle_choice_3', 'requested_date', 'confirmation_code',)
    autocomplete_fields = ('customer',)


class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'percent',)


class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'amount', 'percent',)


class TaxRateAdmin(admin.ModelAdmin):
    list_display = ('postal_code', 'total_rate', 'date_updated',)
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }


class GiftCertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'tag', 'cc_name', 'beneficiary_name', 'amount',)


class AdHocPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'amount',)


class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'last_4', 'stripe_card',)
    autocomplete_fields = ('customer',)


admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Rental, RentalAdmin)
admin.site.register(JoyRide, JoyRideAdmin)
admin.site.register(PerformanceExperience, PerformanceExperienceAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(TaxRate, TaxRateAdmin)
admin.site.register(GiftCertificate, GiftCertificateAdmin)
admin.site.register(AdHocPayment, AdHocPaymentAdmin)
admin.site.register(Card, CardAdmin)
